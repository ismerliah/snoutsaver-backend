from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from sqlmodel import Field, SQLModel, Relationship


class BaseCategory(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    type: str  # Expense or Income
    icon: str  # Store the icon name as a string


class CreatedCategory(BaseCategory):
    pass


class UpdatedCategory(BaseCategory):
    name: Optional[str] = None
    type: Optional[str] = None
    icon: Optional[str] = None


class Category(BaseCategory):
    id: int


class DBCategory(Category, SQLModel, table=True):
    __tablename__ = "categories"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    type: str
    icon: str

class CategoryList(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    items: list[Category]
    page: int
    page_size: int
    size_per_page: int
