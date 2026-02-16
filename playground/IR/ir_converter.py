#!/usr/bin/env python3
"""
Universal IR Konverter
Unterstützt: Remote Central, Flipper Zero, IRDB
Ausgabe: Flipper parsed oder Flipper raw (mit pyIRDecoder encoding)
Bitte das Repository pyIRDecode in das Arbeitsverzeichnis clonen "git clone https://github.com/kdschlosser/pyIRDecoder.git" und den sys.path entsprechend anpassen

"""

import sys
import argparse
import re
import csv
import io
import urllib.request
import urllib.error

# pyIRDecoder laden
try:
    sys.path.insert(0, '/home/dezi/dev/ir_arte/pyIRDecoder')
    import pyIRDecoder
    print("✓ pyIRDecoder geladen", file=sys.stderr)
except ImportError as e:
    print(f"✗ pyIRDecoder nicht gefunden: {e}", file=sys.stderr)
    print("  Installiere mit: git clone https://github.com/kdschlosser/pyIRDecoder.git ", file=sys.stderr)
    sys.exit(1)


# ============================================================================
# PROTOKOLL MAPPINGS
# ============================================================================

# Mapping von erkannten Protokollen zu Flipper Protokollen
PROTOCOL_MAP = {
    'NEC': 'NEC',
    'NEC_EXTENDED': 'NECext',
    'SAMSUNG': 'Samsung32',
    'SAMSUNG20': 'Samsung32', 
    'SAMSUNG36': 'Samsung32',
    'RC5': 'RC5',
    'RC6': 'RC6',
    'SONY12': 'SIRC',
    'SONY15': 'SIRC15',
    'SONY20': 'SIRC20',
    'JVC': 'JVC',
    'PANASONIC': 'Kaseikyo',
    'KASEIKYO': 'Kaseikyo',
}

# Flipper zu pyIRDecoder Protokoll Mapping
FLIPPER_TO_PYIR = {
    'NEC': 'NEC',
    'NECext': 'NECx',
    'Samsung32': 'Samsung36',
    'RC5': 'RC5',
    'RC6': 'RC6',
    'SIRC': 'Sony12',
    'SIRC15': 'Sony15',
    'SIRC20': 'Sony20',
    'JVC': 'JVC',
    'Kaseikyo': 'Kaseikyo',
}


# ============================================================================
# FORMAT DETECTION
# ============================================================================

def detect_file_format(content):
    """Erkennt das Dateiformat"""
    lines = content.strip().split('\n')
    
    # Flipper Format
    if any('type: parsed' in line or 'type: raw' in line for line in lines):
        return 'flipper'
    
    # Remote Central (Pronto Hex mit 4-stelligen Hex Werten)
    if any(re.match(r'^[0-9a-fA-F]{4}\s+[0-9a-fA-F]{4}', line) for line in lines):
        return 'remotecentral'
    
    # IRDB CSV Format
    if 'functionname,protocol,device' in lines[0]:
        return 'irdb'
    
    return 'unknown'


# ============================================================================
# REMOTE CENTRAL PARSER
# ============================================================================

def pronto_to_timings(pronto_hex):
    """Konvertiert Pronto Hex zu Timings"""
    try:
        parts = pronto_hex.split()
        if len(parts) < 4:
            return None
        freq_code = int(parts[1], 16)
        if freq_code == 0:
            frequency = 38000
        else:
            frequency = int(1000000 / (freq_code * 0.241246))
        seq1_len = int(parts[2], 16)
        seq2_len = int(parts[3], 16)
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


def parse_remotecentral(content):
    """Parst Remote Central Format"""
    entries = []
    lines = content.strip().split('\n')
    
    # Extrahiere Device Info aus Header
    device_brand = "Unknown"
    device_type = "Unknown"
    
    for line in lines:
        if 'RemoteCentral:' in line or '#RemoteCentral:' in line:
            parts = line.replace('#RemoteCentral:', '').replace('RemoteCentral:', '').strip().split(':')
            if len(parts) >= 2:
                device_brand = parts[0].strip()
                device_type = parts[1].strip()
            break
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Überspringe Header und Kommentare
        if line.startswith('#') or line.startswith('Filetype') or line.startswith('Version'):
            i += 1
            continue
        
        # Button Name (Zeile vor Pronto Code)
        if line and not re.match(r'^[0-9a-fA-F]{4}', line):
            button_name = line
            i += 1
            if i < len(lines):
                pronto_line = lines[i].strip()
                if re.match(r'^[0-9a-fA-F]{4}', pronto_line):
                    timings = pronto_to_timings(pronto_line)
                    if timings:
                        entries.append({
                            'format': 'remotecentral',
                            'name': button_name,
                            'timings': timings,
                            'device_brand': device_brand,
                            'device_type': device_type
                        })
        i += 1
    
    return entries


def parse_flipper(content):
    """Parst Flipper Format"""
    entries = []
    lines = content.strip().split('\n')
    
    device_brand = "Unknown"
    device_type = "Unknown"
    
    # Extrahiere Device Info
    for line in lines:
        if line.startswith('#Flipper:'):
            parts = line.replace('#Flipper:', '').split(':')
            if len(parts) >= 2:
                device_brand = parts[0].strip()
                device_type = parts[1].strip()
            break
    
    current_entry = None
    
    for line in lines:
        line = line.strip()
        
        if line.startswith('name:'):
            if current_entry:
                entries.append(current_entry)
            current_entry = {
                'format': 'flipper',
                'name': line.split(':', 1)[1].strip(),
                'device_brand': device_brand,
                'device_type': device_type
            }
        elif current_entry and ':' in line:
            key, value = line.split(':', 1)
            current_entry[key.strip()] = value.strip()
    
    if current_entry:
        entries.append(current_entry)
    
    return entries


# ============================================================================
# IRDB PARSER
# ============================================================================

def parse_irdb(content):
    """Parst IRDB CSV Format"""
    entries = []
    
    reader = csv.DictReader(io.StringIO(content))
    
    for row in reader:
        protocol = row.get('protocol', '').upper()
        device = int(row.get('device', 0))
        subdevice = int(row.get('subdevice', -1))
        function = int(row.get('function', 0))
        name = row.get('functionname', 'Unknown')
        
        entries.append({
            'format': 'irdb',
            'name': name,
            'protocol': protocol,
            'device': device,
            'subdevice': subdevice,
            'function': function,
            'device_brand': 'IRDB',
            'device_type': protocol
        })
    
    return entries


# ============================================================================
# PROTOKOLL DETECTION
# ============================================================================

def convert_to_rlc(timings):
    """Konvertiert Timings zu RLC Format für pyIRDecoder"""
    rlc = []
    for i, val in enumerate(timings):
        if i % 2 == 0:
            rlc.append(val)
        else:
            rlc.append(-val)
    
    # Stelle sicher dass abschließender Space vorhanden
    if len(timings) % 2 != 0:
        rlc.append(-40000)
    
    return rlc


def detect_protocol(rlc, frequency):
    """Versucht Protokoll mit pyIRDecoder zu erkennen"""
    
    # Teste wichtigste Protokolle direkt
    protocols_to_test = [
        ('NEC', pyIRDecoder.protocols.NEC),
        ('NECx', pyIRDecoder.protocols.NECx),
        ('Samsung36', pyIRDecoder.protocols.Samsung36),
        ('RC5', pyIRDecoder.protocols.RC5),
        ('RC6', pyIRDecoder.protocols.RC6),
        ('Sony12', pyIRDecoder.protocols.Sony12),
        ('Sony15', pyIRDecoder.protocols.Sony15),
        ('Sony20', pyIRDecoder.protocols.Sony20),
        ('JVC', pyIRDecoder.protocols.JVC),
        ('Kaseikyo', pyIRDecoder.protocols.Kaseikyo),
    ]
    
    for proto_name, protocol in protocols_to_test:
        try:
            code = protocol.decode(rlc, frequency)
            if code:
                # Hole Werte
                device = getattr(code, 'device', None)
                sub_device = getattr(code, 'sub_device', None)
                function = getattr(code, 'function', None)
                
                if device is not None and function is not None:
                    # Formatiere für Flipper
                    flipper_proto = PROTOCOL_MAP.get(proto_name, proto_name)
                    
                    # Formatiere Adresse
                    if sub_device is not None:
                        address = f"{device:02X} {sub_device:02X} 00 00"
                    else:
                        address = f"{device:04X} 00 00 00" if device > 255 else f"{device:02X} 00 00 00"
                    
                    command = f"{function:02X} 00 00 00"
                    
                    return {
                        'protocol': flipper_proto,
                        'address': address,
                        'command': command
                    }
        except:
            continue
    
    return None


# ============================================================================
# ENCODING (parsed → raw)
# ============================================================================

def encode_to_raw(protocol, address, command, frequency=38000):
    """
    Encodiert Flipper parsed zu raw Timings mit pyIRDecoder
    """
    
    # Mappe Flipper Protokoll zu pyIRDecoder
    pyir_proto_name = FLIPPER_TO_PYIR.get(protocol, protocol)
    
    try:
        # Hole Protokoll
        pyir_protocol = getattr(pyIRDecoder.protocols, pyir_proto_name, None)
        if not pyir_protocol:
            return None
        
        # Parse Adresse und Command
        addr_parts = address.split()
        cmd_parts = command.split()
        
        device = int(addr_parts[0], 16)
        sub_device = int(addr_parts[1], 16) if len(addr_parts) > 1 else 0
        func = int(cmd_parts[0], 16)
        
        # Encode
        params = {}
        
        # Protokoll-spezifische Parameter
        if 'NEC' in pyir_proto_name:
            params['device'] = device
            params['sub_device'] = sub_device
            params['function'] = func
        elif 'Samsung' in pyir_proto_name:
            params['device'] = device
            params['sub_device'] = sub_device
            params['function'] = func
        elif 'Sony' in pyir_proto_name:
            params['device'] = device
            params['function'] = func
        elif 'JVC' in pyir_proto_name:
            params['address'] = device
            params['command'] = func
        elif 'Kaseikyo' in pyir_proto_name:
            params["device"] = device
            params["sub_device"] = sub_device
            params["function"] = func
            params["extended_function"] = 0
            params["oem1"] = 0
            params["oem2"] = 0
        else:
            # Generisch
            params['device'] = device
            params['function'] = func
        
        # Encode mit pyIRDecoder
        code = pyir_protocol.encode(**params)
        
        if code and hasattr(code, 'original_rlc'):
            rlc = code.original_rlc
            # Konvertiere RLC zu positiven Timings
            timings = [abs(t) for t in rlc]
            freq = getattr(code, 'frequency', frequency)
            
            return {
                'frequency': freq,
                'values': timings
            }
    
    except Exception as e:
        print(f"  Encoding Fehler für {protocol}: {e}", file=sys.stderr)
        return None
    
    return None


# ============================================================================
# OUTPUT GENERATION
# ============================================================================

def generate_flipper_output(entry, output_format):
    """Generiert Flipper Ausgabe (parsed oder raw)"""
    
    output = []
    output.append("#")
    
    # Header
    fmt = entry.get('format')
    if fmt == 'remotecentral':
        output.append(f"# Quelle: RemoteCentral {entry['device_brand']}:{entry['device_type']}")
    elif fmt == 'flipper':
        output.append(f"# Quelle: Flipper {entry['device_brand']}:{entry['device_type']}")
    elif fmt == 'irdb':
        output.append(f"# Quelle: IRDB {entry['protocol']}")
    
    output.append("#")
    output.append(f"name: {entry['name']}")
    
    # Entscheide zwischen parsed und raw
    if output_format == 'raw':
        # IMMER raw ausgeben
        timings = None
        
        if fmt == 'remotecentral':
            # Haben bereits Timings
            timings = entry['timings']
        
        elif fmt == 'flipper':
            if entry.get('type') == 'raw':
                # Bereits raw
                output.append(f"type: raw")
                output.append(f"frequency: {entry.get('frequency', 38000)}")
                output.append(f"duty_cycle: {entry.get('duty_cycle', '0.330000')}")
                output.append(f"data: {entry.get('data', '')}")
                return "\n".join(output)
            else:
                # parsed → raw encodieren
                protocol = entry.get('protocol')
                address = entry.get('address')
                command = entry.get('command')
                
                if protocol and address and command:
                    encoded = encode_to_raw(protocol, address, command)
                    if encoded:
                        timings = encoded
        
        elif fmt == 'irdb':
            # IRDB → encode zu raw
            protocol = PROTOCOL_MAP.get(entry['protocol'], entry['protocol'])
            device = entry['device']
            subdevice = entry.get('subdevice', 0)
            function = entry['function']
            
            address = f"{device:02X} {subdevice:02X} 00 00" if subdevice >= 0 else f"{device:02X} 00 00 00"
            command = f"{function:02X} 00 00 00"
            
            encoded = encode_to_raw(protocol, address, command)
            if encoded:
                timings = encoded
        
        # Gib raw aus
        if timings:
            output.append("type: raw")
            output.append(f"frequency: {timings['frequency']}")
            output.append(f"duty_cycle: 0.330000")
            
            # Data in Zeilen zu max 200 Werten
            values = timings['values']
            data_str = " ".join(str(v) for v in values)
            output.append(f"data: {data_str}")
        else:
            output.append("# Konvertierung zu raw fehlgeschlagen")
            return None
    
    else:
        # parsed Format
        if fmt == 'remotecentral':
            # Versuche Protokoll zu erkennen
            rlc = convert_to_rlc(entry['timings']['values'])
            detected = detect_protocol(rlc, entry['timings']['frequency'])
            
            if detected:
                output.append("type: parsed")
                output.append(f"protocol: {detected['protocol']}")
                output.append(f"address: {detected['address']}")
                output.append(f"command: {detected['command']}")
            else:
                # Fallback zu raw
                output.append("type: raw")
                output.append(f"frequency: {entry['timings']['frequency']}")
                output.append(f"duty_cycle: 0.330000")
                data_str = " ".join(str(v) for v in entry['timings']['values'])
                output.append(f"data: {data_str}")
        
        elif fmt == 'flipper':
            # Gib parsed zurück wie es ist
            output.append(f"type: {entry.get('type', 'parsed')}")
            if 'protocol' in entry:
                output.append(f"protocol: {entry['protocol']}")
            if 'address' in entry:
                output.append(f"address: {entry['address']}")
            if 'command' in entry:
                output.append(f"command: {entry['command']}")
            if entry.get('type') == 'raw' and 'data' in entry:
                output.append(f"frequency: {entry.get('frequency', 38000)}")
                output.append(f"duty_cycle: {entry.get('duty_cycle', '0.330000')}")
                output.append(f"data: {entry['data']}")
        
        elif fmt == 'irdb':
            # IRDB → parsed
            protocol = PROTOCOL_MAP.get(entry['protocol'], entry['protocol'])
            device = entry['device']
            subdevice = entry.get('subdevice', -1)
            function = entry['function']
            
            output.append("type: parsed")
            output.append(f"protocol: {protocol}")
            
            if subdevice >= 0:
                output.append(f"address: {device:02X} {subdevice:02X} 00 00")
            else:
                output.append(f"address: {device:02X} FD 00 00")
            
            output.append(f"command: {function:02X} 00 00 00")
    
    return "\n".join(output)


# ============================================================================
# URL LOADING
# ============================================================================

def load_from_url(url):
    """Lädt Dateiinhalt von einer URL"""
    try:
        req = urllib.request.Request(
            url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        )
        with urllib.request.urlopen(req, timeout=30) as response:
            # Versuche UTF-8, fallback zu latin-1
            try:
                content = response.read().decode('utf-8')
            except UnicodeDecodeError:
                content = response.read().decode('latin-1')
            return content
    except urllib.error.HTTPError as e:
        print(f"✗ HTTP Fehler beim Laden der URL: {e.code} {e.reason}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"✗ URL Fehler: {e.reason}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"✗ Fehler beim Laden von URL: {e}", file=sys.stderr)
        sys.exit(1)


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Universal IR Konverter mit pyIRDecoder',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:
  %(prog)s -i input.ir -o output.ir                    # Auto, Flipper parsed
  %(prog)s -i input.ir -o output.ir -f raw             # Flipper raw (encodiert parsed→raw)
  %(prog)s -i remote.ir -o flipper.ir -f flipper       # Zu Flipper parsed
  %(prog)s --url https://example.com/remote.ir -o out.ir  # Von URL laden
  
Formate:
  flipper = Flipper parsed Format (type: parsed mit Protokoll)
  raw     = Flipper raw Format (type: raw mit Timings)
        """
    )
    
    # Input-Quellen (entweder Datei oder URL)
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('-i', '--input',
                        help='Eingabedatei')
    input_group.add_argument('--url',
                        help='URL zur Eingabedatei')
    
    parser.add_argument('-o', '--output',
                        help='Ausgabedatei (Standard: stdout)')
    parser.add_argument('-f', '--format', choices=['flipper', 'raw'],
                        default='flipper',
                        help='Ausgabeformat (flipper=parsed, raw=timings)')
    
    args = parser.parse_args()
    
    # Lese Input (Datei oder URL)
    try:
        if args.url:
            print(f"Lade von URL: {args.url}", file=sys.stderr)
            content = load_from_url(args.url)
        else:
            with open(args.input, 'r') as f:
                content = f.read()
    except Exception as e:
        source = args.url if args.url else args.input
        print(f"✗ Fehler beim Lesen von {source}: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Erkenne Format
    file_format = detect_file_format(content)
    print(f"Erkanntes Format: {file_format}", file=sys.stderr)
    
    if file_format == 'unknown':
        print("✗ Unbekanntes Dateiformat", file=sys.stderr)
        sys.exit(1)
    
    # Parse
    if file_format == 'remotecentral':
        entries = parse_remotecentral(content)
    elif file_format == 'flipper':
        entries = parse_flipper(content)
    elif file_format == 'irdb':
        entries = parse_irdb(content)
    else:
        entries = []
    
    print(f"Gefundene Einträge: {len(entries)}", file=sys.stderr)
    
    # Konvertiere
    output_lines = []
    output_lines.append("Filetype: IR signals file")
    output_lines.append("Version: 1")
    
    converted_count = 0
    for entry in entries:
        result = generate_flipper_output(entry, args.format)
        if result:
            output_lines.append(result)
            output_lines.append("")  # Leerzeile
            converted_count += 1
    
    print(f"Konvertiert: {converted_count} Einträge", file=sys.stderr)
    
    # Ausgabe
    result = "\n".join(output_lines)
    
    if args.output:
        try:
            with open(args.output, 'w') as f:
                f.write(result)
            print(f"✓ Geschrieben nach: {args.output}", file=sys.stderr)
        except Exception as e:
            print(f"✗ Fehler beim Schreiben: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(result)


if __name__ == '__main__':
    main()
