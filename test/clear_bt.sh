#!/bin/bash
# ble_python_reset.sh - Setzt Bluetooth auf Zustand für Python App Pairing
# Einfach, direkt, zuverlässig
# Usage: sudo ./ble_python_reset.sh

echo "=================================================="
echo "   BLUETOOTH RESET für Python App Pairing"
echo "=================================================="
echo ""

# Nur Root
if [ "$EUID" -ne 0 ]; then
    echo "ERROR: Bitte mit sudo ausführen!"
    exit 1
fi

# 1. STOPPE ALLES
echo "[1/5] Stoppe Bluetooth..."
systemctl stop bluetooth
pkill -9 bluetoothd 2>/dev/null || true
sleep 2

# 2. LÖSCHE ALLES
echo "[2/5] Lösche alle Daten..."
rm -rf /var/lib/bluetooth/* 2>/dev/null || true
rm -rf /var/cache/bluetooth/* 2>/dev/null || true
sleep 1

# 3. HARDWARE RESET
echo "[3/5] Reset Hardware..."
hciconfig hci0 down 2>/dev/null || true
sleep 1
modprobe -r btusb bluetooth 2>/dev/null || true
sleep 1
modprobe btusb bluetooth 2>/dev/null || true
sleep 1
hciconfig hci0 up 2>/dev/null || true
sleep 1

# 4. BLUETOOTH NEU STARTEN (OHNE KONFIG)
echo "[4/5] Starte Bluetooth neu..."
systemctl start bluetooth
sleep 3

# 5. NICHTS KONFIGURIEREN! Python App macht alles selbst
echo "[5/5] Fertig. Keine weitere Konfiguration!"
echo ""
echo "=================================================="
echo "   SYSTEM IST BEREIT FÜR PYTHON APP"
echo "=================================================="
echo ""
echo "Nächste Schritte:"
echo "1. Python App starten: python main.py"
echo "2. Auf Nokia: 'Virtual Keyboard' suchen"
echo "3. Pairing sollte funktionieren"
echo ""
echo "WICHTIG: Keine bluetoothctl Befehle vorher ausführen!"
echo "         Die Python App konfiguriert alles selbst."
echo ""
