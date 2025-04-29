from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = "sqlite:///database.db"
engine = create_engine(DATABASE_URL, echo=False)
session_maker = sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass

