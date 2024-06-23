from fastapi import APIRouter
from sqlmodel import Session, create_engine, select, SQLModel

from db import engine
from models import User

router = APIRouter()


@router.get("/")
def read_users():
    with Session(engine) as session:
        statement = select(User).with_only_columns(
            User.id,
            User.name,
            User.given_name,
            User.family_name,
            User.picture,
        )
        users = session.exec(statement)
        return users.all()
