from typing import TypedDict
from uuid import UUID


class TCPMessage(TypedDict):
    message_id: UUID
    reply_to: UUID | None
    sent_at: float
    additioinal_data: dict | None
