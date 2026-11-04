from app.models.invoice import Invoice
from app.models.party import Party
from app.models.business import Business
from app.models.user import User
from app.services.security import create_access_token, hash_password


def _party_workspace(db_session):
    business = Business(name="Party Management Co", gstin="29ABCDE1234F1Z5", state_code="29", invoice_prefix="PTY-")
    db_session.add(business)
    db_session.flush()
    user = User(
        business_id=business.id,
        name="Party Owner",
        email="party-owner@example.com",
        password_hash=hash_password("Password123!"),
        role="owner",
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    token = create_access_token({"sub": str(user.id), "email": user.email, "role": user.role, "business_id": business.id})
    return {"Authorization": f"Bearer {token}"}, business.id


def test_manual_party_flows_into_invoice_and_can_be_archived_safely(client, db_session):
    headers, business_id = _party_workspace(db_session)
    response = client.post("/api/v1/parties", headers=headers, json={
        "name": "  Acme   Services ",
        "type": "customer",
        "gst_registration_type": "regular",
        "gstin": "29AAAAA1111A1Z1",
        "state_code": "29",
        "address": "10 Market Road",
        "shipping_address": "Warehouse 2",
        "phone": "+91 98765 43210",
        "email": "BILLING@ACME.EXAMPLE",
        "payment_terms_days": 21,
        "credit_limit_paise": 5000000,
        "notes": "Monthly account",
    })
    assert response.status_code == 201, response.text
    party = response.json()
    assert party["name"] == "Acme Services"
    assert party["email"] == "billing@acme.example"
    assert party["gstin"] == "29AAAAA1111A1Z1"
    assert party["shipping_address"] == "Warehouse 2"
    page = client.get("/invoices/new", headers=headers, cookies={"access_token": headers["Authorization"].removeprefix("Bearer ")})
    assert page.status_code == 200
    assert f'data-gstin="{party["gstin"]}"' in page.text
    assert "10 Market Road" in page.text

    duplicate = client.post("/api/v1/parties", headers=headers, json={
        "name": "Other Display Name", "type": "customer", "gst_registration_type": "regular",
        "gstin": "29AAAAA1111A1Z1", "state_code": "29",
    })
    assert duplicate.status_code == 409

    invoice = client.post("/api/v1/generator/invoices", headers=headers, json={
        "customer_id": party["id"],
        "invoice_date": "2026-04-01",
        "items": [{"description": "Monthly service", "quantity": 1, "rate_paise": 100000, "gst_rate": 18}],
    })
    assert invoice.status_code == 201, invoice.text
    invoice_data = invoice.json()
    assert invoice_data["buyer_gstin"] == "29AAAAA1111A1Z1"
    assert invoice_data["due_date"] == "2026-04-22"
    pdf = client.get(f"/api/v1/generator/invoices/{invoice_data['id']}/pdf", headers=headers)
    assert pdf.status_code == 200 and pdf.content.startswith(b"%PDF")

    archived = client.post(f"/api/v1/parties/{party['id']}/archive", headers=headers)
    assert archived.status_code == 200 and archived.json()["is_archived"] is True
    assert client.get("/api/v1/parties", headers=headers).json() == []
    assert len(client.get("/api/v1/parties?include_archived=true", headers=headers).json()) == 1
    stored_invoice = db_session.query(Invoice).filter(Invoice.id == invoice_data["id"], Invoice.business_id == business_id).one()
    assert stored_invoice.party_id == party["id"]
    rejected = client.post("/api/v1/generator/invoices", headers=headers, json={
        "customer_id": party["id"], "items": [{"description": "Item", "quantity": 1, "rate_paise": 100, "gst_rate": 0}]
    })
    assert rejected.status_code == 404

    restored = client.post(f"/api/v1/parties/{party['id']}/restore", headers=headers)
    assert restored.status_code == 200 and restored.json()["is_archived"] is False


def test_unregistered_customer_and_duplicate_name_handling(client, db_session):
    headers, _ = _party_workspace(db_session)
    created = client.post("/api/v1/parties", headers=headers, json={
        "name": "Walk-in Customer", "type": "customer", "gst_registration_type": "unregistered",
        "address": "Main Street",
    })
    assert created.status_code == 201, created.text
    assert created.json()["gstin"] is None

    missing_gstin = client.post("/api/v1/parties", headers=headers, json={
        "name": "Registered Customer", "type": "customer", "gst_registration_type": "regular",
    })
    assert missing_gstin.status_code == 422

    duplicate_name = client.post("/api/v1/parties", headers=headers, json={
        "name": "Walk-in Customer", "type": "customer", "gst_registration_type": "unregistered",
    })
    assert duplicate_name.status_code == 409


def test_party_page_contains_manage_and_filter_controls(client, db_session):
    headers, _ = _party_workspace(db_session)
    response = client.get("/parties", headers=headers, cookies={"access_token": headers["Authorization"].removeprefix("Bearer ")})
    assert response.status_code == 200
    assert "Add party" in response.text
    assert "Search name, GSTIN, phone, or email" in response.text
    assert "Customers" in response.text and "Suppliers" in response.text and "Both" in response.text
