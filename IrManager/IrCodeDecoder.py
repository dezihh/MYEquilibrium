"""
Multi-Strategy IR Code Decoder
Dekodiert rohe IR-Codes (Mikrosekunden-Arrays) in standardisierte Formate.

Ziel: Verbindliche, wiederholbare Aussagen über IR-Protokolle und Kommandos.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from enum import Enum


class IRProtocol(str, Enum):
    """Standardisierte IR-Protokolle"""
    NEC = "nec"
    EXTENDED_NEC = "nec_ext"
    JVC = "jvc"
    SONY_SIRC = "sony_sirc"
    RC5 = "rc5"
    RC6 = "rc6"
    DENON = "denon"
    SHARP = "sharp"
    UNKNOWN = "unknown"


@dataclass
class DecodedIRCode:
    """Struktur für dekodierte IR-Codes"""
    protocol: IRProtocol
    confidence: float  # 0.0-1.0
    raw_code: List[int]  # Original Mark/Space Array
    device_bits: int = 0  # Z.B. für NEC: Device ID
    command_bits: int = 0  # Z.B. für NEC: Command Code
    binary_str: Optional[str] = None  # Binäre Darstellung
    hex_str: Optional[str] = None  # Hex-Darstellung
    repeat_code: Optional[List[int]] = None  # Wiederholungs-Sequenz falls vorhanden
    details: Dict[str, Any] = None  # Protokoll-spezifische Details
    
    def __post_init__(self):
        if self.details is None:
            self.details = {}


class IRCodeDecoder:
    """
    Dekodiert rohe IR-Codes (Mark/Space Mikrosekunden).
    
    Strategie:
    1. Struktur-Analyse (Header, Bits)
    2. Protokoll-Erkennung
    3. Bits extrahieren (Device/Command)
    4. Validierung
    """
    
    TOLERANCE = 0.25  # ±25% Toleranz für Mark/Space Längen
    
    def decode(self, code: List[int]) -> DecodedIRCode:
        """
        Dekodiert einen IR-Code zu Protokoll + Daten.
        
        Args:
            code: Array von [mark1, space1, mark2, space2, ...]
            
        Returns:
            DecodedIRCode mit Protokoll, Device, Command
        """
        if not code or len(code) < 4:
            return DecodedIRCode(
                protocol=IRProtocol.UNKNOWN,
                confidence=0.0,
                raw_code=code
            )
        
        # Versuche verschiedene Protokolle (spezifisch zu generisch)
        candidates = [
            self._try_nec(code),
            self._try_extended_nec(code),
            self._try_jvc(code),
            self._try_sony(code),
            self._try_rc5(code),
            self._try_rc6(code),
        ]
        
        # Wähle beste Kandidat (mit Confidence > 0)
        valid = [c for c in candidates if c.confidence > 0]
        if valid:
            best = max(valid, key=lambda x: x.confidence)
            return best
        else:
            return DecodedIRCode(
                protocol=IRProtocol.UNKNOWN,
                confidence=0.0,
                raw_code=code
            )
    
    def _try_nec(self, code: List[int]) -> DecodedIRCode:
        """NEC: 9ms header, 4.5ms space, 32 bits, 560us marks"""
        if len(code) < 67:  # Header (2) + 32 bits (64) + end marker (1) = 67 minimum
            return DecodedIRCode(IRProtocol.NEC, 0.0, code)
        
        header_mark = code[0]
        header_space = code[1] if len(code) > 1 else 0
        
        # NEC Header: 9ms mark ± tolerance
        if not self._match_timing(header_mark, 9000, self.TOLERANCE):
            return DecodedIRCode(IRProtocol.NEC, 0.0, code)
        
        # NEC Header space: 4.5ms
        if not self._match_timing(header_space, 4500, self.TOLERANCE):
            return DecodedIRCode(IRProtocol.NEC, 0.0, code)
        
        # Dekodiere 32 Bits
        bits = self._extract_bits(code[2:], 560, 560, 1690)
        if len(bits) < 32:
            return DecodedIRCode(IRProtocol.NEC, 0.5, code)
        
        # NEC Format: Device (8 bits) + Device Inverse (8) + Command (8) + Command Inverse (8)
        device = bits[0:8]
        device_inv = bits[8:16]
        command = bits[16:24]
        command_inv = bits[24:32]
        
        device_val = self._bits_to_int(device)
        command_val = self._bits_to_int(command)
        
        # Validiere Inverse Bits
        device_check = (device_val ^ self._bits_to_int(device_inv)) == 0xFF
        command_check = (command_val ^ self._bits_to_int(command_inv)) == 0xFF
        
        confidence = 0.9 if (device_check and command_check) else 0.75
        
        return DecodedIRCode(
            protocol=IRProtocol.NEC,
            confidence=confidence,
            raw_code=code,
            device_bits=device_val,
            command_bits=command_val,
            binary_str=f"D:{device_val:08b} C:{command_val:08b}",
            hex_str=f"0x{device_val:02X}{command_val:02X}",
            details={
                "header_mark": header_mark,
                "header_space": header_space,
                "device": device_val,
                "command": command_val,
                "device_check_valid": device_check,
                "command_check_valid": command_check,
            }
        )
    
    def _try_extended_nec(self, code: List[int]) -> DecodedIRCode:
        """Extended NEC: Wie NEC aber ohne inverse Bits"""
        return DecodedIRCode(IRProtocol.EXTENDED_NEC, 0.0, code)
    
    def _try_jvc(self, code: List[int]) -> DecodedIRCode:
        """JVC: 8.4ms header, 4.2ms space"""
        if len(code) < 4:
            return DecodedIRCode(IRProtocol.JVC, 0.0, code)
        
        header_mark = code[0]
        header_space = code[1]
        
        if self._match_timing(header_mark, 8400, self.TOLERANCE) and \
           self._match_timing(header_space, 4200, self.TOLERANCE):
            return DecodedIRCode(IRProtocol.JVC, 0.7, code, details={"header": True})
        
        return DecodedIRCode(IRProtocol.JVC, 0.0, code)
    
    def _try_sony(self, code: List[int]) -> DecodedIRCode:
        """SONY SIRC: 2.4ms header, variable bit length"""
        return DecodedIRCode(IRProtocol.SONY_SIRC, 0.0, code)
    
    def _try_rc5(self, code: List[int]) -> DecodedIRCode:
        """RC5: Bi-phase encoding"""
        return DecodedIRCode(IRProtocol.RC5, 0.0, code)
    
    def _try_rc6(self, code: List[int]) -> DecodedIRCode:
        """RC6: Inverse bi-phase encoding"""
        return DecodedIRCode(IRProtocol.RC6, 0.0, code)
    
    def _match_timing(self, actual: int, expected: int, tolerance: float) -> bool:
        """Prüfe ob Timing im Toleranzbereich liegt"""
        margin = expected * tolerance
        return (expected - margin) <= actual <= (expected + margin)
    
    def _extract_bits(self, marks_spaces: List[int], short_mark: int, short_space: int, long_space: int) -> List[int]:
        """
        Extrahiere Bits aus Mark/Space Sequenz.
        Logik: lange space = 1, kurze space = 0
        """
        bits = []
        for i in range(1, len(marks_spaces), 2):
            if i >= len(marks_spaces):
                break
            space = marks_spaces[i]
            
            if self._match_timing(space, long_space, self.TOLERANCE):
                bits.append(1)
            elif self._match_timing(space, short_space, self.TOLERANCE):
                bits.append(0)
        
        return bits
    
    def _bits_to_int(self, bits: List[int]) -> int:
        """Konvertiere Bitarray zu Integer (LSB first)"""
        result = 0
        for i, bit in enumerate(bits):
            result |= (bit << i)
        return result


def to_flipper_zero_format(decoded: DecodedIRCode) -> str:
    """
    Konvertiere DecodedIRCode zu Flipper Zero .ir Format.
    
    Flipper Zero Format:
    ```
    Filetype: IR signals file
    Version: 1
    # 
    name: [command name]
    type: [protocol]
    frequency: 38000
    duty_cycle: 0.33
    data: [raw mark/space array]
    ```
    """
    protocol_map = {
        IRProtocol.NEC: "NEC",
        IRProtocol.EXTENDED_NEC: "NEC",
        IRProtocol.JVC: "JVC",
        IRProtocol.SONY_SIRC: "SONY",
        IRProtocol.RC5: "RC5",
        IRProtocol.RC6: "RC6",
    }
    
    proto_name = protocol_map.get(decoded.protocol, "RAW")
    
    # Flipper Zero erwartet Mark/Space als Komma-separierte Liste
    data_str = ",".join(str(x) for x in decoded.raw_code)
    
    ir_file = f"""Filetype: IR signals file
Version: 1
#
name: {decoded.hex_str or "Unknown"}
type: {proto_name}
frequency: 38000
duty_cycle: 0.33
data: {data_str}"""
    
    return ir_file


# Test
if __name__ == "__main__":
    # Moon-Code aus der DB
    moon_code = [9035, 4440, 611, 1633, 611, 515, 611, 515, 611, 515, 611, 515, 611, 515, 611, 515, 611, 515, 611, 515, 611, 1633, 611, 1633, 611, 1633, 611, 1633, 611, 1633, 611, 1633, 611, 1633, 611, 515, 611, 1633, 611, 1633, 611, 515, 611, 515, 611, 515, 611, 515, 611, 515, 611, 1633, 611, 515, 611, 515, 611, 1633, 611, 1633, 611, 1633, 611, 1633, 611, 1633, 611]
    
    decoder = IRCodeDecoder()
    result = decoder.decode(moon_code)
    
    print(f"Protocol: {result.protocol.value}")
    print(f"Confidence: {result.confidence}")
    print(f"Device: 0x{result.device_bits:02X}")
    print(f"Command: 0x{result.command_bits:02X}")
    print(f"Binary: {result.binary_str}")
    print(f"Hex: {result.hex_str}")
    print(f"Details: {result.details}")
    print("\nFlipper Zero Format:")
    print(to_flipper_zero_format(result))
