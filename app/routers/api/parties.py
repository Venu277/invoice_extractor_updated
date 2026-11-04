from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import get_current_user, require_role
from app.models.user import User
from app.schemas.parties import PartyCreate, PartyResponse, PartyUpdate
from app.services.party_service import create_party, list_parties, get_party, update_party, set_party_archived

router = APIRouter(prefix="/parties", tags=["Parties (Vendors & Customers)"])


@router.get("", response_model=list[PartyResponse])
def get_parties(
    type: str | None = Query(None, description="vendor, customer, or all"),
    include_archived: bool = Query(False),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return list_parties(db, current_user.business_id, party_type=type, include_archived=include_archived)


@router.post("", response_model=PartyResponse, status_code=201)
def add_party(
    data: PartyCreate,
    current_user: User = Depends(require_role("owner", "accountant")),
    db: Session = Depends(get_db)
):
    return create_party(db, current_user.business_id, data)


@router.get("/{party_id}", response_model=PartyResponse)
def get_party_detail(
    party_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return get_party(db, current_user.business_id, party_id)


@router.put("/{party_id}", response_model=PartyResponse)
def edit_party(
    party_id: int,
    data: PartyUpdate,
    current_user: User = Depends(require_role("owner", "accountant")),
    db: Session = Depends(get_db)
):
    return update_party(db, current_user.business_id, party_id, data)


@router.post("/{party_id}/archive", response_model=PartyResponse)
def archive_party(
    party_id: int,
    current_user: User = Depends(require_role("owner", "accountant")),
    db: Session = Depends(get_db)
):
    return set_party_archived(db, current_user.business_id, party_id, True)


@router.post("/{party_id}/restore", response_model=PartyResponse)
def restore_party(
    party_id: int,
    current_user: User = Depends(require_role("owner", "accountant")),
    db: Session = Depends(get_db)
):
    return set_party_archived(db, current_user.business_id, party_id, False)
