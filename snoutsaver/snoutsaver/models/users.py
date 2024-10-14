import pydantic
import datetime
import bcrypt

from pydantic import BaseModel, ConfigDict

from sqlmodel import Field, SQLModel

from typing import Optional

class BaseUser(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    email: str = pydantic.Field(json_schema_extra={"example":"user@email.local", "unique": True})
    username: str = pydantic.Field(json_schema_extra={"example":"user", "unique": True})

class User(BaseUser):
    id: int
    last_login_date: datetime.datetime | None = pydantic.Field(
        json_schema_extra=dict(example="2023-01-01T00:00:00.000000"), default=None
    )
    register_date: datetime.datetime | None = pydantic.Field(
        json_schema_extra=dict(example="2023-01-01T00:00:00.000000"), default=None
    )

class RegisterUser(BaseUser):
    password: str = pydantic.Field(json_schema_extra=dict(example="password", minLength=8))
    confirm_password: str = pydantic.Field(json_schema_extra=dict(example="confirm_password"))
    provider: str = pydantic.Field(json_schema_extra=dict(example="default"))
    profile_picture: str | None = Field(default=None)
class ChangePassword(BaseModel):
    current_password: str
    new_password: str

class GetUser(BaseUser):
    id: int
    first_name: str | None = Field(default=None)
    last_name: str | None = Field(default=None)
    profile_picture: str | None = Field(default=None)
    provider: str | None = Field(default=None)

class UpdateUser(BaseModel):
    email: str = pydantic.Field(json_schema_extra={"example":"user@email.local", "unique": True})
    username: str = pydantic.Field(json_schema_extra={"example":"user", "unique": True})
    first_name: str = pydantic.Field(json_schema_extra=dict(example="Firstname"))
    last_name: str = pydantic.Field(json_schema_extra=dict(example="Lastname"))
    profile_picture: str = pydantic.Field(json_schema_extra=dict(example="www.example.com/profile_picture.png"))

class UpdateProfilePicture(BaseModel):
    profile_picture: str = pydantic.Field(json_schema_extra=dict(example="www.example.com/profile_picture.png"))

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    expires_at: datetime.datetime
    scope: str
    issued_at: datetime.datetime

class DBUser(BaseUser, SQLModel, table=True):
    __tablename__ = "users"
    id: int | None = Field(default=None, primary_key=True)

    first_name: str | None = Field(default=None)
    last_name: str | None = Field(default=None)
    password: str | None = Field(default=None)
    profile_picture: str | None = Field(default=None)
    provider: str | None = Field(default=None)

    register_date: datetime.datetime = Field(default_factory=datetime.datetime.now)
    updated_date: datetime.datetime = Field(default_factory=datetime.datetime.now)
    last_login_date: datetime.datetime | None = Field(default=None)

    async def get_encrypted_password(self, plain_password):
        return bcrypt.hashpw(
            plain_password.encode("utf-8"), salt=bcrypt.gensalt()
        ).decode("utf-8")

    async def set_password(self, plain_password):
        self.password = await self.get_encrypted_password(plain_password)

    async def verify_password(self, plain_password):
        return bcrypt.checkpw(
            plain_password.encode("utf-8"), self.password.encode("utf-8")
        )
    
class UserList(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    items: list[GetUser]
    page: int
    page_size: int
    size_per_page: int

