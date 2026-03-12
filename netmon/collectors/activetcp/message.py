from typing import TypedDict


# TODO: change to pydantic.BaseModel
class TCPMessage(TypedDict):
    message_id: str
    reply_to: str | None
    sent_at: float
    additioinal_data: dict | None
