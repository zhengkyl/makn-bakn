import os
import base64
import json
from typing import Annotated
import httpx
from fastapi import APIRouter, Cookie, Depends, HTTPException
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
    response_data = response.json()
    access_token = response_data.get("access_token")
    id_token = response_data.get("id_token")
    
    user_info = httpx.get("https://www.googleapis.com/oauth2/v1/userinfo", headers={"Authorization": f"Bearer {access_token}"})

    user_info = user_info.json()

    # id_payload = base64.b64decode(id_token.split(".")[1])
    # id_payload = json.loads(id_payload)
    
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
# {"access_token": access_token, "id_token": id_token}
    resp = RedirectResponse("/")
    resp.set_cookie(key="access_token", value=access_token)
    resp.set_cookie(key="id", value=id_token)
# headers={"Set-Cookie": f"access_token={access_token}; HttpOnly; Secure",
#                                           "Set-Cookie": f"id_token={id_token}; HttpOnly; Secure" }
    return resp

async def get_current_user(id_token: Annotated[str, Cookie()]):
    payload = base64.b64decode(id_token.split(".")[1] + "==")
    payload = json.loads(payload)
    
    with Session(engine) as session:
      stmt = select(User).where(User.google_id == str(payload["sub"]))
      user = session.exec(stmt).first()
      if user == None:
        raise HTTPException(status_code=401)
      
      return user
