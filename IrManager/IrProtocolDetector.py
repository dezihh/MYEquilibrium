from __future__ import annotations

from typing import Any, Dict, List, Tuple


def _approx(value: float, target: float, tolerance: float = 0.25) -> bool:
    return target * (1 - tolerance) <= value <= target * (1 + tolerance)


def _match_ratio(values: List[float], target: float, tolerance: float = 0.25) -> float:
    if not values:
        return 0.0
    matches = sum(1 for v in values if _approx(v, target, tolerance))
    return matches / len(values)


def _split_pairs(code: List[int]) -> Tuple[List[int], List[int]]:
    marks = code[0::2]
    spaces = code[1::2]
    return marks, spaces


def detect_protocol(code: List[int]) -> Dict[str, Any]:
    """
    Best-effort IR protocol detection based on mark/space timing array.

    Returns a dict with:
    - protocol: str
    - confidence: float (0..1)
    - details: dict (diagnostics)
    """
    if not code or len(code) < 4:
        return {"protocol": "unknown", "confidence": 0.0, "details": {"reason": "code too short"}}

    header_mark = code[0]
    header_space = code[1]

    marks, spaces = _split_pairs(code[2:])

    details: Dict[str, Any] = {
        "header_mark": header_mark,
        "header_space": header_space,
        "length": len(code),
    }

    # NEC (9ms + 4.5ms, 560us marks, 560/1690us spaces)
    if _approx(header_mark, 9000, 0.2) and _approx(header_space, 4500, 0.25):
        mark_ratio = _match_ratio(marks, 560, 0.35)
        space0_ratio = _match_ratio(spaces, 560, 0.35)
        space1_ratio = _match_ratio(spaces, 1690, 0.35)
        confidence = min(1.0, (mark_ratio + max(space0_ratio, space1_ratio)) / 2.0)
        details.update({
            "mark_ratio": mark_ratio,
            "space0_ratio": space0_ratio,
            "space1_ratio": space1_ratio,
        })
        return {"protocol": "NEC", "confidence": confidence, "details": details}

    # NEC repeat (9ms + 2.25ms + 560us)
    if _approx(header_mark, 9000, 0.2) and _approx(header_space, 2250, 0.3):
        return {"protocol": "NEC_REPEAT", "confidence": 0.8, "details": details}

    # JVC (8ms + 4ms, 560us marks, 560/1690us spaces)
    if _approx(header_mark, 8000, 0.2) and _approx(header_space, 4000, 0.25):
        mark_ratio = _match_ratio(marks, 560, 0.35)
        space0_ratio = _match_ratio(spaces, 560, 0.35)
        space1_ratio = _match_ratio(spaces, 1690, 0.35)
        confidence = min(1.0, (mark_ratio + max(space0_ratio, space1_ratio)) / 2.0)
        details.update({
            "mark_ratio": mark_ratio,
            "space0_ratio": space0_ratio,
            "space1_ratio": space1_ratio,
        })
        return {"protocol": "JVC", "confidence": confidence, "details": details}

    # SONY SIRC (2.4ms + 0.6ms, marks 0.6/1.2ms, spaces ~0.6ms)
    if _approx(header_mark, 2400, 0.25) and _approx(header_space, 600, 0.3):
        mark_ratio_600 = _match_ratio(marks, 600, 0.35)
        mark_ratio_1200 = _match_ratio(marks, 1200, 0.35)
        space_ratio = _match_ratio(spaces, 600, 0.35)
        confidence = min(1.0, (max(mark_ratio_600, mark_ratio_1200) + space_ratio) / 2.0)
        details.update({
            "mark_ratio_600": mark_ratio_600,
            "mark_ratio_1200": mark_ratio_1200,
            "space_ratio": space_ratio,
        })
        return {"protocol": "SONY_SIRC", "confidence": confidence, "details": details}

    # RC5/RC6 (bi-phase, ~889us unit; RC6 header ~2666us)
    if _approx(header_mark, 2666, 0.35) or _approx(header_mark, 889, 0.35):
        return {"protocol": "RC5/RC6", "confidence": 0.5, "details": details}

    # Denon/Sharp (heuristic; header ~3200/1600, marks ~400, spaces ~400/1200)
    if _approx(header_mark, 3200, 0.3) and _approx(header_space, 1600, 0.3):
        mark_ratio = _match_ratio(marks, 400, 0.4)
        space0_ratio = _match_ratio(spaces, 400, 0.4)
        space1_ratio = _match_ratio(spaces, 1200, 0.4)
        confidence = min(1.0, (mark_ratio + max(space0_ratio, space1_ratio)) / 2.0)
        details.update({
            "mark_ratio": mark_ratio,
            "space0_ratio": space0_ratio,
            "space1_ratio": space1_ratio,
        })
        return {"protocol": "DENON/SHARP", "confidence": confidence, "details": details}

    return {"protocol": "unknown", "confidence": 0.0, "details": details}
