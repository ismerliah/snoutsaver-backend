from typing import Optional
from pydantic import BaseModel, ConfigDict
from sqlmodel import Field, SQLModel


class PocketCreate(BaseModel):
    user_id: int = Field(default=None, foreign_key="users.id")
    pocket_id : int
    name: str 
    category: Optional[str] = None
    balance: float 
    monthly_expense: Optional[float] = None

class PocketTransfer(BaseModel):
    from_pocket_id: int 
    to_pocket_id: int 
    amount: float 