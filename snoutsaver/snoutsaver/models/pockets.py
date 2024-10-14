from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from sqlmodel import Field, SQLModel, Relationship

from . import users
from . import records
from . import categories

class BasePocket(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    name: str
    balance: float
    category: Optional[List[dict]] = None 

class PocketCreate(BasePocket):
    monthly_expenses: Optional[List[dict]] = None

class AllPocket(BasePocket):
    id: int
    user_id: int
    monthly_expenses: Optional[List[dict]] = None

class PocketTransfer(BaseModel):
    from_pocket_id: int = Field(default=None, foreign_key="pockets.id")
    to_pocket_id: int = Field(default=None, foreign_key="pockets.id")
    amount: float 

class DBPocket(SQLModel, table=True):
    __tablename__ = "pockets"
    id: int | None = Field(default=None, primary_key=True)

    user_id: int = Field(default=None, foreign_key="users.id")
    user: users.DBUser = Relationship()

    name: str
    balance: float

    category: List[categories.DBCategory] = Relationship()
    monthly_expenses: List[records.DBRecord] = Relationship()


class PocketList(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    items: list[AllPocket]
    page: int
    page_size: int
    size_per_page: int