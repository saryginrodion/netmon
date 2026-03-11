import asyncio
import uuid
from asyncio import transports
from datetime import UTC, datetime

import msgpack

from collectors.activetcp.message import TCPMessage


class ActiveTCPServer(asyncio.Protocol):
    def connection_made(self, transport: transports.Transport) -> None:
        peername = transport.get_extra_info("peername")
        print(f"connection from {peername}")
        self.transport: asyncio.Transport = transport

    def data_received(self, data: bytes) -> None:
        request: TCPMessage = msgpack.unpackb(data)
        print("received message:", request)

        response: TCPMessage = {
            "message_id": uuid.uuid4(),
            "reply_to": request["message_id"],
            "sent_at": datetime.now(tz=UTC).timestamp(),
            "additioinal_data": None,
        }

        response_packed: bytes = msgpack.packb(response)  # type: ignore
        self.transport.write(response_packed)


async def main() -> None:
    loop = asyncio.get_running_loop()

    server = await loop.create_server(
        ActiveTCPServer,
        "127.0.0.1",
        8001,
    )

    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
