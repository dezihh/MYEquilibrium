import asyncio
from BleKeyboard.BleKeyboard import BleKeyboard

async def main():
    kb = await BleKeyboard.create()
    await kb.advertise()
    print("BleKeyboard Modul ist eigenständig aktiv.")
    while True:
        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main())
