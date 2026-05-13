import asyncio


async def handle(reader, writer):
    data = await reader.read(1024)

    if data:
        writer.write(data)
        await writer.drain()

    writer.close()


async def run_quic_server(host="0.0.0.0", port=8003):
    server = await asyncio.start_server(
        handle,
        host,
        port
    )

    async with server:
        await server.serve_forever()