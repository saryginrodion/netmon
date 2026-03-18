# TODO: vibecoded it, maybe need some fixes
import asyncio
from asyncio.protocols import DatagramProtocol
import uuid
from datetime import datetime, UTC

import msgpack
from structlog.stdlib import BoundLogger

from netmon.collectors.activeudp.message import UDPMessage


class ActiveUDPServer(asyncio.DatagramProtocol):
    """Сервер для активного теста UDP протокола."""
    def __init__(self, logger: BoundLogger):
        self._logger = logger
        self.transport = None

    def connection_made(self, transport: DatagramProtocol):
        self.transport = transport
        self._logger.info("UDP server started")

    def datagram_received(self, data: bytes, addr):
        try:
            request = msgpack.unpackb(data, raw=False)

            self._logger.info("received message", message=request)

            response: UDPMessage = {
                "message_id": str(uuid.uuid4()),
                "reply_to": request["message_id"],
                "sent_at": datetime.now(tz=UTC).timestamp(),
                "additioinal_data": None,
            }

            packed: bytes = msgpack.packb(response)  # type: ignore

            self.transport.sendto(packed, addr)  # type: ignore

        except Exception as e:
            self._logger.error("failed handling datagram", error=str(e))

    async def start(self, addr: str, port: int):
        loop = asyncio.get_running_loop()

        await loop.create_datagram_endpoint(
            lambda: self,
            local_addr=(addr, port),
        )
