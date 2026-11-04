import re
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.party import Party
from app.schemas.parties import PartyCreate, PartyUpdate
from app.gst.rules import get_gstin_state_code
from app.gst.rules import is_valid_state_code


def _duplicate_party(db: Session, business_id: int, data: PartyCreate, exclude_id: int | None = None) -> Party | None:
    query = db.query(Party).filter(Party.business_id == business_id)
    if exclude_id is not None:
        query = query.filter(Party.id != exclude_id)
    candidates = query.all()
    name_key = " ".join(data.name.casefold().split())
    email_key = (data.email or "").strip().casefold()
    phone_key = re.sub(r"\D", "", data.phone or "")
    for existing in candidates:
        if data.gstin and existing.gstin and data.gstin == existing.gstin:
            return existing
        if " ".join(existing.name.casefold().split()) != name_key:
            continue
        if data.gstin and existing.gstin and data.gstin != existing.gstin:
            continue
        same_email = email_key and existing.email and email_key == existing.email.strip().casefold()
        same_phone = phone_key and existing.phone and phone_key == re.sub(r"\D", "", existing.phone)
        existing_has_contacts = bool(existing.email or existing.phone)
        if same_email or same_phone or not (email_key or phone_key) or not existing_has_contacts:
            return existing
    return None


def create_party(db: Session, business_id: int, data: PartyCreate) -> Party:
    normalized = PartyCreate.model_validate(data.model_dump())
    if normalized.email and not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", normalized.email.strip()):
        raise HTTPException(status_code=422, detail="Enter a valid email address.")
    normalized.email = normalized.email.strip().lower() if normalized.email else None
    normalized.phone = normalized.phone.strip() if normalized.phone else None
    if normalized.state_code and not is_valid_state_code(normalized.state_code):
        raise HTTPException(status_code=422, detail="Choose a valid Indian state or territory.")
    if normalized.gstin:
        gstin_state = get_gstin_state_code(normalized.gstin)
        if not normalized.state_code:
            normalized.state_code = gstin_state
        elif gstin_state and normalized.state_code != gstin_state:
            raise HTTPException(status_code=422, detail="The selected state does not match the GSTIN state code.")
    duplicate = _duplicate_party(db, business_id, normalized)
    if duplicate:
        raise HTTPException(status_code=409, detail=f"A matching party already exists: {duplicate.name} (#{duplicate.id}). Open it to review or edit.")
    party = Party(business_id=business_id, auto_created=False, **normalized.model_dump())
    db.add(party)
    db.commit()
    db.refresh(party)
    return party


def get_or_create_party_from_invoice(
    db: Session,
    business_id: int,
    name: str | None,
    gstin: str | None,
    state_code: str | None,
    direction: str = "purchase"
) -> Party:
    """
    Suppliers and customers are created automatically from extracted invoices:
    Matched by GSTIN, then by normalised name.
    """
    clean_name = (name or "Unknown Party").strip()
    clean_gstin = gstin.strip().upper() if gstin else None

    # Determine party type: customer if sales, otherwise vendor
    party_type = "customer" if direction == "sales" else "vendor"

    party = None
    # 1. Match by GSTIN within tenant
    if clean_gstin:
        party = db.query(Party).filter(
            Party.business_id == business_id,
            Party.gstin == clean_gstin,
            Party.is_archived.is_(False)
        ).first()

    # 2. Match by normalized name
    if not party and clean_name:
        party = db.query(Party).filter(
            Party.business_id == business_id,
            Party.name.ilike(clean_name),
            Party.is_archived.is_(False),
            ((Party.gstin.is_(None)) | (Party.gstin == clean_gstin)) if clean_gstin else True
        ).first()

    # Reuse an archived match rather than creating a duplicate account.
    if not party and clean_gstin:
        party = db.query(Party).filter(Party.business_id == business_id, Party.gstin == clean_gstin).first()
    if not party and clean_name:
        party = db.query(Party).filter(
            Party.business_id == business_id,
            Party.name.ilike(clean_name),
            ((Party.gstin.is_(None)) | (Party.gstin == clean_gstin)) if clean_gstin else True
        ).first()

    if party:
        party.is_archived = False
        if clean_name != "Unknown Party" and party.name == "Unknown Party":
            party.name = clean_name
        if clean_gstin and not party.gstin:
            party.gstin = clean_gstin
            party.gst_registration_type = "regular"
        if state_code and not party.state_code:
            party.state_code = state_code
        # If party was vendor and now has sales invoice, update to 'both'
        if party.type != party_type and party.type != "both":
            party.type = "both"
        db.commit()
        db.refresh(party)
        return party

    # 3. Create new party
    derived_state = state_code or get_gstin_state_code(clean_gstin)
    new_party = Party(
        business_id=business_id,
        name=clean_name,
        gstin=clean_gstin,
        state_code=derived_state,
        type=party_type,
        auto_created=True,
        gst_registration_type="regular" if clean_gstin else "unregistered",
        payment_terms_days=30,
        credit_limit_paise=0
    )
    db.add(new_party)
    db.commit()
    db.refresh(new_party)
    return new_party


def list_parties(
    db: Session, business_id: int, party_type: str | None = None, include_archived: bool = False
) -> list[Party]:
    query = db.query(Party).filter(Party.business_id == business_id)
    if not include_archived:
        query = query.filter(Party.is_archived.is_(False))
    if party_type in {"vendor", "supplier"}:
        query = query.filter(Party.type.in_(["vendor", "both"]))
    elif party_type == "customer":
        query = query.filter(Party.type.in_(["customer", "both"]))
    elif party_type in {"both", "all"}:
        pass
    return query.order_by(Party.name.asc()).all()


def get_party(db: Session, business_id: int, party_id: int) -> Party:
    party = db.query(Party).filter(
        Party.id == party_id,
        Party.business_id == business_id
    ).first()
    if not party:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Party not found."
        )
    return party


def update_party(
    db: Session, business_id: int, party_id: int, data: PartyUpdate
) -> Party:
    party = get_party(db, business_id, party_id)
    update_dict = data.model_dump(exclude_unset=True)
    merged = {key: getattr(party, key) for key in PartyCreate.model_fields}
    merged.update(update_dict)
    validated = PartyCreate.model_validate(merged)
    if validated.email and not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", validated.email.strip()):
        raise HTTPException(status_code=422, detail="Enter a valid email address.")
    validated.email = validated.email.strip().lower() if validated.email else None
    validated.phone = validated.phone.strip() if validated.phone else None
    if validated.state_code and not is_valid_state_code(validated.state_code):
        raise HTTPException(status_code=422, detail="Choose a valid Indian state or territory.")
    if validated.gstin:
        gstin_state = get_gstin_state_code(validated.gstin)
        if not validated.state_code:
            validated.state_code = gstin_state
        elif gstin_state and validated.state_code != gstin_state:
            raise HTTPException(status_code=422, detail="The selected state does not match the GSTIN state code.")
    duplicate = _duplicate_party(db, business_id, validated, exclude_id=party_id)
    if duplicate:
        raise HTTPException(status_code=409, detail=f"A matching party already exists: {duplicate.name} (#{duplicate.id}).")
    update_dict = validated.model_dump()

    for k, v in update_dict.items():
        setattr(party, k, v)

    db.commit()
    db.refresh(party)
    return party


def set_party_archived(db: Session, business_id: int, party_id: int, archived: bool) -> Party:
    party = get_party(db, business_id, party_id)
    if archived:
        from app.models.recurring import RecurringTemplate
        scheduled = db.query(RecurringTemplate).filter(
            RecurringTemplate.business_id == business_id,
            RecurringTemplate.party_id == party_id,
            RecurringTemplate.active.is_(True),
        ).first()
        if scheduled:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Pause or finish this party's active recurring invoice schedule before archiving it.",
            )
    party.is_archived = archived
    db.commit()
    db.refresh(party)
    return party
