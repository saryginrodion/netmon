import asyncio
import uuid
from asyncio import transports
from datetime import UTC, datetime

import msgpack
from structlog.stdlib import BoundLogger

from collectors.activetcp.message import TCPMessage


class ActiveTCPServer(asyncio.Protocol):
    """Сервер коллектора для ActiveTCPCollector.

    Принимает и переупаковывает сообщения, которые прислал ему клиент.
    """

    def __init__(self, logger: BoundLogger) -> None:
        self._logger = logger.bind()


    async def handle_client(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
    ) -> None:
        unpacker = msgpack.Unpacker(raw=False)
    
        try:
            while True:
                data: bytes = await reader.read(4096)
                if not data:
                    break
    
                unpacker.feed(data)
    
                for request in unpacker:
                    response: TCPMessage = {
                        "message_id": uuid.uuid4(),
                        "reply_to": request["message_id"],
                        "sent_at": datetime.now(tz=UTC).timestamp(),
                        "additioinal_data": None,
                    }
    
                    response_packed: bytes = msgpack.packb(response)  # type: ignore
                    writer.write(response_packed)
    
                await writer.drain()
    
        except Exception as e:
            self._logger.exception("error while handling client", error=str(e))
    
        finally:
            writer.close()
            await writer.wait_closed()
