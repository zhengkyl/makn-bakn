from typing import Annotated
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlmodel import Session, select

from auth import get_current_user
from db import engine
from models import Badge, Meal, User
from ws import connection_manager

router = APIRouter()


@router.get("/")
def read_users(skip: Annotated[int, Query()] = 0, limit: Annotated[int, Query()] = 10):
    with Session(engine) as session:
        stmt = (
            select(User)
            .with_only_columns(
                User.id,
                User.name,
                User.given_name,
                User.family_name,
                User.picture,
            )
            .order_by(User.created_at.desc())
            .skip(skip)
            .limit(limit)
        )
        users = session.exec(stmt)
        return users.all()


class NewBadge(BaseModel):
    name: str
    picture: str


@router.post("/badges")
def create_badge(new_badge: NewBadge, user: Annotated[User, Depends(get_current_user)]):
    with Session(engine) as session:
        badge = Badge(name=new_badge.name, picture=new_badge.picture, user=user)
        session.add(badge)
        session.commit()
        session.refresh(badge)

        connection_manager.broadcast(
            {
                "type": "badge",
                "name": badge.name,
                "picture": badge.picture,
                "user": user.name,
                "created_at": badge.created_at,
            }
        )
        return badge


@router.get("/badges")
def read_badges(
    user: Annotated[User, Depends(get_current_user)],
    skip: Annotated[int, Query()] = 0,
    limit: Annotated[int, Query()] = 10,
):
    with Session(engine) as session:
        stmt = (
            select(Badge)
            .where(Badge.user == user)
            .order_by(Badge.created_at.desc())
            .skip(skip)
            .limit(limit)
        )
        badges = session.exec(stmt)
        return badges.all()


class NewMeal(BaseModel):
    name: str
    picture: str


@router.post("/meals")
def create_meal(new_meal: NewMeal, user: Annotated[User, Depends(get_current_user)]):
    with Session(engine) as session:
        meal = Meal(name=new_meal.name, picture=new_meal.picture, user=user)
        session.add(meal)
        session.commit()
        session.refresh(meal)

        connection_manager.broadcast(
            {
                "type": "meal",
                "name": meal.name,
                "picture": meal.picture,
                "user": user.name,
                "created_at": meal.created_at,
            }
        )
        return meal


@router.get("/meals")
def read_meals(
    user: Annotated[User, Depends(get_current_user)],
    skip: Annotated[int, Query()] = 0,
    limit: Annotated[int, Query()] = 10,
):
    with Session(engine) as session:
        stmt = (
            select(Meal)
            .where(Meal.user == user)
            .order_by(Meal.created_at.desc())
            .skip(skip)
            .limit(limit)
        )
        meals = session.exec(stmt)
        return meals.all()


@router.get("/feed")
def read_feed(
    meals: Annotated[bool, Query()] = True,
    badges: Annotated[bool, Query()] = True,
):
    with Session(engine) as session:
        stmt = select(Meal).order_by(Meal.created_at.desc()).limit(50)
        meals = session.exec(stmt)
        meals = meals.all()

        stmt = select(Badge).order_by(Badge.created_at.desc()).limit(50)
        badges = session.exec(stmt)
        badges = badges.all()

        i = 0
        j = 0
        feed = []
        while i < len(meals) or j < len(badges):
            if i == len(meals):
                feed.append(badges[j])
                j += 1
            elif j == len(badges):
                feed.append(meals[i])
                i += 1
            elif meals[i].created_at <= badges[j].created_at:
                feed.append[meals[i]]
                i += 1
            else:
                feed.append(badges[j])
                j += 1

        return feed
