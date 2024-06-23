from typing import List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from ws import connection_manager

from dotenv import load_dotenv

load_dotenv()

from users import router as users_router
from recipes import router as recipes_router
from auth import router as auth_router

app = FastAPI(port=8000)

origins = [
    # "*"
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"greetings": "traveler"}

app.include_router(users_router, prefix="/users")
app.include_router(recipes_router, prefix="/recipes")
app.include_router(auth_router)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await connection_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket)
