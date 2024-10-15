import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport


from typing import Any, Dict, Optional
from pydantic_settings import SettingsConfigDict

from snoutsaver import models, config, main, security
import pytest
import pytest_asyncio

import pathlib
import datetime
import sys

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


SettingsTesting = config.Settings
SettingsTesting.model_config = SettingsConfigDict(
    env_file=".testing.env", validate_assignment=True, extra="allow"
)


@pytest.fixture(name="app", scope="session")
def app_fixture():
    settings = SettingsTesting()
    path = pathlib.Path("test-data")
    if not path.exists():
        path.mkdir()

    app = main.create_app(settings)

    asyncio.run(models.recreate_table())

    yield app


@pytest.fixture(name="client", scope="session")
def client_fixture(app: FastAPI) -> AsyncClient:

    # client = TestClient(app)
    # yield client
    # app.dependency_overrides.clear()
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost")


@pytest_asyncio.fixture(name="session", scope="session")
async def get_session() -> models.AsyncIterator[models.AsyncSession]:
    settings = SettingsTesting()
    models.init_db(settings)
    async_session = models.sessionmaker(
        models.engine, class_=models.AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session

# [User]------------------------------------------------------------

# user1
@pytest_asyncio.fixture(name="user1")
async def example_user1(session: models.AsyncSession) -> models.DBUser:
    password = "12345678"
    username = "user1"

    query = await session.exec(
        models.select(models.DBUser).where(models.DBUser.username == username).limit(1)
    )
    user = query.one_or_none()
    if user:
        return user
    
    user = models.DBUser(
        username=username,
        password=password,
        confirm_password=password,
        email="test1@test.com",
        first_name="Firstname",
        last_name="lastname",
        last_login_date=datetime.datetime.now(tz=datetime.timezone.utc),
    )

    await user.set_password(password)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user

@pytest_asyncio.fixture(name="token_user1")
async def oauth_token_user1(user1: models.DBUser) -> dict:
    settings = SettingsTesting()
    access_token_expires = datetime.timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    user = user1
    return models.Token(
        access_token=security.create_access_token(
            data={"sub": user.id},
            expires_delta=access_token_expires,
        ),
        refresh_token=security.create_refresh_token(
            data={"sub": user.id},
            expires_delta=access_token_expires,
        ),
        token_type="Bearer",
        scope="",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        expires_at=datetime.datetime.now() + access_token_expires,
        issued_at=user.last_login_date,
        user_id=user.id,
    )
# ----------------------------------------------------------------------

# [Category]------------------------------------------------------------

@pytest_asyncio.fixture(name="category1")
async def example_category1(session: models.AsyncSession) -> models.DBCategory:
    name = "Food"
    type = "Expense"
    icon = "fastfood_rounded"

    query = await session.exec(
        models.select(models.DBCategory).where(models.DBCategory.name == name).limit(1)
    )
    category = query.one_or_none()
    if category:
        return category
    
    category = models.DBCategory(
        name=name,
        type=type,
        icon=icon
    )

    session.add(category)
    await session.commit()
    await session.refresh(category)
    return category


@pytest_asyncio.fixture(name="category2")
async def example_category2(session: models.AsyncSession) -> models.DBCategory:
    name = "Travel"
    type = "Expense"
    icon = "flight_rounded"

    query = await session.exec(
        models.select(models.DBCategory).where(models.DBCategory.name == name).limit(1)
    )
    category = query.one_or_none()
    if category:
        return category
    
    category = models.DBCategory(
        name=name,
        type=type,
        icon=icon
    )

    session.add(category)
    await session.commit()
    await session.refresh(category)
    return category

# ----------------------------------------------------------------------

# [Record]------------------------------------------------------------
@pytest_asyncio.fixture(name="record")
async def example_record1(session: models.AsyncSession) -> models.DBRecord:
    user_id = 1
    description = "first record"
    amount = 100
    currency = "THB"
    type = "Expense"
    category_id = 1
    category_name = "Food"

    query = await session.exec(
        models.select(models.DBRecord).where(models.DBRecord.user_id == user_id).limit(1)
    )
    record = query.one_or_none()
    if record:
        return record
    
    record = models.DBRecord(
        user_id=user_id,
        description=description,
        amount=amount,
        currency=currency,
        category_id=category_id,
        category_name=category_name,
        type=type,
    )

    session.add(record)
    await session.commit()
    await session.refresh(record)
    return record

# ----------------------------------------------------------------------