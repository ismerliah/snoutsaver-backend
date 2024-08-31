import pytest
from httpx import AsyncClient
from snoutsaver import models

#test
@pytest.mark.asyncio
async def test_create_record(
    client: AsyncClient, 
    test_user, 
    test_categories
    ):
    record_data = {
        "user_id": test_user.id,
        "description": "Test record",
        "amount": 100.0,
        "currency": "THB",
        "type": "Expense",
        "category_id": test_categories.id,
        "category_name": test_categories.name
    }
    response = await client.post("/records", json=record_data)
    assert response.status_code == 201
    data = response.json()
    assert data["description"] == "Test record"
    assert data["amount"] == 100.0
    assert data["currency"] == "THB"

#test read all
@pytest.mark.asyncio
async def test_read_all_records(
    client: AsyncClient, 
    test_user, 
    test_categories
    ):
    record_data = {
        "user_id": test_user.id,
        "description": "Another record",
        "amount": 200.0,
        "currency": "THB",
        "type": "Expense",
        "category_id": test_categories.id,
        "category_name": test_categories.name
    }
    await client.post("/records", json=record_data)
    response = await client.get("/records")
    assert response.status_code == 200
    data = response.json()
    assert len(data["records"]) > 0

#test read
@pytest.mark.asyncio
async def test_read_record(
    client: AsyncClient, 
    test_user, 
    test_categories
    ):
    record_data = {
        "user_id": test_user.id,
        "description": "Record to read",
        "amount": 150.0,
        "currency": "THB",
        "type": "Expense",
        "category_id": test_categories.id,
        "category_name": test_categories.name
    }
    response = await client.post("/records", json=record_data)
    record_id = response.json()["id"]
    response = await client.get(f"/records/{record_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["description"] == "Record to read"

#test update
@pytest.mark.asyncio
async def test_update_record(
    client: AsyncClient, 
    test_user, 
    test_categories
    ):
    record_data = {
        "user_id": test_user.id,
        "description": "Record to update",
        "amount": 300.0,
        "currency": "THB",
        "type": "Expense",
        "category_id": test_categories.id,
        "category_name": test_categories.name
    }
    response = await client.post("/records", json=record_data)
    record_id = response.json()["id"]
    update_data = {
        "amount": 350.0,
        "currency": "USD",
        "category_id": test_categories.id
    }
    response = await client.put(f"/records/{record_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["amount"] == 350.0
    assert data["currency"] == "USD"

#test delete
@pytest.mark.asyncio
async def test_delete_record(
    client: AsyncClient, 
    test_user, 
    test_categories
    ):
    record_data = {
        "user_id": test_user.id,
        "description": "Record to delete",
        "amount": 400.0,
        "currency": "THB",
        "type": "Expense",
        "category_id": test_categories.id,
        "category_name": test_categories.name
    }
    response = await client.post("/records", json=record_data)
    record_id = response.json()["id"]
    response = await client.delete(f"/records/{record_id}")
    assert response.status_code == 204
    #verify deletion
    response = await client.get(f"/records/{record_id}")
    assert response.status_code == 404