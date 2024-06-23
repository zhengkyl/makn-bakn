import os
import httpx
from fastapi import APIRouter
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select
from models import User
from db import engine

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.get("/login/google")
async def login_google():
  return RedirectResponse(f"https://accounts.google.com/o/oauth2/auth?response_type=code&client_id={os.environ.get("GOOGLE_CLIENT_ID")}&redirect_uri={os.environ.get("GOOGLE_REDIRECT_URI")}&scope=openid%20profile%20email&access_type=offline")

@router.get("/auth/google")
async def auth_google(code: str):
    token_url = "https://accounts.google.com/o/oauth2/token"
    data = {
        "code": code,
        "client_id": os.environ.get("GOOGLE_CLIENT_ID"),
        "client_secret": os.environ.get("GOOGLE_CLIENT_SECRET"),
        "redirect_uri": os.environ.get("GOOGLE_REDIRECT_URI"),
        "grant_type": "authorization_code",
    }
    response = httpx.post(token_url, data=data)
    access_token = response.json().get("access_token")
    
    user_info = httpx.get("https://www.googleapis.com/oauth2/v1/userinfo", headers={"Authorization": f"Bearer {access_token}"})

    user_info = user_info.json()

    with Session(engine) as session:
        stmt = select(User).where(User.google_id == str(user_info["id"]))
        user = session.exec(stmt).first()

        if user == None:
          new_user = User(google_id=str(user_info["id"]),
              name=user_info["name"],
              given_name=user_info["given_name"],
              family_name=user_info["family_name"],
              email=user_info["email"],
              picture = user_info["picture"])
          session.add(new_user)
          session.commit()
    
    # should redirect immediately, but client side i guess
    return {"token": access_token}
