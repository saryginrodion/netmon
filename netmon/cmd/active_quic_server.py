import asyncio
import ipaddress
import tempfile
from datetime import datetime, timedelta, timezone

from cryptography import x509# type: ignore
from cryptography.hazmat.primitives import hashes, serialization# type: ignore
from cryptography.hazmat.primitives.asymmetric import rsa# type: ignore
from cryptography.x509.oid import NameOID# type: ignore

from aioquic.asyncio import serve# type: ignore
from aioquic.asyncio.protocol import QuicConnectionProtocol# type: ignore
from aioquic.quic.configuration import QuicConfiguration# type: ignore
from aioquic.quic.events import ConnectionTerminated, HandshakeCompleted, ProtocolNegotiated, QuicEvent, StreamDataReceived# type: ignore

HOST = "127.0.0.1"
PORT = 4433


def generate_self_signed_cert() -> tuple[str, str]:
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    subject = issuer = x509.Name(
        [
            x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Local"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "Localhost"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "QUIC Test"),
            x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
        ]
    )

    now = datetime.now(timezone.utc)
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - timedelta(minutes=1))
        .not_valid_after(now + timedelta(days=365))
        .add_extension(
            x509.SubjectAlternativeName(
                [
                    x509.DNSName("localhost"),
                    x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
                ]
            ),
            critical=False,
        )
        .sign(key, hashes.SHA256())
    )

    cert_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pem")
    key_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pem")

    cert_file.write(cert.public_bytes(serialization.Encoding.PEM))
    cert_file.close()

    key_file.write(
        key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        )
    )
    key_file.close()

    return cert_file.name, key_file.name


class EchoServerProtocol(QuicConnectionProtocol):
    def quic_event_received(self, event: QuicEvent) -> None:
        if isinstance(event, ProtocolNegotiated):
            print("[server] protocol negotiated", flush=True)
            return

        if isinstance(event, HandshakeCompleted):
            print("[server] handshake completed", flush=True)
            return

        if isinstance(event, StreamDataReceived):
            self._quic.send_stream_data(
                event.stream_id,
                event.data,
                end_stream=event.end_stream,
            )
            self.transmit()
            return

        if isinstance(event, ConnectionTerminated):
            print(
                f"[server] connection terminated: error_code={event.error_code}, reason={event.reason_phrase}",
                flush=True,
            )


async def main() -> None:
    cert_path, key_path = generate_self_signed_cert()

    configuration = QuicConfiguration(is_client=False)
    configuration.load_cert_chain(certfile=cert_path, keyfile=key_path)
    configuration.alpn_protocols = ["quic-echo"]
    configuration.max_datagram_frame_size = 65536

    print(f"[server] starting on {HOST}:{PORT}", flush=True)
    print(f"[server] cert: {cert_path}", flush=True)
    print(f"[server] key:  {key_path}", flush=True)

    await serve(
        HOST,
        PORT,
        configuration=configuration,
        create_protocol=EchoServerProtocol,
    )

    print(f"[server] listening on {HOST}:{PORT}", flush=True)
    await asyncio.Event().wait()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[server] stopped", flush=True)
