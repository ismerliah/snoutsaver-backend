from typing import Optional

from sqlmodel import Field, SQLModel, create_engine, Session, select

from . import users
from . import categories
from . import records


connect_args = {}

engine = create_engine(
    "postgresql+pg8000://postgres:123456@localhost/snoutsaverdb",
    echo=True,
    connect_args=connect_args,
)


def init_db():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
