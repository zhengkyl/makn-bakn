from datetime import datetime, UTC
from typing import Optional
from sqlmodel import Field, Relationship, SQLModel


class User(SQLModel, table=True):
    id: Optional[int] = Field(
        default=None, primary_key=True
    )  # generated by database, so init with None
    google_id: str
    name: str
    given_name: str
    family_name: str
    email: str
    picture: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    badges: list["Badge"] = Relationship(back_populates="user")
    meals: list["Meal"] = Relationship(back_populates="user")


class Badge(SQLModel, table=True):
    id: Optional[int] = Field(
        default=None, primary_key=True
    )  # generated by database, so init with None
    name: str
    picture: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    user_id: int = Field(foreign_key="user.id")
    user: User = Relationship(back_populates="badges")


class Meal(SQLModel, table=True):
    id: Optional[int] = Field(
        default=None, primary_key=True
    )  # generated by database, so init with None
    name: str
    picture: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    user_id: int = Field(foreign_key="user.id")
    user: User = Relationship(back_populates="meals")
