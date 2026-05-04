import asyncio
from modules.media.real import RealMediaModule

async def main():
    module = RealMediaModule()
    songs = await module.get_all_songs()
    print("SONGS:", songs)

asyncio.run(main())
