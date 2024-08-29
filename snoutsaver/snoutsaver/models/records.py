import datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict
from typing import Optional

from sqlmodel import Field, SQLModel


class Record(BaseModel):
    user_id: int
    amount: float
    currency: str

    type: str


class Records(BaseModel):
    id: int


class CreateRecord(Record):
    pass


class DBRecord(Record, SQLModel):
    __tablename__ = "records"
    id: int = Field(default=None, primary_key=True)

    record_date: datetime.datetime = Field(default=datetime.datetime.now)

class RecordList(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    records: list[Record]
