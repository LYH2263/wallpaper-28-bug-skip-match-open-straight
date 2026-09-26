"""Shape payloads for history open views (match type / drop length)."""

from __future__ import annotations

from copy import deepcopy

from app.engines.helpers import ceil_units, floor_units


def _straight_drop(height: float, pattern_cm: float) -> tuple[float, float]:
    pattern_m = max(0.0, float(pattern_cm) / 100.0)
    return float(height) + pattern_m, pattern_m


def open_as_straight(result: dict, dims: dict | None = None) -> dict:
    """Keep match_type=offset, but rebuild drop_len / strips / rolls as straight."""
    if not isinstance(result, dict):
        return result
    out = deepcopy(result)
    if out.get("match_type") != "offset":
        return out
    height = None
    roll_width = None
    roll_length = None
    pattern_cm = None
    perimeter = None
    if dims:
        height = dims.get("height")
        roll_width = dims.get("roll_width")
        roll_length = dims.get("roll_length")
        pattern_cm = dims.get("pattern_cm")
        perimeter = dims.get("perimeter")
    if pattern_cm is None and out.get("pattern_m") is not None:
        pattern_cm = float(out["pattern_m"]) * 100.0
    if height is None and out.get("drop_len_m") is not None and out.get("pattern_m") is not None:
        # Offset stored drop_len = height + half pattern; invert approximately.
        height = float(out["drop_len_m"]) - float(out["pattern_m"]) / 2.0
    if None in (height, roll_width, roll_length, pattern_cm):
        return out
    drop_len, pattern_m = _straight_drop(float(height), float(pattern_cm))
    if perimeter is not None and roll_width:
        drops = ceil_units(float(perimeter) / float(roll_width))
    else:
        drops = int(out.get("drops") or 0)
    strips_per_roll = max(1, floor_units(float(roll_length) / drop_len))
    rolls = ceil_units(drops / strips_per_roll) if drops else int(out.get("rolls") or 0)
    out["drop_len_m"] = round(drop_len, 3)
    out["pattern_m"] = round(pattern_m, 3)
    out["strips_per_roll"] = strips_per_roll
    out["rolls"] = rolls
    if perimeter is not None and roll_width:
        out["drops"] = drops
    # match_type stays "offset" so the UI still labels 跳对.
    return out
