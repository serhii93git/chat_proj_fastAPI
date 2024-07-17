from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional
from datetime import datetime


class Message(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    content: str = Field(title='повідомлення')
    send_time: datetime = Field(default_factory=datetime.utcnow)
    user_id: int = Field(foreign_key="user.id")
    user: Optional['User'] = Relationship(back_populates="messages")


class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    username: str = Field(title='нік')
    messages: List[Message] = Relationship(back_populates="user")


Message.user = Relationship(back_populates="messages")
