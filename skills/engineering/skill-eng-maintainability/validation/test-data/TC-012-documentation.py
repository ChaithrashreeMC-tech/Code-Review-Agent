# TC-012: Documentation and Contract Clarity (MAINT12)
# Demonstrates missing documentation on complex algorithms / misleading docstrings vs. clear contracts

import re

# --- VIOLATION ---
def parse_security_manifest(raw_token: str) -> dict:
    """
    VIOLATION:
    Misleading and contradictory docstring:
    'Takes a raw JSON token and returns the parsed payload dictionary.'
    In reality, it parses custom semicolon-delimited header-checksum bitmasks,
    fails silently on parity mismatch, and mutates input strings.
    Zero explanation of the complex regex or non-obvious bit-shift parity algorithm.
    """
    # Complex non-obvious regex with zero documentation
    pattern = re.compile(r"^SEC-(\d{4})-([A-Z]{2})\$([0-9a-f]{8})#(\d+)$")
    match = pattern.match(raw_token)
    if not match:
        raise ValueError("Invalid format")

    code, region, checksum, flags = match.groups()
    flag_int = int(flags)
    # Non-obvious bit shifting without explanation
    is_valid = ((flag_int >> 3) & 0x01) == 1 and (int(checksum, 16) ^ flag_int) % 7 == 0
    return {"region": region, "code": code, "authorized": is_valid}


# --- SAFE IMPLEMENTATION ---
def parse_security_manifest_safe(raw_token: str) -> dict:
    """
    Parses a hardware security token and verifies bit-level integrity flags.

    Args:
        raw_token: Formatted as 'SEC-<year>-<region>$<hex_checksum>#<flags>'.
                   Example: 'SEC-2024-US$0000abcd#15'

    Returns:
        dict containing 'region', 'code', and boolean 'authorized'.

    Notes:
        Authorization requires the third control bit to be set (flag_int >> 3)
        and the XOR checksum against flags modulo 7 to equal 0, matching
        spec RFC-8942 section 4.2.
    """
    pattern = re.compile(r"^SEC-(\d{4})-([A-Z]{2})\$([0-9a-f]{8})#(\d+)$")
    match = pattern.match(raw_token)
    if not match:
        raise ValueError(f"Malformed token: {raw_token}")

    code, region, checksum, flags = match.groups()
    flag_int = int(flags)
    is_valid = ((flag_int >> 3) & 0x01) == 1 and (int(checksum, 16) ^ flag_int) % 7 == 0
    return {"region": region, "code": code, "authorized": is_valid}

