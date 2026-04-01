from typing import TypedDict


# TODO: change to pydantic.BaseModel
class QUICMessage(TypedDict):
    message_id: str
    reply_to: str | None
    sent_at: float
    additional_data: dict | None
