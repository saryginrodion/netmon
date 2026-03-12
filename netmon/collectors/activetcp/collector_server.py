import asyncio
import uuid
from datetime import UTC, datetime

import msgpack
from structlog.stdlib import BoundLogger

from netmon.collectors.activetcp.message import TCPMessage


class ActiveTCPServer(asyncio.Protocol):
    """Сервер коллектора для ActiveTCPCollector.

    Принимает и переупаковывает сообщения, которые прислал ему клиент.
    """

    def __init__(self, logger: BoundLogger) -> None:
        self._logger = logger
        self._server = None

    async def handle_client(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
    ) -> None:
        log = self._logger.bind(action="handle_client", trace_id=uuid.uuid4(), peername=writer.get_extra_info("peername"))
        unpacker = msgpack.Unpacker(raw=False)

        try:
            while True:
                data: bytes = await reader.read(4096)
                if not data:
                    break

                unpacker.feed(data)

                for request in unpacker:
                    log.info("received message", message=request)
                    response: TCPMessage = {
                        "message_id": str(uuid.uuid4()),
                        "reply_to": request["message_id"],
                        "sent_at": datetime.now(tz=UTC).timestamp(),
                        "additioinal_data": None,
                    }

                    response_packed: bytes = msgpack.packb(response)  # type: ignore
                    writer.write(response_packed)
                    log.info("wrote message", message=response)

                await writer.drain()

        except Exception as e:
            log.exception("error while handling client", error=str(e))

        finally:
            writer.close()
            await writer.wait_closed()

    async def start_server(self, addr: str, port: int) -> None:
        log = self._logger.bind(action="start_server", addr=addr, port=port)

        try:
            self._server = await asyncio.start_server(self.handle_client, addr, port)
            log.info("server started")
        except Exception as e:
            log.exception("failed to start server", error=str(e))
            raise e
