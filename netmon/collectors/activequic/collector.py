import asyncio
import ssl
from collections.abc import Iterable
from datetime import UTC, datetime, timedelta
from typing import override
from uuid import uuid4

import msgpack # type: ignore
from aioquic.asyncio.client import connect
from aioquic.asyncio.protocol import QuicConnectionProtocol
from aioquic.quic.configuration import QuicConfiguration
from aioquic.quic.events import ConnectionTerminated, DatagramFrameReceived, ProtocolNegotiated
from structlog.stdlib import BoundLogger # type: ignore

from netmon.collectors.activequic.message import QUICMessage # type: ignore
from interface import MetricsCollector # type: ignore
from base_metric_entry import BaseMetricEntry # type: ignore
from metricvalue import MetricValue # type: ignore
from storage import InMemoryStorage # type: ignore

class ClientQUICProtocol(QuicConnectionProtocol):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.messages: asyncio.Queue[bytes] = asyncio.Queue()
        self.wait_closed_event = asyncio.Event()

    def send_message(self, msg: QUICMessage) -> None:
        data = msgpack.packb(msg.to_dict(), use_bin_type=True)
        self._quic.send_datagram_frame(data)
        self.transmit()

    def quic_event_received(self, event) -> None:
        if isinstance(event, DatagramFrameReceived):
            self.messages.put_nowait(event.data)
        elif isinstance(event, ConnectionTerminated):
            self.wait_closed_event.set()

class ActiveQUICClientProtocol(QuicConnectionProtocol):
    def __init__(self, *args, logger: BoundLogger, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._logger = logger
        self._messages: asyncio.Queue[QUICMessage] = asyncio.Queue()
        self._connected = asyncio.Event()
        self._closed = asyncio.Event()

    @property
    def messages(self) -> asyncio.Queue[QUICMessage]:
        return self._messages

    async def wait_connected(self) -> None:
        await self._connected.wait()

    async def wait_closed_event(self) -> None:
        await self._closed.wait()

    def send_message(self, message: QUICMessage) -> None:
        payload = msgpack.packb(message, use_bin_type=True)
        self._quic.send_datagram_frame(payload)
        self.transmit()

    def quic_event_received(self, event) -> None:
        if isinstance(event, ProtocolNegotiated):
            self._logger.info("QUIC protocol negotiated", alpn=event.alpn_protocol)
            self._connected.set()
            return

        if isinstance(event, DatagramFrameReceived):
            packet = msgpack.unpackb(event.data, raw=False)
            self._messages.put_nowait(packet)
            return

        if isinstance(event, ConnectionTerminated):
            self._logger.warning(
                "QUIC connection terminated",
                error_code=event.error_code,
                frame_type=event.frame_type,
                reason=event.reason_phrase,
            )
            self._closed.set()


class ActiveQUICCollector(MetricsCollector):
    def __init__(
        self,
        logger: BoundLogger,
        addr: str,
        port: int,
        metrics_interval: timedelta,
        packet_send_delay: timedelta = timedelta(seconds=5),
        reconnect_interval: timedelta = timedelta(seconds=15),
        read_timeout: timedelta = timedelta(seconds=10),
        certificate_authority_path: str | None = None,
        server_name: str | None = None,
        insecure_skip_verify: bool = False,
        alpn_protocols: list[str] | None = None,
    ) -> None:
        self._logger = logger
        self._metrics_interval = metrics_interval
        self._reconnect_delay = reconnect_interval
        self._addr = addr
        self._port = port
        self._packet_send_delay = packet_send_delay
        self._read_timeout = read_timeout
        self._certificate_authority_path = certificate_authority_path
        self._server_name = server_name or addr
        self._insecure_skip_verify = insecure_skip_verify
        self._alpn_protocols = alpn_protocols or ["netmon-activequic"]

        self._stop_event = asyncio.Event()
        self._is_running = False

        self._sent_packet = InMemoryStorage[datetime]()
        self._latency_to_server = InMemoryStorage[float]()
        self._latency_from_server = InMemoryStorage[float]()
        self._rtt = InMemoryStorage[float]()

    @override
    async def collect(self, time: datetime) -> Iterable[BaseMetricEntry]:
        rtt = MetricValue()
        rtt.add_all(list(self._rtt.values()))

        latency_to_server = MetricValue()
        latency_to_server.add_all(list(self._latency_to_server.values()))

        latency_from_server = MetricValue()
        latency_from_server.add_all(list(self._latency_from_server.values()))

        return [
            BaseMetricEntry(
                origin=self.__class__.__name__,
                timestamp=datetime.now().timestamp(),
                destinatation=self._addr,
                rtt=rtt,
                latency_from=latency_from_server,
                latency_to=latency_to_server,
                packet_loss=self._packet_loss(),
            )
        ]

    def _create_configuration(self) -> QuicConfiguration:
        configuration = QuicConfiguration(
            is_client=True,
            alpn_protocols=self._alpn_protocols,
        )
        configuration.max_datagram_frame_size = 65535
        configuration.server_name = self._server_name
        if self._certificate_authority_path:
            configuration.load_verify_locations(self._certificate_authority_path)

        if self._insecure_skip_verify:
            configuration.verify_mode = ssl.CERT_NONE
        else:
            configuration.verify_mode = ssl.CERT_REQUIRED

        return configuration

    def _packet_loss(self) -> float:
        all_sent_packets = {k for k, _ in self._sent_packet.items()}
        all_received_packets = {k for k, _ in self._rtt.items()}

        lost_packet_ids = all_sent_packets - all_received_packets

        if len(all_sent_packets) == 0:
            return 0.0

        return len(lost_packet_ids) / len(all_sent_packets)

    async def handle_received_packet(self, packet: QUICMessage) -> None:
        """Обработка входящего пакета"""
        log = self._logger.bind(action="handle_received_packet", packet=packet)
        message_id = packet["reply_to"]

        if message_id is None:
            log.error("packet from server without message_id")
            return

        now = datetime.now(tz=UTC)

        sent_to_at = self._sent_packet.get(message_id)
        if sent_to_at is None:
            log.warning("sent_to timestamp not found")
            return

        sent_from_at = datetime.fromtimestamp(packet["sent_at"], tz=UTC)
        if sent_to_at.tzinfo is None:
            sent_to_at = sent_to_at.replace(tzinfo=UTC)

        latency_from_server = now - sent_from_at
        latency_to_server = sent_from_at - sent_to_at
        rtt = latency_from_server + latency_to_server

        log.debug(
            "calculated metrics",
            rtt=rtt,
            latency_from_server=latency_from_server,
            latency_to_server=latency_to_server,
        )

        self._rtt.add(message_id, rtt.total_seconds(), self._metrics_interval)
        self._latency_from_server.add(message_id, latency_from_server.total_seconds(), self._metrics_interval)
        self._latency_to_server.add(message_id, latency_to_server.total_seconds(), self._metrics_interval)

    async def send_messages_loop(self, protocol: ActiveQUICClientProtocol) -> None:
        """Цикл отправки сообщений."""
        log = self._logger.bind(action="send_messages_loop")
        while not self._stop_event.is_set():
            now = datetime.now(tz=UTC)
            msg: QUICMessage = {
                "message_id": str(uuid4()),
                "reply_to": None,
                "sent_at": now.timestamp(),
                "additional_data": None,
            }

            self._sent_packet.add(msg["message_id"], now, self._metrics_interval)

            try:
                protocol.send_message(msg)
                log.debug("Sent QUIC message", message_id=msg["message_id"])
            except Exception as e:
                log.exception("Failed to send message", error=e)
                raise

            await asyncio.sleep(self._packet_send_delay.total_seconds())

    async def receiving_messages_loop(self, protocol: ActiveQUICClientProtocol) -> None:
        """Цикл приёма сообщений через QUIC DATAGRAM."""
        log = self._logger.bind(action="receiving_messages_loop")

        while not self._stop_event.is_set():
            try:
                packet = await asyncio.wait_for(protocol.messages.get(), self._read_timeout.total_seconds())
                await self.handle_received_packet(packet)
            except TimeoutError:
                if protocol._closed.is_set():
                    raise ConnectionError("QUIC connection closed")
                log.debug("no packets received before timeout")
            except Exception as e:
                log.error("Error receiving message", error=e)
                raise

    async def _run_one_connection(self) -> None:
        log = self._logger.bind(action="_run_one_connection")
        configuration = self._create_configuration()
        self._stop_event = asyncio.Event()

        try:
            log.info("Attempting to connect", addr=self._addr, port=self._port)
            async with connect(
                self._addr,
                self._port,
                configuration=configuration,
                create_protocol=lambda *args, **kwargs: ActiveQUICClientProtocol(
                    *args,
                    logger=self._logger,
                    **kwargs,
                ),
                wait_connected=True,
            ) as protocol:
                await protocol.wait_connected()
                log.info("Connected to QUIC server", addr=self._addr, port=self._port)

                send_task = asyncio.create_task(self.send_messages_loop(protocol))
                recv_task = asyncio.create_task(self.receiving_messages_loop(protocol))
                closed_task = asyncio.create_task(protocol.wait_closed_event())

                done, pending = await asyncio.wait(
                    {send_task, recv_task, closed_task},
                    return_when=asyncio.FIRST_EXCEPTION,
                )

                for task in pending:
                    task.cancel()

                for task in done:
                    exc = task.exception()
                    if exc is not None:
                        raise exc
        except Exception as e:
            log.warning("QUIC connection failed", error=str(e))
            raise

    async def run_collector(self) -> None:
        """Создание подключения и запуск циклов отправки и приёма."""
        log = self._logger.bind(action="run_collector")
        self._is_running = True
        while self._is_running:
            try:
                await self._run_one_connection()
            except Exception as e:
                log.warning("Connection attempt failed", error=str(e))
                await asyncio.sleep(self._reconnect_delay.total_seconds())

    async def start_collector(self) -> None:
        asyncio.create_task(self.run_collector())

    async def stop(self) -> None:
        self._stop_event.set()
        self._is_running = False
