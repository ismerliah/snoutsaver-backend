import datetime
import pydantic

from pydantic import BaseModel, ConfigDict
from typing import Optional

from sqlmodel import Field, SQLModel, Relationship

# from snoutsaver.snoutsaver.models.pockets import DBPocket

from . import users
from . import categories
from . import pockets


class BaseRecord(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: int
    description: str = pydantic.Field(json_schema_extra=dict(example="Description"))

    amount: float
    currency: str = "THB"
    type: str = "Expense"

    category_id: int
    category_name: str

    pocket_id: Optional[int] = None

class Records(BaseRecord):
    id: int

    record_date: datetime.datetime | None = pydantic.Field(
        json_schema_extra=dict(example="2023-01-01T00:00:00.000000"), default=None
    )

class CreateRecord(BaseRecord):
    record_date: Optional[datetime.datetime] = pydantic.Field(
        json_schema_extra=dict(example="2023-01-01T00:00:00.000000")
    )

class UpdatedRecord(BaseRecord):
    type: Optional[str] = None
    amount: Optional[int] = None
    currency: Optional[str] = "THB"

    category_id: Optional[int] = None
    # category_name: Optional[str] = None
    
    record_date: Optional[datetime.datetime] = pydantic.Field(
        json_schema_extra=dict(example="2023-01-01T00:00:00.000000")
    )

class DBRecord(BaseRecord, SQLModel, table=True):
    __tablename__ = "records"
    id: int | None = Field(default=None, primary_key=True)

    user_id: int = Field(default=None, foreign_key="users.id")
    user: users.DBUser = Relationship()

    amount: float
    currency: str
    type: str
    description: str | None = Field(default=None)

    pocket_id: int | None = Field(default=None, foreign_key="pockets.id")
    pocket: pockets.DBPocket = Relationship()

    category: categories.DBCategory = Relationship()
    category_id: int = Field(default=None, foreign_key="categories.id")
    category_name: str

    record_date: datetime.datetime = Field(default_factory=datetime.datetime.now)

    is_monthly: bool = Field(default=False)
    setup_id: int | None = Field(default=None, foreign_key="setups.id")

    #pocket_id: int = Field(default=None, foreign_key="pockets.id")
    #pocket: Optional["DBPocket"] = Relationship(back_populates="monthly_expenses")

class RecordList(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    records: list[Records]
