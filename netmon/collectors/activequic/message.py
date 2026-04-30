from typing import TypedDict


class QUICMessage(TypedDict):
    message_id: str
    reply_to: str | None
    sent_at: float