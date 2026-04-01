import asyncio
import ssl
import uuid
from datetime import UTC, datetime

import msgpack # type: ignore
from aioquic.asyncio import serve
from aioquic.asyncio.protocol import QuicConnectionProtocol
from aioquic.quic.configuration import QuicConfiguration
from aioquic.quic.events import DatagramFrameReceived, ProtocolNegotiated
from structlog.stdlib import BoundLogger # type: ignore

from netmon.collectors.activequic.message import QUICMessage # type: ignore


class ActiveQUICServerProtocol(QuicConnectionProtocol):
    """Сервер коллектора для ActiveQUICCollector.

    Принимает QUIC DATAGRAM и отправляет ответ с reply_to.
    """

    def __init__(self, *args, logger: BoundLogger, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._logger = logger

    def quic_event_received(self, event) -> None:
        if isinstance(event, ProtocolNegotiated):
            self._logger.info("QUIC protocol negotiated", alpn=event.alpn_protocol)
            return

        if isinstance(event, DatagramFrameReceived):
            log = self._logger.bind(action="quic_event_received", trace_id=str(uuid.uuid4()))
            request: QUICMessage = msgpack.unpackb(event.data, raw=False)
            log.info("received message", message=request)

            response: QUICMessage = {
                "message_id": str(uuid.uuid4()),
                "reply_to": request["message_id"],
                "sent_at": datetime.now(tz=UTC).timestamp(),
                "additional_data": None,
            }

            payload = msgpack.packb(response, use_bin_type=True)
            self._quic.send_datagram_frame(payload)
            self.transmit()
            log.info("wrote message", message=response)


class ActiveQUICServer:
    def __init__(self, logger: BoundLogger) -> None:
        self._logger = logger
        self._server = None

    async def start_server(
        self,
        addr: str,
        port: int,
        certificate_path: str,
        private_key_path: str,
        alpn_protocols: list[str] | None = None,
    ) -> None:
        log = self._logger.bind(action="start_server", addr=addr, port=port)
        configuration = QuicConfiguration(
            is_client=False,
            alpn_protocols=alpn_protocols or ["netmon-activequic"],
        )
        configuration.max_datagram_frame_size = 65535
        configuration.load_cert_chain(certificate_path, private_key_path)
        configuration.verify_mode = ssl.CERT_NONE

        try:
            self._server = await serve(
                addr,
                port,
                configuration=configuration,
                create_protocol=lambda *args, **kwargs: ActiveQUICServerProtocol(*args, logger=self._logger, **kwargs),
            )
            log.info("server started")
        except Exception as e:
            log.exception("failed to start server", error=str(e))
            raise
