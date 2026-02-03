#!/usr/bin/env python3
"""
Debug script to check if pairing agent is correctly exported on D-Bus.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from bluez_peripheral.util import get_message_bus


async def main():
    bus = await get_message_bus()
    
    print("=" * 70)
    print("Checking D-Bus exports...")
    print("=" * 70)
    
    # List all objects on the system bus
    introspection = await bus.introspect("org.freedesktop.DBus", "/org/freedesktop/DBus")
    proxy_object = bus.get_proxy_object("org.freedesktop.DBus", "/org/freedesktop/DBus", introspection)
    dbus_interface = proxy_object.get_interface("org.freedesktop.DBus")
    
    # Get all services
    services = await dbus_interface.call_list_names()
    print(f"\nServices containing 'wehrfritz':")
    for service in sorted(services):
        if 'wehrfritz' in service.lower() or 'equilibrium' in service.lower():
            print(f"  - {service}")
    
    # Try to introspect our agent path
    agent_path = "/me/wehrfritz/equilibrium/agent"
    print(f"\n" + "=" * 70)
    print(f"Checking agent at {agent_path}...")
    print("=" * 70)
    
    try:
        # Get all objects
        root_introspection = await bus.introspect("org.bluez", "/")
        root_object = bus.get_proxy_object("org.bluez", "/", root_introspection)
        object_manager = root_object.get_interface("org.freedesktop.DBus.ObjectManager")
        managed_objects = await object_manager.call_get_managed_objects()
        
        print(f"\nObjects managed by BlueZ:")
        for path in sorted(managed_objects.keys()):
            if 'agent' in path.lower():
                print(f"  - {path}")
                for interface in managed_objects[path]:
                    print(f"    - {interface}")
    
    except Exception as e:
        print(f"Error introspecting BlueZ: {e}")
    
    # Try introspecting the agent directly
    print(f"\nDirect introspection of {agent_path}:")
    try:
        introspection = await bus.introspect("org.bluez", agent_path)
        print(f"Success! Agent is exported.")
        
        # Parse the introspection XML
        from xml.etree import ElementTree as ET
        root = ET.fromstring(introspection)
        
        print(f"\nAgent interfaces and methods:")
        for iface in root.findall(".//interface"):
            iface_name = iface.get("name")
            print(f"\n  Interface: {iface_name}")
            
            for method in iface.findall(".//method"):
                method_name = method.get("name")
                args = [arg.get("name", "") for arg in method.findall("arg")]
                print(f"    - {method_name}({', '.join(args)})")
    
    except Exception as e:
        print(f"Error: {e}")
        print("Agent is NOT exported on D-Bus!")
    
    # Check BlueZ agents
    print(f"\n" + "=" * 70)
    print("Checking registered agents with BlueZ...")
    print("=" * 70)
    
    try:
        bluez_introspection = await bus.introspect("org.bluez", "/org/bluez")
        bluez_proxy = bus.get_proxy_object("org.bluez", "/org/bluez", bluez_introspection)
        agent_manager = bluez_proxy.get_interface("org.bluez.AgentManager1")
        
        # Try to call a method to check if it works
        print("AgentManager1 interface found!")
        
    except Exception as e:
        print(f"Error accessing AgentManager1: {e}")


if __name__ == "__main__":
    asyncio.run(main())
