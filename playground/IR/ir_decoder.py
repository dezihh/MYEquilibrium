#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
IR SIGNAL DECODER - Infrarot-Signal-Dekodierung mit pyIRDecoder
═══════════════════════════════════════════════════════════════════════════════

BESCHREIBUNG:
    Dekodiert Infrarot-Signale (IR) mit über 160 Protokollen.
    Unterstützt Flipper Zero .ir Dateien, Pronto Hex Format und manuelle Eingabe.
    
UNTERSTÜTZTE PROTOKOLLE:
    NEC, Sony (SIRC), RC5, RC6, Samsung, Panasonic, Sharp, JVC, Denon,
    DirecTV, DishNetwork, Sky, Tivo, und 140+ weitere Protokolle
    
EINGABEFORMATE:
    - Flipper Zero .ir Dateien (type: raw mit data:)
    - Pronto Hex Format (z.B. "0000 006d 0000 0020 000a 001e...")
    - Manuelle Timing-Eingabe (komma-getrennte Werte)
    
VERWENDUNG:
    # Standard Test-Signal dekodieren
    ./ir_decoder.py
    
    # Flipper/Pronto Datei dekodieren
    ./ir_decoder.py --file signals.ir
    
    # Eigene Timings dekodieren
    ./ir_decoder.py --timings "9035,4440,611,1633,..."
    
    # Nur ein Protokoll testen
    ./ir_decoder.py --protocol NEC --file signals.ir
    
    # Alle Protokolle auflisten
    ./ir_decoder.py --list
    
AUSGABE:
    - Erkanntes Protokoll
    - Device/Sub-Device/Function Codes
    - Hexadezimale Darstellung
    - Zusätzliche Parameter (falls vorhanden)
    
AUTOR: IR Decoder Team
VERSION: 1.0
LIZENZ: MIT

═══════════════════════════════════════════════════════════════════════════════
"""

import sys
import os
import re
import argparse

# pyIRDecoder laden
sys.path.insert(0, os.path.expanduser('~/pyIRDecoder'))
sys.path.insert(0, '/home/dezi/dev/ir_arte/pyIRDecoder')

try:
    import pyIRDecoder
except ImportError:
    print("✗ pyIRDecoder nicht gefunden!", file=sys.stderr)
    print("  Installation: git clone https://github.com/kdschlosser/pyIRDecoder.git", file=sys.stderr)
    sys.exit(1)


# ═══════════════════════════════════════════════════════════════════════════
# HELPER FUNKTIONEN
# ═══════════════════════════════════════════════════════════════════════════

def convert_to_rlc(raw_timings):
    """
    Konvertiert Raw Timings zu RLC Format für pyIRDecoder
    
    Args:
        raw_timings: Liste von positiven Timing-Werten [mark, space, mark, space, ...]
        
    Returns:
        Liste im RLC Format [mark, -space, mark, -space, ...]
    """
    rlc_data = []
    for i, val in enumerate(raw_timings):
        if i % 2 == 0:
            rlc_data.append(val)       # Mark (positiv)
        else:
            rlc_data.append(-val)      # Space (negativ)
    
    # Stelle sicher dass ein abschließender Space vorhanden ist
    if len(raw_timings) % 2 != 0:
        rlc_data.append(-40000)
    
    return rlc_data


def decode_with_protocol(protocol, rlc_data, frequency):
    """
    Dekodiert Signal mit einem spezifischen Protokoll
    
    Args:
        protocol: pyIRDecoder Protokoll-Objekt
        rlc_data: Signal im RLC Format
        frequency: Trägerfrequenz in Hz
        
    Returns:
        Dictionary mit Dekodierungs-Ergebnis
    """
    try:
        code = protocol.decode(rlc_data, frequency)
        if code:
            return {
                'success': True,
                'device': getattr(code, 'device', None),
                'sub_device': getattr(code, 'sub_device', None),
                'function': getattr(code, 'function', None),
                'hexadecimal': getattr(code, 'hexadecimal', None),
                'code_object': code
            }
    except Exception as e:
        return {'success': False, 'error': str(e)}
    return {'success': False}


# ═══════════════════════════════════════════════════════════════════════════
# PROTOKOLL DETECTION
# ═══════════════════════════════════════════════════════════════════════════

def get_available_protocols():
    """
    Sammelt alle verfügbaren Protokolle aus pyIRDecoder
    
    Returns:
        Liste von Protokoll-Namen
    """
    import os
    
    protocol_names = []
    
    try:
        # Finde das Protokoll-Verzeichnis
        protocols_dir = os.path.join(os.path.dirname(pyIRDecoder.__file__), 'protocols')
        
        if not os.path.exists(protocols_dir):
            return []
        
        # Liste alle .py Dateien
        for filename in os.listdir(protocols_dir):
            if filename.endswith('.py') and not filename.startswith('_'):
                # Protokoll-Name aus Dateinamen ableiten
                proto_module = filename[:-3]  # Entferne .py
                
                # Konvertiere zu Klassenname (z.B. "nec" -> "NEC", "sony12" -> "Sony12")
                # Die meisten Protokolle haben die Klasse in UpperCase
                try:
                    # Versuche verschiedene Varianten
                    for variant in [
                        proto_module.upper(),  # NEC
                        proto_module,          # nec
                        proto_module.capitalize(),  # Nec
                        ''.join(word.capitalize() for word in proto_module.split('_'))  # Sony_12 -> Sony12
                    ]:
                        try:
                            proto_obj = getattr(pyIRDecoder.protocols, variant)
                            if hasattr(proto_obj, 'decode'):
                                protocol_names.append(variant)
                                break
                        except:
                            continue
                except:
                    pass
        
    except Exception as e:
        # Fallback: Versuche bekannte Protokolle direkt
        known_protocols = [
            'NEC', 'NECx', 'NEC48', 'Sony12', 'Sony15', 'Sony20',
            'RC5', 'RC6', 'Samsung36', 'JVC', 'Panasonic', 'Sharp'
        ]
        for proto in known_protocols:
            try:
                if hasattr(getattr(pyIRDecoder.protocols, proto), 'decode'):
                    protocol_names.append(proto)
            except:
                pass
    
    return protocol_names


def decode_all_protocols(raw_timings, frequency=38000):
    """
    Versucht alle verfügbaren Protokolle zu dekodieren
    
    Args:
        raw_timings: Liste von Timing-Werten
        frequency: Trägerfrequenz in Hz
        
    Returns:
        Liste von erfolgreichen Dekodierungen
    """
    rlc_data = convert_to_rlc(raw_timings)
    
    print("=" * 70)
    print("IR DECODER - pyIRDecoder mit 160+ Protokollen")
    print("=" * 70)
    print(f"\nRaw Timings: {len(raw_timings)} Werte")
    print(f"RLC Format: {len(rlc_data)} Werte")
    print(f"Frequenz: {frequency} Hz\n")
    
    # Sammle verfügbare Protokolle
    protocol_names = get_available_protocols()
    
    print(f"Verfügbare Protokolle: {len(protocol_names)}")
    print("-" * 70)
    
    if len(protocol_names) == 0:
        print("✗ FEHLER: Keine Protokolle gefunden!")
        print("  pyIRDecoder scheint nicht korrekt geladen zu sein.")
        return []
    
    # Teste alle Protokolle
    successful_decodes = []
    
    for proto_name in sorted(protocol_names):
        protocol = getattr(pyIRDecoder.protocols, proto_name)
        result = decode_with_protocol(protocol, rlc_data, frequency)
        
        if result['success']:
            print(f"✓ {proto_name:20} -> ERKANNT!")
            successful_decodes.append((proto_name, result))
    
    # Zeige Ergebnisse
    print()
    print("=" * 70)
    print(f"ERGEBNISSE: {len(successful_decodes)} Protokoll(e) erkannt")
    print("=" * 70)
    
    if successful_decodes:
        for proto_name, result in successful_decodes:
            print(f"\n✓✓✓ {proto_name} ✓✓✓")
            print(f"{'='*60}")
            
            if result['device'] is not None:
                print(f"  Device:       {result['device']}")
            if result['sub_device'] is not None:
                print(f"  Sub-Device:   {result['sub_device']}")
            if result['function'] is not None:
                print(f"  Function:     {result['function']}")
            if result['hexadecimal'] is not None:
                print(f"  Hexadecimal:  {result['hexadecimal']}")
            
            # Zeige weitere Attribute
            code = result['code_object']
            extra_attrs = []
            for attr in ['oem', 'oem1', 'oem2', 'toggle', 'mode', 'checksum']:
                val = getattr(code, attr, None)
                if val is not None:
                    extra_attrs.append(f"{attr}={val}")
            
            if extra_attrs:
                print(f"  Weitere:      {', '.join(extra_attrs)}")
    else:
        print("\n✗ Kein Protokoll konnte das Signal dekodieren")
        print("  Mögliche Gründe:")
        print("  - Signal unvollständig")
        print("  - Unbekanntes Protokoll")
        print("  - Timing-Fehler im Signal")
    
    print("\n" + "=" * 70)
    return successful_decodes


# ═══════════════════════════════════════════════════════════════════════════
# FILE PARSING
# ═══════════════════════════════════════════════════════════════════════════

def pronto_to_timings(pronto_hex):
    """
    Konvertiert Pronto Hex Code zu Timings
    
    Args:
        pronto_hex: Pronto Hex String (z.B. "0000 006d 0000 0020...")
        
    Returns:
        Dictionary mit 'frequency' und 'values' oder None
    """
    try:
        parts = pronto_hex.split()
        if len(parts) < 4:
            return None
        
        # Pronto Format: [0000] [freq_code] [seq1_len] [seq2_len] [data...]
        freq_code = int(parts[1], 16)
        frequency = 38000 if freq_code == 0 else int(1000000 / (freq_code * 0.241246))
        
        seq1_len = int(parts[2], 16)
        seq2_len = int(parts[3], 16)
        
        # Konvertiere Hex zu Timings
        timing_values = []
        total_bursts = seq1_len + seq2_len
        
        for hex_val in parts[4:4 + total_bursts]:
            if freq_code > 0:
                timing = int(int(hex_val, 16) * 1000000 / (freq_code * 0.241246))
            else:
                timing = int(hex_val, 16) * 26
            timing_values.append(timing)
        
        return {'frequency': frequency, 'values': timing_values}
    except:
        return None


def download_from_url(url):
    """
    Lädt Datei von URL herunter
    
    Args:
        url: URL zur .ir Datei
        
    Returns:
        Dateiinhalt als String
    """
    import urllib.request
    
    try:
        print(f"Lade von URL: {url}", file=sys.stderr)
        with urllib.request.urlopen(url, timeout=10) as response:
            content = response.read().decode('utf-8')
        print(f"✓ {len(content)} Bytes geladen", file=sys.stderr)
        return content
    except Exception as e:
        raise Exception(f"Fehler beim Laden von URL: {e}")


def parse_flipper_ir_file(filename_or_content, from_url=False):
    """
    Parst Flipper .ir Datei und Pronto Hex Dateien
    
    Args:
        filename_or_content: Pfad zur .ir Datei oder Dateiinhalt (bei from_url=True)
        from_url: True wenn filename_or_content bereits der Dateiinhalt ist
        
    Returns:
        Liste von Dictionaries mit 'name', 'timings', 'frequency'
    """
    signals = []
    
    if from_url:
        # Inhalt wurde bereits geladen
        lines = filename_or_content.split('\n')
    else:
        # Datei von Disk lesen
        with open(filename_or_content, 'r') as f:
            lines = f.readlines()
    
    current_signal = {}
    
    for line in lines:
        line_stripped = line.strip() if isinstance(line, str) else line
        
        # Flipper Format: name:
        if line_stripped.startswith('name:'):
            if current_signal and 'timings' in current_signal:
                signals.append(current_signal)
            current_signal = {'name': line_stripped.split(':', 1)[1].strip()}
        
        # Flipper Format: type:
        elif line_stripped.startswith('type:'):
            current_signal['type'] = line_stripped.split(':', 1)[1].strip()
        
        # Flipper Format: frequency:
        elif line_stripped.startswith('frequency:'):
            current_signal['frequency'] = int(line_stripped.split(':', 1)[1].strip())
        
        # Flipper Format: data:
        elif line_stripped.startswith('data:'):
            data_str = line_stripped.split(':', 1)[1].strip()
            current_signal['timings'] = [int(x) for x in data_str.split()]
        
        # Pronto Hex Format
        elif re.match(r'^[0-9a-fA-F]{4}\s+[0-9a-fA-F]{4}', line_stripped):
            pronto_data = pronto_to_timings(line_stripped)
            if pronto_data and current_signal:
                current_signal['timings'] = pronto_data['values']
                current_signal['frequency'] = pronto_data['frequency']
                current_signal['type'] = 'raw'
        
        # Button Name (Zeile ohne Marker)
        elif (line_stripped and 
              not line_stripped.startswith('#') and
              not line_stripped.startswith('Filetype') and
              not line_stripped.startswith('Version') and
              ':' not in line_stripped and
              not re.match(r'^[0-9a-fA-F]{4}', line_stripped)):
            if current_signal and 'timings' in current_signal:
                signals.append(current_signal)
            current_signal = {'name': line_stripped}
    
    # Letztes Signal
    if current_signal and 'timings' in current_signal:
        signals.append(current_signal)
    
    return signals


def parse_timing_input(timing_str):
    """
    Parst manuellen Timing-String
    
    Args:
        timing_str: Komma-getrennte Timings "9035,4440,..."
        
    Returns:
        Liste von Integer-Werten
    """
    timing_str = timing_str.strip('[]')
    values = []
    for val in timing_str.split(','):
        val = val.strip()
        if val:
            values.append(int(val))
    return values


# ═══════════════════════════════════════════════════════════════════════════
# PROTOCOL LISTING
# ═══════════════════════════════════════════════════════════════════════════

def list_all_protocols():
    """Listet alle verfügbaren Protokolle kategorisiert auf"""
    protocol_names = get_available_protocols()
    
    print("=" * 70)
    print(f"VERFÜGBARE PROTOKOLLE: {len(protocol_names)}")
    print("=" * 70)
    
    categories = {
        'NEC': [], 'Sony': [], 'RC': [], 'Samsung': [],
        'Panasonic': [], 'Sharp': [], 'JVC': [], 'Denon': [],
        'TV/STB': [], 'Andere': []
    }
    
    for name in sorted(protocol_names):
        if 'NEC' in name:
            categories['NEC'].append(name)
        elif 'Sony' in name.lower():
            categories['Sony'].append(name)
        elif name.startswith('RC'):
            categories['RC'].append(name)
        elif 'Samsung' in name:
            categories['Samsung'].append(name)
        elif 'Panasonic' in name:
            categories['Panasonic'].append(name)
        elif 'Sharp' in name:
            categories['Sharp'].append(name)
        elif 'JVC' in name:
            categories['JVC'].append(name)
        elif 'Denon' in name:
            categories['Denon'].append(name)
        elif any(x in name for x in ['DirecTV', 'Dish', 'Sky', 'Tivo']):
            categories['TV/STB'].append(name)
        else:
            categories['Andere'].append(name)
    
    for category, protocols in categories.items():
        if protocols:
            print(f"\n{category} ({len(protocols)}):")
            for i, proto in enumerate(protocols):
                print(f"  {proto}", end="")
                if (i + 1) % 3 == 0:
                    print()
                else:
                    print("", end="  ")
            print()
    
    print("\n" + "=" * 70)


# ═══════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════

def main():
    """Hauptprogramm"""
    
    parser = argparse.ArgumentParser(
        description='IR Signal Decoder mit pyIRDecoder (160+ Protokolle)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:
  %(prog)s                                      # Test-Signal dekodieren
  %(prog)s --list                               # Alle Protokolle auflisten
  %(prog)s --file signals.ir                    # Lokale Datei dekodieren
  %(prog)s --url https://example.com/remote.ir  # Datei von URL laden
  %(prog)s --timings "9035,4440,611,..."        # Manuelle Timings
  %(prog)s --file signals.ir --protocol NEC     # Nur NEC testen
  %(prog)s --frequency 36000                    # Andere Frequenz
        """
    )
    
    parser.add_argument('--list', action='store_true',
                        help='Listet alle verfügbaren Protokolle auf')
    parser.add_argument('-t', '--timings',
                        help='Raw IR Timings (komma-getrennt)')
    parser.add_argument('-i', '--file',
                        help='Lokale Flipper .ir Datei oder Pronto Hex Datei')
    parser.add_argument('-u', '--url',
                        help='URL zu .ir Datei (lädt Datei aus dem Web)')
    parser.add_argument('-f', '--frequency', type=int, default=38000,
                        help='Trägerfrequenz in Hz (Standard: 38000)')
    parser.add_argument('-p', '--protocol',
                        help='Nur spezifisches Protokoll testen')
    
    args = parser.parse_args()
    
    # Liste Protokolle
    if args.list:
        list_all_protocols()
        return
    
    # Sammle Signale zum Dekodieren
    signals_to_decode = []
    
    if args.url:
        # Von URL laden
        try:
            content = download_from_url(args.url)
            signals = parse_flipper_ir_file(content, from_url=True)
            if not signals:
                print(f"✗ Keine Signale in URL gefunden", file=sys.stderr)
                sys.exit(1)
            
            print(f"URL geladen: {len(signals)} Signal(e)", file=sys.stderr)
            for sig in signals:
                signals_to_decode.append({
                    'name': sig['name'],
                    'timings': sig['timings'],
                    'frequency': sig.get('frequency', args.frequency)
                })
        except Exception as e:
            print(f"✗ Fehler beim Laden von URL: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            sys.exit(1)
    
    elif args.file:
        # Datei laden
        try:
            signals = parse_flipper_ir_file(args.file)
            if not signals:
                print(f"✗ Keine Signale in {args.file} gefunden", file=sys.stderr)
                sys.exit(1)
            
            print(f"Datei geladen: {len(signals)} Signal(e)", file=sys.stderr)
            for sig in signals:
                signals_to_decode.append({
                    'name': sig['name'],
                    'timings': sig['timings'],
                    'frequency': sig.get('frequency', args.frequency)
                })
        except Exception as e:
            print(f"✗ Fehler beim Laden: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            sys.exit(1)
    
    elif args.timings:
        # Manuelle Timings
        try:
            test_timing = parse_timing_input(args.timings)
            signals_to_decode.append({
                'name': 'Manual Input',
                'timings': test_timing,
                'frequency': args.frequency
            })
        except Exception as e:
            print(f"✗ Fehler beim Parsen: {e}", file=sys.stderr)
            sys.exit(1)
    
    else:
        # Test-Signal (NEC)
        test_timing = [
            9035, 4440, 611, 1633, 611, 515, 611, 515, 611, 515, 611, 515, 611, 515, 
            611, 515, 611, 515, 611, 515, 611, 1633, 611, 1633, 611, 1633, 611, 1633, 
            611, 1633, 611, 1633, 611, 1633, 611, 515, 611, 1633, 611, 1633, 611, 515, 
            611, 515, 611, 515, 611, 515, 611, 515, 611, 1633, 611, 515, 611, 515, 
            611, 1633, 611, 1633, 611, 1633, 611, 1633, 611, 1633, 611
        ]
        print("Test-Signal (NEC)", file=sys.stderr)
        signals_to_decode.append({
            'name': 'Test Signal',
            'timings': test_timing,
            'frequency': args.frequency
        })
    
    # Dekodiere alle Signale
    for idx, signal in enumerate(signals_to_decode):
        if len(signals_to_decode) > 1:
            print("\n" + "=" * 70)
            print(f"SIGNAL {idx + 1}/{len(signals_to_decode)}: {signal['name']}")
            print("=" * 70)
        
        if args.protocol:
            # Nur ein Protokoll testen
            try:
                protocol = getattr(pyIRDecoder.protocols, args.protocol)
            except AttributeError:
                print(f"✗ Protokoll '{args.protocol}' nicht gefunden", file=sys.stderr)
                print(f"  Nutze --list für verfügbare Protokolle", file=sys.stderr)
                sys.exit(1)
            
            rlc_data = convert_to_rlc(signal['timings'])
            result = decode_with_protocol(protocol, rlc_data, signal['frequency'])
            
            if result['success']:
                print(f"\n✓✓✓ {args.protocol} ERKANNT! ✓✓✓\n")
                if result['device'] is not None:
                    print(f"  Device:       {result['device']}")
                if result['sub_device'] is not None:
                    print(f"  Sub-Device:   {result['sub_device']}")
                if result['function'] is not None:
                    print(f"  Function:     {result['function']}")
                if result['hexadecimal'] is not None:
                    print(f"  Hexadecimal:  {result['hexadecimal']}")
            else:
                print(f"\n✗ {args.protocol} konnte Signal nicht dekodieren")
                if 'error' in result:
                    print(f"  Fehler: {result['error']}")
        else:
            # Alle Protokolle testen
            decode_all_protocols(signal['timings'], signal['frequency'])


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nAbgebrochen.", file=sys.stderr)
    except Exception as e:
        print(f"\n✗ Fehler: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
