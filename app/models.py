from sqlmodel import SQLModel, Field
from datetime import datetime

class Message(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    content: str = Field(title='повідомлення')
    send_time: datetime = Field(default_factory=datetime.utcnow)
