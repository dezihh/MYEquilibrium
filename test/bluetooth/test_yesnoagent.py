#!/usr/bin/env python3
"""
Test YesNoAgent introspection.
"""

import asyncio
from bluez_peripheral.util import get_message_bus
from bluez_peripheral.agent import YesNoAgent


async def dummy_confirmation(passkey):
    print(f"Dummy confirmation called with passkey: {passkey}")
    return True


def dummy_cancel():
    print("Dummy cancel called")


async def main():
    bus = await get_message_bus()
    
    agent = YesNoAgent(dummy_confirmation, dummy_cancel)
    agent.export(bus, path="/test/yesnoagent")
    
    print("YesNoAgent exported at /test/yesnoagent")
    print("\nIntrospection:")
    
    try:
        introspection = await bus.introspect("org.freedesktop.DBus", "/test/yesnoagent")
        print(introspection[:500])
    except Exception as e:
        print(f"Error: {e}")
    
    # Try through dbus command
    print("\nWaiting 2 seconds... (check with: dbus-send --print-reply --session /test/yesnoagent org.freedesktop.DBus.Introspectable.Introspect)")
    await asyncio.sleep(2)
    
    agent.unexport()
    print("\nAgent unexported")


if __name__ == "__main__":
    asyncio.run(main())
