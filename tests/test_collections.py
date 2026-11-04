import pytest
from starlette.testclient import TestClient
from app.models.collection import InvoiceCollection
from app.models.invoice import Invoice
from app.models.user import User


def test_invoice_collections_crud_and_case_insensitive_uniqueness(client: TestClient):
    # 1. Sign up and authenticate
    signup_payload = {
        "business_name": "Axion Collection Test Corp",
        "owner_name": "Collector Tester",
        "email": "collector@test.com",
        "password": "Password123!",
        "gstin": "29AABCA9999A1Z1"
    }
    sign_res = client.post("/api/v1/auth/signup", json=signup_payload)
    assert sign_res.status_code == 201

    login_res = client.post("/api/v1/auth/login", json={
        "email": "collector@test.com",
        "password": "Password123!"
    })
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Create first collection
    create_payload = {
        "name": "October 2026 Marketing Bills",
        "month": 10,
        "year": 2026,
        "invoice_ids": []
    }
    res = client.post("/api/v1/collections", json=create_payload, headers=headers)
    assert res.status_code == 201
    data = res.json()
    assert data["name"] == "October 2026 Marketing Bills"
    assert data["month"] == 10
    assert data["year"] == 2026
    col_id = data["id"]

    # 3. Test case-insensitive duplicate rejection
    dup_payload = {
        "name": "october 2026 marketing bills",  # lower case duplicate!
        "month": 10,
        "year": 2026,
        "invoice_ids": []
    }
    dup_res = client.post("/api/v1/collections", json=dup_payload, headers=headers)
    assert dup_res.status_code == 400
    assert "already exists" in dup_res.text.lower()

    # 4. Another case variation check (uppercase)
    dup_upper = {
        "name": "OCTOBER 2026 MARKETING BILLS",
        "month": 11,
        "year": 2026,
        "invoice_ids": []
    }
    dup_upper_res = client.post("/api/v1/collections", json=dup_upper, headers=headers)
    assert dup_upper_res.status_code == 400

    # 5. List collections
    list_res = client.get("/api/v1/collections", headers=headers)
    assert list_res.status_code == 200
    cols = list_res.json()
    assert len(cols) == 1
    assert cols[0]["name"] == "October 2026 Marketing Bills"

    # 6. Get collection by id
    get_res = client.get(f"/api/v1/collections/{col_id}", headers=headers)
    assert get_res.status_code == 200
    assert get_res.json()["id"] == col_id


def test_delete_selected_collections_deletes_unshared_invoices_only(client: TestClient, db_session):
    signup_payload = {
        "business_name": "Axion Collection Delete Test Corp",
        "owner_name": "Collection Delete Tester",
        "email": "collection-delete@test.com",
        "password": "Password123!",
        "gstin": "29AABCA9999A1Z1"
    }
    assert client.post("/api/v1/auth/signup", json=signup_payload).status_code == 201
    login_res = client.post("/api/v1/auth/login", json={
        "email": signup_payload["email"],
        "password": signup_payload["password"]
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    user = db_session.query(User).filter_by(email=signup_payload["email"]).one()

    unique_invoice = Invoice(
        business_id=user.business_id,
        invoice_no="DELETE-UNIQUE-001",
        direction="purchase",
        in_workspace=False
    )
    shared_invoice = Invoice(
        business_id=user.business_id,
        invoice_no="DELETE-SHARED-001",
        direction="purchase",
        in_workspace=False
    )
    db_session.add_all([unique_invoice, shared_invoice])
    db_session.flush()

    selected_collection = InvoiceCollection(
        business_id=user.business_id,
        name="Selected collection",
        name_normalized="selected collection",
        month=10,
        year=2026,
        invoice_ids=[unique_invoice.id, shared_invoice.id]
    )
    remaining_collection = InvoiceCollection(
        business_id=user.business_id,
        name="Remaining collection",
        name_normalized="remaining collection",
        month=10,
        year=2026,
        invoice_ids=[shared_invoice.id]
    )
    db_session.add_all([selected_collection, remaining_collection])
    db_session.commit()
    selected_collection_id = selected_collection.id
    remaining_collection_id = remaining_collection.id

    page_response = client.get("/invoices?view=collections", headers=headers)
    assert page_response.status_code == 200
    assert 'class="collection-select"' in page_response.text
    assert 'id="deleteCollectionsModal"' in page_response.text

    response = client.post(
        "/api/v1/collections/delete-selected",
        json={"collection_ids": [selected_collection_id]},
        headers=headers
    )

    assert response.status_code == 200
    assert response.json() == {
        "deleted_collection_count": 1,
        "deleted_invoice_count": 1
    }
    assert db_session.get(InvoiceCollection, selected_collection_id) is None
    assert db_session.get(InvoiceCollection, remaining_collection_id) is not None
    assert db_session.get(Invoice, unique_invoice.id).deleted_at is not None
    assert db_session.get(Invoice, shared_invoice.id).deleted_at is None
