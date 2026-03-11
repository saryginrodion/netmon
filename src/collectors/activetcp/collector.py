import asyncio
from collections.abc import Iterable
from datetime import datetime, timedelta
from typing import override
from uuid import uuid4

import msgpack
from structlog.stdlib import BoundLogger

from collectors.activetcp.message import TCPMessage
from collectors.interface import MetricsCollector
from entities.base_metric_entry import BaseMetricEntry


class ActiveTCPCollector(MetricsCollector):
    def __init__(
        self,
        logger: BoundLogger,
        addr: str,
        port: int,
        metrics_interval: timedelta,
        packet_send_delay: timedelta = timedelta(seconds=5),
        reconnect_interval: timedelta = timedelta(seconds=15),
        read_timeout: timedelta = timedelta(seconds=10),
        write_timeout: timedelta = timedelta(seconds=10),
    ) -> None:
        self._logger = logger
        self._metrics_interval = metrics_interval
        self._reconnect_delay = reconnect_interval
        self._addr = addr
        self._port = port
        self._packet_send_delay = packet_send_delay
        self._read_timeout = read_timeout
        self._write_timeout = write_timeout

        self._stop_event = asyncio.Event()
        self._is_running = False

    @override
    async def collect(self, time: datetime) -> Iterable[BaseMetricEntry]:
        return await super().collect(time)

    async def handle_received_packet(self, packet: dict) -> None:
        """Обработка входящего пакета"""
        self._logger.debug("Received packet", packet=packet)

    async def send_messages_loop(self, writer: asyncio.StreamWriter) -> None:
        """Цикл отправки сообщений"""
        log = self._logger.bind(action="send_messages_loop")
        while not self._stop_event.is_set():
            msg: TCPMessage = {
                "message_id": str(uuid4()),
                "reply_to": None,
                "sent_at": datetime.now().timestamp(),
                "additioinal_data": None,
            }

            try:
                packed: bytes = msgpack.packb(msg)  # type: ignore
                writer.write(packed)
                await asyncio.wait_for(writer.drain(), self._write_timeout.total_seconds())

                log.info("Sent TCP message", message_id=msg["message_id"])
            except Exception as e:
                log.exception("Failed to send message", error=e)
                raise e

            await asyncio.sleep(self._packet_send_delay.total_seconds())

    async def receiving_messages_loop(self, reader: asyncio.StreamReader) -> None:
        """Цикл приёма сообщений через msgpack.Unpacker"""
        log = self._logger.bind(action="receiving_messages_loop")
        unpacker = msgpack.Unpacker(raw=False)

        while not self._stop_event.is_set():
            try:
                data = await asyncio.wait_for(reader.read(4096), self._read_timeout.total_seconds())
                if not data:
                    raise ConnectionError("reader is EOF")

                unpacker.feed(data)

                for packet in unpacker:
                    await self.handle_received_packet(packet)

            except Exception as e:
                log.error("Error receiving message", error=e)
                raise e

    async def _run_one_connection(self) -> None:
        log = self._logger.bind(action="_run_one_connection")
        try:
            log.info("Attempting to connect")
            self._stop_event = asyncio.Event()
            reader, writer = await asyncio.open_connection(self._addr, self._port)
            log.info("Connected to TCP server", addr=self._addr, port=self._port)
        except Exception as e:
            log.warning("Connection attempt failed", error=str(e))
            await asyncio.sleep(self._reconnect_delay.total_seconds())

        send_task = asyncio.create_task(self.send_messages_loop(writer))
        recv_task = asyncio.create_task(self.receiving_messages_loop(reader))

        try:
            await asyncio.gather(send_task, recv_task)
        except Exception as e:
            log.warning("gather failed", error=e)
            raise e
        finally:
            send_task.cancel()
            recv_task.cancel()
            self._stop_event.set()
            writer.close()
            await writer.wait_closed()

    async def run_collector(self) -> None:
        """Создание подключения и запуск циклов отправки и приёма"""
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
