from httpx import AsyncClient
import pytest

from snoutsaver import models

# Not Authenticated Create Category
@pytest.mark.asyncio
async def test_no_authenticated_create_category(
    client: AsyncClient
):
    payload = {
        "name": "Travel",
        "type": "Expense"
    }
    response = await client.post("/categories", json=payload)

    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}

# Authenticated Create Category
@pytest.mark.asyncio
async def test_create_category(
    client: AsyncClient, token_user1: models.Token
):
    headers = {"Authorization": f"{token_user1.token_type} {token_user1.access_token}"}
    payload = {
        "name": "Travel",
        "type": "Expense",
        "icon": "flight_rounded"
    }
    response = await client.post("/categories", json=payload, headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == payload["name"]
    assert data["type"] == payload["type"]
    assert data["icon"] == payload["icon"]

# Create Existing Category
@pytest.mark.asyncio
async def test_create_existing_category(
    client: AsyncClient, token_user1: models.Token, category1: models.DBCategory
):
    headers = {"Authorization": f"{token_user1.token_type} {token_user1.access_token}"}
    payload = {
        "name": category1.name,
        "type": category1.type,
        "icon": category1.icon
    }
    response = await client.post("/categories", json=payload, headers=headers)

    assert response.status_code == 400
    assert response.json() == {"detail": "Category already exists"}

# Not Authenticated Read All Categories
@pytest.mark.asyncio
async def test_no_authenticated_read_all_categories(
    client: AsyncClient
):
    response = await client.get("/categories")

    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}

# Authenticated Read All Categories
@pytest.mark.asyncio
async def test_read_all_categories(
    client: AsyncClient, token_user1: models.Token
):
    headers = {"Authorization": f"{token_user1.token_type} {token_user1.access_token}"}
    response = await client.get("/categories", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert isinstance(data["items"], list)

# Not Authenticated Read Category by ID
@pytest.mark.asyncio
async def test_no_authenticated_read_category(
    client: AsyncClient, category1: models.DBCategory
):
    # Valid category id
    valid_response = await client.get(f"/categories/{category1.id}")
    assert valid_response.status_code == 401
    assert valid_response.json() == {"detail": "Not authenticated"}

    # Invalid category id
    invalid_category_id = 999
    invalid_response = await client.get(f"/categories/{invalid_category_id}")
    assert invalid_response.status_code == 401
    assert invalid_response.json() == {"detail": "Not authenticated"}

# Authenticated Read Category by ID
@pytest.mark.asyncio
async def test_read_category(
    client: AsyncClient, token_user1: models.Token, category1: models.DBCategory
):
    headers = {"Authorization": f"{token_user1.token_type} {token_user1.access_token}"}

    # Valid category id
    valid_response = await client.get(f"/categories/{category1.id}", headers=headers)

    assert valid_response.status_code == 200
    data = valid_response.json()
    assert data["id"] == category1.id
    assert data["name"] == category1.name

    # Invalid category id
    invalid_category_id = 999
    invalid_response = await client.get(f"/categories/{invalid_category_id}", headers=headers)
    assert invalid_response.status_code == 404
    assert invalid_response.json() == {"detail": "Category not found"}

# Not Authenticated Update Category
@pytest.mark.asyncio
async def test_no_authenticated_update_category(
    client: AsyncClient, category1: models.DBCategory, category2: models.DBCategory
):
    new_name_payload = {
        "name": "Healthy Food",
        "type": category1.type
    }
    duplicate_name_payload = {
        "name": category2.name,
        "type": category1.type
    }

    # Valid category id & New name
    valid_response_new_name = await client.put(f"/categories/{category1.id}", json=new_name_payload)
    assert valid_response_new_name.status_code == 401
    assert valid_response_new_name.json() == {"detail": "Not authenticated"}

    # Valid category id & Duplicate name
    valid_response_duplicate_name = await client.put(f"/categories/{category1.id}", json=duplicate_name_payload)
    assert valid_response_duplicate_name.status_code == 401
    assert valid_response_duplicate_name.json() == {"detail": "Not authenticated"}

    # Invalid category id
    invalid_category_id = 999
    invalid_response = await client.put(f"/categories/{invalid_category_id}", json=new_name_payload)
    assert invalid_response.status_code == 401
    assert invalid_response.json() == {"detail": "Not authenticated"}

# Authenticated Update Category
@pytest.mark.asyncio
async def test_update_category(
    client: AsyncClient, token_user1: models.Token, category1: models.DBCategory, category2: models.DBCategory
):
    headers = {"Authorization": f"{token_user1.token_type} {token_user1.access_token}"}
    
    new_name_payload = {
        "name": "Healthy Food",
        "type": category1.type,
        "icon": category1.icon
    }
    duplicate_name_payload = {
        "name": category2.name,
        "type": category1.type,
        "icon": category1.icon
    }

    # Valid category id & New name
    valid_response_new_name = await client.put(f"/categories/{category1.id}", json=new_name_payload, headers=headers)
    print("Valid response (new name):", valid_response_new_name.json())
    assert valid_response_new_name.status_code == 200
    data = valid_response_new_name.json()
    assert data["name"] == new_name_payload["name"]
    assert data["type"] == new_name_payload["type"]
    assert data["icon"] == new_name_payload["icon"]

    # Valid category id & Duplicate name
    valid_response_duplicate_name = await client.put(f"/categories/{category1.id}", json=duplicate_name_payload, headers=headers)
    print("Valid response (duplicate name):", valid_response_duplicate_name.json())
    assert valid_response_duplicate_name.status_code == 400
    assert valid_response_duplicate_name.json() == {"detail": "Category name already exists"}

    # Invalid category id
    invalid_category_id = 999
    invalid_response = await client.put(f"/categories/{invalid_category_id}", json=new_name_payload, headers=headers)
    print("Invalid response:", invalid_response.json())
    assert invalid_response.status_code == 404
    assert invalid_response.json() == {"detail": "Category not found"}

# Not Authenticated Delete Category
@pytest.mark.asyncio
async def test_no_authenticated_delete_category(
    client: AsyncClient, category1: models.DBCategory
):
    # Valid category id
    valid_response = await client.delete(f"/categories/{category1.id}")
    assert valid_response.status_code == 401
    assert valid_response.json() == {"detail": "Not authenticated"}

    # Invalid category id
    invalid_category_id = 999
    invalid_response = await client.delete(f"/categories/{invalid_category_id}")
    assert invalid_response.status_code == 401
    assert invalid_response.json() == {"detail": "Not authenticated"}

# Authenticated Delete Category
@pytest.mark.asyncio
async def test_delete_category(
    client: AsyncClient, token_user1: models.Token, category1: models.DBCategory
):
    headers = {"Authorization": f"{token_user1.token_type} {token_user1.access_token}"}

    # Valid category id
    valid_response = await client.delete(f"/categories/{category1.id}", headers=headers)
    data = valid_response.json()
    assert valid_response.status_code == 200
    assert data["message"] == "Delete category success"

    # Invalid category id
    invalid_category_id = 999
    invalid_response = await client.delete(f"/categories/{invalid_category_id}", headers=headers)
    assert invalid_response.status_code == 404
    assert invalid_response.json() == {"detail": "Category not found"}