from typing import TypedDict


class UDPMessage(TypedDict):
    message_id: str
    reply_to: str | None
    sent_at: float
    additioinal_data: dict | None
