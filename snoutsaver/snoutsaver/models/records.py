import datetime
import pydantic
import pytz

from pydantic import BaseModel, ConfigDict
from typing import Optional

from sqlmodel import Field, SQLModel, Relationship

from . import users
from . import categories


class BaseRecord(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: int
    amount: float
    currency: str
    type: str
    category_id: int
    category_name: str

class Records(BaseModel):
    id: int


class CreateRecord(BaseRecord):
    record_date: datetime.datetime | None = pydantic.Field(
        json_schema_extra=dict(example="2023-01-01T00:00:00.000000"), default=None
    )

class UpdatedRecord(BaseRecord):
    type: Optional[str] = None
    amount: float
    currency: str

class DBRecord(BaseRecord, SQLModel, table=True):
    __tablename__ = "records"
    id: int = Field(default=None, primary_key=True)

    user_id: int = Field(default=None, foreign_key="users.id")
    user: users.DBUser = Relationship()
    # amount: float
    # currency: str
    # type: str
    category: categories.DBCategory = Relationship()
    category_id: int = Field(default=None, foreign_key="categories.id")
    category_name: str

    record_date: datetime.datetime = Field(default_factory=datetime.datetime.now)

class RecordList(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    records: list[Records]
