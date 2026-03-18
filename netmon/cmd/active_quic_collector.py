import asyncio
import time
from statistics import mean

from aioquic.asyncio import connect # type: ignore
from aioquic.asyncio.protocol import QuicConnectionProtocol# type: ignore
from aioquic.quic.configuration import QuicConfiguration# type: ignore
from aioquic.quic.events import ConnectionTerminated, HandshakeCompleted, ProtocolNegotiated, QuicEvent, StreamDataReceived# type: ignore

HOST = "127.0.0.1"
PORT = 4433
SEND_INTERVAL = 0.1
METRIC_INTERVAL = 5.0
CONNECT_TIMEOUT = 10.0
ALPN = "quic-echo"


class Metrics:
    def __init__(self) -> None:
        self.sent_times: dict[int, float] = {}
        self.rtts: list[float] = []
        self.total_sent = 0
        self.total_received = 0

    def packet_sent(self, msg_id: int) -> None:
        self.sent_times[msg_id] = time.perf_counter()
        self.total_sent += 1

    def packet_received(self, msg_id: int) -> None:
        sent_at = self.sent_times.pop(msg_id, None)
        if sent_at is None:
            return
        self.rtts.append(time.perf_counter() - sent_at)
        self.total_received += 1

    def print_window(self) -> None:
        sent_count = len(self.rtts) + len(self.sent_times)
        received_count = len(self.rtts)
        loss = ((sent_count - received_count) / sent_count * 100.0) if sent_count else 0.0
        last_rtt = self.rtts[-1] if self.rtts else 0.0
        avg_rtt = mean(self.rtts) if self.rtts else 0.0
        jitter = (max(self.rtts) - min(self.rtts)) if len(self.rtts) >= 2 else 0.0

        print("\n====== QUIC METRICS ======", flush=True)
        print(f"Window sent:      {sent_count}", flush=True)
        print(f"Window received:  {received_count}", flush=True)
        print(f"Last RTT:         {last_rtt * 1000:.2f} ms", flush=True)
        print(f"Average RTT:      {avg_rtt * 1000:.2f} ms", flush=True)
        print(f"Window loss:      {loss:.2f} %", flush=True)
        print(f"Jitter:           {jitter * 1000:.2f} ms", flush=True)
        print(f"Total sent:       {self.total_sent}", flush=True)
        print(f"Total received:   {self.total_received}", flush=True)

        self.rtts.clear()
        self.sent_times.clear()


class ClientProtocol(QuicConnectionProtocol):
    def __init__(self, *args, metrics: Metrics, connected_event: asyncio.Event, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.metrics = metrics
        self.connected_event = connected_event

    def quic_event_received(self, event: QuicEvent) -> None:
        if isinstance(event, ProtocolNegotiated):
            print("[client] protocol negotiated", flush=True)
            return

        if isinstance(event, HandshakeCompleted):
            print("[client] handshake completed", flush=True)
            self.connected_event.set()
            return

        if isinstance(event, StreamDataReceived):
            try:
                raw_id, _ = event.data.split(b"|", 1)
                self.metrics.packet_received(int(raw_id))
            except (ValueError, IndexError):
                pass
            return

        if isinstance(event, ConnectionTerminated):
            print(
                f"[client] connection terminated: error_code={event.error_code}, reason={event.reason_phrase}",
                flush=True,
            )


async def sender_loop(client: QuicConnectionProtocol, metrics: Metrics) -> None:
    message_id = 0
    window_started_at = time.perf_counter()

    while True:
        stream_id = client._quic.get_next_available_stream_id()
        payload = f"{message_id}|{time.time():.6f}".encode("utf-8")

        client._quic.send_stream_data(stream_id, payload, end_stream=True)
        client.transmit()
        metrics.packet_sent(message_id)
        message_id += 1

        now = time.perf_counter()
        if now - window_started_at >= METRIC_INTERVAL:
            metrics.print_window()
            window_started_at = now

        await asyncio.sleep(SEND_INTERVAL)


async def quic_client() -> None:
    configuration = QuicConfiguration(is_client=True)
    configuration.verify_mode = False
    configuration.alpn_protocols = [ALPN]
    configuration.max_datagram_frame_size = 65536

    metrics = Metrics()
    connected_event = asyncio.Event()

    print(f"[client] connecting to {HOST}:{PORT}", flush=True)

    async with connect(
        HOST,
        PORT,
        configuration=configuration,
        create_protocol=lambda *args, **kwargs: ClientProtocol(
            *args,
            metrics=metrics,
            connected_event=connected_event,
            **kwargs,
        ),
    ) as client:
        try:
            await asyncio.wait_for(connected_event.wait(), timeout=CONNECT_TIMEOUT)
        except asyncio.TimeoutError:
            raise TimeoutError(
                f"QUIC handshake timeout after {CONNECT_TIMEOUT:.0f} seconds. "
                "Проверь, что сервер запущен и firewall не режет UDP."
            )

        print(f"[client] connected to {HOST}:{PORT}", flush=True)
        await sender_loop(client, metrics)


if __name__ == "__main__":
    try:
        asyncio.run(quic_client())
    except KeyboardInterrupt:
        print("\n[client] stopped", flush=True)
    except Exception as exc:
        print(f"[client] error: {exc}", flush=True)
        raise
