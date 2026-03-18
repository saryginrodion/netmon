# TODO: vibecoded it, maybe need some fixes
import asyncio
import socket
from collections.abc import Iterable
from datetime import datetime, timedelta
from typing import override
from uuid import uuid4

import msgpack
from structlog.stdlib import BoundLogger

from netmon.collectors.interface import MetricsCollector
from netmon.entities.base_metric_entry import BaseMetricEntry
from netmon.entities.metricvalue import MetricValue
from netmon.in_memory_storage.storage import InMemoryStorage


class ActiveUDPCollector(MetricsCollector):
    def __init__(
        self,
        logger: BoundLogger,
        addr: str,
        port: int,
        metrics_interval: timedelta,
        packet_send_delay: timedelta = timedelta(seconds=5),
        read_timeout: timedelta = timedelta(seconds=10),
    ) -> None:

        self._logger = logger
        self._metrics_interval = metrics_interval
        self._addr = addr
        self._port = port
        self._packet_send_delay = packet_send_delay
        self._read_timeout = read_timeout

        self._stop_event = asyncio.Event()
        self._is_running = False

        self._sock: socket.socket | None = None

        self._sent_packet = InMemoryStorage[datetime]()
        self._latency_to_server = InMemoryStorage[float]()
        self._latency_from_server = InMemoryStorage[float]()
        self._rtt = InMemoryStorage[float]()

    # ----------------------------------------------------------------

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

    # ----------------------------------------------------------------

    def _packet_loss(self) -> float:
        all_sent_packets = {k for k, _ in self._sent_packet.items()}
        all_received_packets = {k for k, _ in self._rtt.items()}

        lost_packet_ids = all_sent_packets - all_received_packets

        if len(all_sent_packets) == 0:
            return 0.0

        return len(lost_packet_ids) / len(all_sent_packets)

    # ----------------------------------------------------------------

    async def handle_received_packet(self, packet) -> None:

        log = self._logger.bind(action="handle_received_packet", packet=packet)

        message_id = packet["reply_to"]

        if message_id is None:
            log.error("packet from server without message_id")
            return

        now = datetime.now()

        sent_to_at = self._sent_packet.get(message_id)
        if sent_to_at is None:
            log.warning("sent_to timestamp not found")
            return

        sent_from_at = datetime.fromtimestamp(packet["sent_at"])

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

    # ----------------------------------------------------------------

    async def send_messages_loop(self) -> None:

        log = self._logger.bind(action="send_messages_loop")

        assert self._sock is not None
        loop = asyncio.get_running_loop()

        while not self._stop_event.is_set():
            msg = {
                "message_id": str(uuid4()),
                "reply_to": None,
                "sent_at": datetime.now().timestamp(),
                "additioinal_data": None,
            }

            self._sent_packet.add(msg["message_id"], datetime.now(), self._metrics_interval)

            try:
                packed = msgpack.packb(msg)

                await loop.sock_sendto(
                    self._sock,
                    packed,  # type: ignore
                    (self._addr, self._port),
                )

                log.debug("Sent UDP message", message_id=msg["message_id"])

            except Exception as e:
                log.exception("Failed to send message", error=e)

            await asyncio.sleep(self._packet_send_delay.total_seconds())

    # ----------------------------------------------------------------

    async def receiving_messages_loop(self) -> None:

        log = self._logger.bind(action="receiving_messages_loop")

        assert self._sock is not None
        loop = asyncio.get_running_loop()

        while not self._stop_event.is_set():
            try:
                data, _ = await asyncio.wait_for(
                    loop.sock_recvfrom(self._sock, 4096),
                    self._read_timeout.total_seconds(),
                )

                packet = msgpack.unpackb(data, raw=False)

                await self.handle_received_packet(packet)

            except asyncio.TimeoutError:
                continue

            except Exception as e:
                log.error("Error receiving message", error=e)

    # ----------------------------------------------------------------

    async def _run(self) -> None:
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.setblocking(False)

        send_task = asyncio.create_task(self.send_messages_loop())
        recv_task = asyncio.create_task(self.receiving_messages_loop())

        try:
            await asyncio.gather(send_task, recv_task)
        finally:
            send_task.cancel()
            recv_task.cancel()
            self._sock.close()

    # ----------------------------------------------------------------

    async def run_collector(self) -> None:

        self._is_running = True

        while self._is_running:
            await self._run()

    # ----------------------------------------------------------------

    async def start_collector(self) -> None:
        asyncio.create_task(self.run_collector())

    # ----------------------------------------------------------------

    async def stop(self) -> None:
        self._stop_event.set()
        self._is_running = False
