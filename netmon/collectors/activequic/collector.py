import asyncio
from uuid import uuid4
from datetime import datetime, timedelta
from collections.abc import Iterable
from typing import override

from aioquic.asyncio.client import connect
from structlog.stdlib import BoundLogger

from netmon.collectors.interface import MetricsCollector
from netmon.entities.base_metric_entry import BaseMetricEntry
from netmon.entities.metric_name_enum import MetricName
from netmon.entities.metricvalue import MetricValue
from netmon.in_memory_storage.storage import InMemoryStorage


class ActiveQUICCollector(MetricsCollector):

    def __init__(
        self,
        logger: BoundLogger,
        addr: str,
        port: int,
        metrics_interval: timedelta,
        packet_send_delay: timedelta = timedelta(seconds=1),
        origin_name: str = "ActiveQUICCollector",
    ):
        self._logger = logger
        self._addr = addr
        self._port = port
        self._metrics_interval = metrics_interval
        self._packet_send_delay = packet_send_delay
        self._origin_name = origin_name

        self._stop_event = asyncio.Event()

        self._sent_packet = InMemoryStorage[datetime]()
        self._rtt = InMemoryStorage[float]()


    def _packet_loss(self):
        sent = {k for k, _ in self._sent_packet.items()}
        recv = {k for k, _ in self._rtt.items()}

        if not sent:
            return 0

        return len(sent - recv) / len(sent)

    @override
    async def collect(self, time: datetime) -> Iterable[BaseMetricEntry]:
        rtt = MetricValue()
        rtt.add_all(list(self._rtt.values()))

        latency = MetricValue()
        latency.add_all(list(map(lambda x: x / 2, self._rtt.values())))

        metrics: dict[MetricName, MetricValue | float] = {
                MetricName.rtt: rtt,
                MetricName.latency_to: latency,
                MetricName.latency_from: latency,
                MetricName.packet_loss: self._packet_loss(),
                MetricName.jitter: rtt.maximum - rtt.minimum,
        }

        return [
            BaseMetricEntry(
                origin=self._origin_name,
                timestamp=datetime.now().timestamp(),
                destination=self._addr,
                metrics=metrics,
            )
        ]

    async def probe_loop(self):
        while not self._stop_event.is_set():

            packet_id = str(uuid4())
            started = datetime.now()

            try:
                async with connect(
                    self._addr,
                    self._port,
                    verify_mode=False
                ) as client:

                    stream_id = client._quic.get_next_available_stream_id()

                    writer = client._quic.get_stream_writer(stream_id)

                    writer.write(packet_id.encode())
                    await writer.drain()

                    data = await asyncio.wait_for(
                        client._quic.wait_connected(),
                        timeout=5
                    )

                    rtt = (datetime.now() - started).total_seconds()*1000

                    self._sent_packet.add(packet_id, started)
                    self._rtt.add(packet_id, rtt)

            except Exception as e:
                self._logger.warning(
                    "quic probe failed",
                    error=str(e)
                )

            await asyncio.sleep(
                self._packet_send_delay.total_seconds()
            )

    async def start_collector(self):
        asyncio.create_task(self.probe_loop())

    async def stop(self):
        self._stop_event.set()
