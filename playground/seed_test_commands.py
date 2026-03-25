#!/usr/bin/env python3
"""
Testdaten-Skript: Legt Dummy-Befehle für alle CommandGroupTypes an einem Gerät an.
Schreibt direkt in die SQLite-DB (config/database.db) – kein laufender Server nötig.

Aufruf:
  python playground/seed_test_commands.py [device_id]

  device_id: ID des Geräts (optional; Standard: erstes Gerät in der DB)
             Bei 0 oder fehlendem Gerät wird ein neues Testgerät erstellt.
"""

import sys
import os

# Projekt-Root ins sys.path damit die lokalen Module gefunden werden
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqlmodel import Session, select
from DbManager.DbManager import engine, create_db_and_tables
from Api.models.Command import Command
from Api.models.Device import Device

# Stelle sicher, dass Tabellen existieren
create_db_and_tables()

# Dummy IR-Code (kurze Mark/Space-Sequenz)
DUMMY_IR = [9024, 4512, 564, 564, 564, 1692, 564, 564, 564, 564]

# Alle Testbefehle: (name, command_group, type, button, extras)
TEST_COMMANDS = [
    # Power
    {"name": "Power Toggle", "command_group": "power",    "type": "ir", "button": "power_toggle"},
    {"name": "Power On",     "command_group": "power",    "type": "ir", "button": "power_on"},
    {"name": "Power Off",    "command_group": "power",    "type": "ir", "button": "power_off"},
    # Numeric
    {"name": "0",  "command_group": "numeric", "type": "ir", "button": "number_zero"},
    {"name": "1",  "command_group": "numeric", "type": "ir", "button": "number_one"},
    {"name": "2",  "command_group": "numeric", "type": "ir", "button": "number_two"},
    {"name": "3",  "command_group": "numeric", "type": "ir", "button": "number_three"},
    {"name": "4",  "command_group": "numeric", "type": "ir", "button": "number_four"},
    {"name": "5",  "command_group": "numeric", "type": "ir", "button": "number_five"},
    {"name": "6",  "command_group": "numeric", "type": "ir", "button": "number_six"},
    {"name": "7",  "command_group": "numeric", "type": "ir", "button": "number_seven"},
    {"name": "8",  "command_group": "numeric", "type": "ir", "button": "number_eight"},
    {"name": "9",  "command_group": "numeric", "type": "ir", "button": "number_nine"},
    # Volume
    {"name": "Vol+",  "command_group": "volume", "type": "ir", "button": "volume_up"},
    {"name": "Vol-",  "command_group": "volume", "type": "ir", "button": "volume_down"},
    {"name": "Mute",  "command_group": "volume", "type": "ir", "button": "mute"},
    # Navigation
    {"name": "Hoch",   "command_group": "navigation", "type": "ir", "button": "direction_up"},
    {"name": "Runter", "command_group": "navigation", "type": "ir", "button": "direction_down"},
    {"name": "Links",  "command_group": "navigation", "type": "ir", "button": "direction_left"},
    {"name": "Rechts", "command_group": "navigation", "type": "ir", "button": "direction_right"},
    {"name": "OK",     "command_group": "navigation", "type": "ir", "button": "select"},
    {"name": "Zurück", "command_group": "navigation", "type": "ir", "button": "back"},
    {"name": "Menü",   "command_group": "navigation", "type": "ir", "button": "menu"},
    {"name": "Home",   "command_group": "navigation", "type": "ir", "button": "home"},
    {"name": "Exit",   "command_group": "navigation", "type": "ir", "button": "exit"},
    # Channel
    {"name": "Kanal+", "command_group": "channel", "type": "ir", "button": "channel_up"},
    {"name": "Kanal-", "command_group": "channel", "type": "ir", "button": "channel_down"},
    # Transport
    {"name": "Play",         "command_group": "transport", "type": "ir", "button": "play"},
    {"name": "Pause",        "command_group": "transport", "type": "ir", "button": "pause"},
    {"name": "Stop",         "command_group": "transport", "type": "ir", "button": "stop"},
    {"name": "Vorspulen",    "command_group": "transport", "type": "ir", "button": "fast_forward"},
    {"name": "Zurückspulen", "command_group": "transport", "type": "ir", "button": "rewind"},
    {"name": "Nächster",     "command_group": "transport", "type": "ir", "button": "next_track"},
    {"name": "Vorheriger",   "command_group": "transport", "type": "ir", "button": "previous_track"},
    # Colored Buttons
    {"name": "Rot",   "command_group": "colored_buttons", "type": "ir", "button": "red"},
    {"name": "Grün",  "command_group": "colored_buttons", "type": "ir", "button": "green"},
    {"name": "Gelb",  "command_group": "colored_buttons", "type": "ir", "button": "yellow"},
    {"name": "Blau",  "command_group": "colored_buttons", "type": "ir", "button": "blue"},
    # Input
    {"name": "HDMI 1", "command_group": "input", "type": "ir", "button": "other"},
    # Other
    {"name": "Helligkeit+", "command_group": "other", "type": "ir", "button": "brightness_up"},
    {"name": "Helligkeit-", "command_group": "other", "type": "ir", "button": "brightness_down"},
]


def main():
    device_id_arg = int(sys.argv[1]) if len(sys.argv) > 1 else None

    with Session(engine) as session:
        # Gerät ermitteln / erstellen
        if device_id_arg:
            device = session.get(Device, device_id_arg)
            if not device:
                print(f"Gerät mit ID {device_id_arg} nicht gefunden.")
                sys.exit(1)
        else:
            device = session.exec(select(Device)).first()
            if not device:
                print("Kein Gerät in der DB gefunden – erstelle Testgerät 'Test-TV'…")
                device = Device(name="Test-TV", type="display", manufacturer="Acme", model="X9000")
                session.add(device)
                session.commit()
                session.refresh(device)
                print(f"  → Gerät erstellt: ID={device.id}")

        print(f"Füge Testbefehle für Gerät '{device.name}' (ID={device.id}) ein…")
        added = 0
        skipped = 0

        for spec in TEST_COMMANDS:
            # Doppelte vermeiden (gleicher button+device)
            existing = session.exec(
                select(Command).where(
                    Command.device_id == device.id,
                    Command.button == spec["button"],
                )
            ).first()
            if existing:
                skipped += 1
                continue

            cmd = Command(
                name=spec["name"],
                command_group=spec["command_group"],
                type=spec["type"],
                button=spec["button"],
                device_id=device.id,
                ir_action=DUMMY_IR,
            )
            session.add(cmd)
            added += 1

        session.commit()
        print(f"  → {added} Befehle eingefügt, {skipped} bereits vorhanden (übersprungen).")
        print("Fertig! Starte den Server neu falls er bereits läuft.")


if __name__ == "__main__":
    main()
