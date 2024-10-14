import pytest
from httpx import AsyncClient
from snoutsaver import models

# Test Create Record with Authorization
@pytest.mark.asyncio
async def test_create_record_with_auth(
    client: AsyncClient, 
    user1: models.DBUser,
    token_user1: models.Token, 
    category1: models.DBCategory):

    headers = {"Authorization": f"{token_user1.token_type} {token_user1.access_token}"}
    record_data = {
        "user_id": user1.id,
        "description": "Test record with auth",
        "amount": 100.0,
        "currency": "THB",
        "type": "Expense",
        "category_id": category1.id,
        "category_name": category1.name,
        "record_date": "2022-01-01"
    }
    response = await client.post("/records", json=record_data, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["description"] == "Test record with auth"
    assert data["amount"] == 100.0
    assert data["currency"] == "THB"

# Test Create Record without Authorization
@pytest.mark.asyncio
async def test_create_record_without_auth(
    client: AsyncClient, 
    category1: models.DBCategory):
    record_data = {
        "user_id": 1,  # This should be an invalid user ID or omit it as needed
        "description": "Test record without auth",
        "amount": 100.0,
        "currency": "THB",
        "type": "Expense",
        "category_id": category1.id,
        "category_name": category1.name
    }
    response = await client.post("/records", json=record_data)
    assert response.status_code == 401  # Unauthorized

# Test Read All Records with Authorization
@pytest.mark.asyncio
async def test_read_all_records_with_auth(
    client: AsyncClient, 
    user1: models.DBUser,
    token_user1: models.Token, 
    category1: models.DBCategory):

    headers = {"Authorization": f"{token_user1.token_type} {token_user1.access_token}"}
    record_data = {
        "user_id": user1.id,
        "description": "Another record with auth",
        "amount": 200.0,
        "currency": "THB",
        "type": "Expense",
        "category_id": category1.id,
        "category_name": category1.name
    }
    await client.post("/records", json=record_data, headers=headers)
    response = await client.get("/records", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data["records"]) > 0

# Test Read All Records without Authorization
@pytest.mark.asyncio
async def test_read_all_records_without_auth(client: AsyncClient):
    response = await client.get("/records")
    assert response.status_code == 401  # Unauthorized

# Test Read Record with Authorization
@pytest.mark.asyncio
async def test_read_record_with_auth(
    client: AsyncClient,
    user1: models.DBUser, 
    token_user1: models.Token, 
    category1: models.DBCategory):

    headers = {"Authorization": f"{token_user1.token_type} {token_user1.access_token}"}
    record_data = {
        "user_id": user1.id,
        "description": "Record with auth",
        "amount": 150.0,
        "currency": "THB",
        "type": "Expense",
        "category_id": category1.id,
        "category_name": category1.name,
        "record_date": "2022-01-01"
    }
    response = await client.post("/records", json=record_data, headers=headers)
    record_id = response.json()["id"]
    response = await client.get(f"/records/{record_id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["description"] == "Record with auth"

# Test Read Record without Authorization
@pytest.mark.asyncio
async def test_read_record_without_auth(
    client: AsyncClient):
    response = await client.get(f"/records/1")  # Using a random ID
    assert response.status_code == 401  # Unauthorized

# Test Update Record with Authorization
@pytest.mark.asyncio
async def test_update_record_with_auth(
    client: AsyncClient,
    user1: models.DBUser, 
    token_user1: models.Token, 
    category1: models.DBCategory):

    headers = {"Authorization": f"{token_user1.token_type} {token_user1.access_token}"}
    record_data = {
        "user_id": user1.id,
        "description": "Record with auth",
        "amount": 300.0,
        "currency": "THB",
        "type": "Expense",
        "category_id": category1.id,
        "category_name": category1.name,
        "record_date": "2022-01-01"
    }
    response = await client.post("/records", json=record_data, headers=headers)
    record_id = response.json()["id"]
    update_data = {
        "user_id": user1.id,
        "description": "Record update with auth",
        "amount": 350.0,
        "currency": "USD",
        "type": "Expense",
        "category_id": category1.id,
        "category_name": category1.name,
        "record_date": "2022-01-01"
    }
    response = await client.put(f"/records/{record_id}", json=update_data, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["amount"] == 350.0
    assert data["currency"] == "USD"

# Test Update Record without Authorization
@pytest.mark.asyncio
async def test_update_record_without_auth(
    client: AsyncClient, 
    category1: models.DBCategory):
    update_data = {
        "amount": 350.0,
        "currency": "USD",
        "category_id": category1.id
    }
    response = await client.put(f"/records/1", json=update_data)  # Using a random ID
    assert response.status_code == 401  # Unauthorized

# Test Delete Record with Authorization
@pytest.mark.asyncio
async def test_delete_record_with_auth(
    client: AsyncClient, 
    user1: models.DBUser,
    token_user1: models.Token, 
    category1: models.DBCategory):

    headers = {"Authorization": f"{token_user1.token_type} {token_user1.access_token}"}
    record_data = {
        "user_id": user1.id,
        "description": "Record delete with auth",
        "amount": 400.0,
        "currency": "THB",
        "type": "Expense",
        "category_id": category1.id,
        "category_name": category1.name,
        "record_date": "2022-01-01"
    }
    response = await client.post("/records", json=record_data, headers=headers)
    record_id = response.json()["id"]
    response = await client.delete(f"/records/{record_id}", headers=headers)
    assert response.status_code == 200
    # Verify deletion
    response = await client.get(f"/records/{record_id}", headers=headers)
    assert response.status_code == 404

# Test Delete Record without Authorization
@pytest.mark.asyncio
async def test_delete_record_without_auth(client: AsyncClient):
    response = await client.delete(f"/records/1")  # Using a random ID
    assert response.status_code == 401  # Unauthorized