from typing import TypedDict


class TCPMessage(TypedDict):
    message_id: str
    reply_to: str | None
    sent_at: float
    additioinal_data: dict | None
