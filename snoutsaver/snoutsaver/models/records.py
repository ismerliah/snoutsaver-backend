import datetime
from pydantic import BaseModel, ConfigDict
from typing import Optional

from sqlmodel import Field, SQLModel


class BaseRecord(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: int
    amount: float
    currency: str
    type: str

class Records(BaseModel):
    id: int


class CreateRecord(BaseRecord):
    pass

class UpdatedRecord(BaseRecord):
    type: Optional[str] = None
    amount: float
    currency: str

class DBRecord(BaseRecord, SQLModel, table=True):
    __tablename__ = "records"
    id: int = Field(default=None, primary_key=True)
    user_id = int
    amount: float
    currency: str
    type: str
    record_date: datetime.datetime = Field(default=datetime.datetime.now)

class RecordList(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    records: list[Records]
