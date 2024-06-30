import json  # Import json module
from fastapi import FastAPI, WebSocket, Depends, Query
from typing import List

from sqlmodel import SQLModel, Session, select

from .database import engine, get_session
from .models import Message, User

app = FastAPI()


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


@app.on_event('startup')
def on_startup():
    create_db_and_tables()


@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket, username: str = Query(...), session: Session = Depends(get_session)):
    await manager.connect(websocket)

    user = session.exec(select(User).where(User.username == username)).first()
    if not user:
        user = User(username=username)
        session.add(user)
        session.commit()
        session.refresh(user)

    try:
        while True:
            data = await websocket.receive_text()
            message = Message(content=data, user_id=user.id)
            session.add(message)
            try:
                session.commit()
            except Exception as e:
                session.rollback()
                print(f"Error committing message: {e}")

            # Create a JSON message
            json_message = {
                "username": username,
                "content": data
            }
            await manager.broadcast(json.dumps(json_message))
    except Exception as e:
        print(f"Error: {e}")
    finally:
        manager.disconnect(websocket)