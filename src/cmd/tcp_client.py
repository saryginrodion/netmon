import asyncio


async def main() -> None:
    reader, writer = await asyncio.open_connection("127.0.0.1", 8001)
    
    while True:
        pass

if __name__ == "__main__":
    asyncio.run(main())
