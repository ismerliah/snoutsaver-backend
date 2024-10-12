from pydantic import BaseModel, ConfigDict
from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional

from . import users
from . import records

class BaseSetup(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    monthly_income: float
    saving_goal: float
    year: int

class Setups(BaseSetup):
    id: int
    monthly_expenses: Optional[List[dict]] = None

class CreateSetup(BaseSetup):
    monthly_expenses: Optional[List[dict]] = None

class UpdatedSetup(BaseSetup):
    monthly_income: Optional[float] = None
    saving_goal: Optional[float] = None
    year: Optional[int] = None
    monthly_expenses: Optional[List[dict]] = None

class DBSetup(SQLModel, table=True):
    __tablename__ = "setups"
    id: int | None = Field(default=None, primary_key=True)

    user_id: int = Field(default=None, foreign_key="users.id")
    user: users.DBUser = Relationship()

    monthly_income: float
    saving_goal: float
    year: int = Field(default=1)

    monthly_expenses: List[records.DBRecord] = Relationship()

class SetupList(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    items: list[Setups]
    page: int
    page_size: int
    size_per_page: int