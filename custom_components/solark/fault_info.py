"""Utilities for decoding Sol-Ark fault bitmaps."""

from .const import FAULT_TABLE


def translate_fault_code_to_messages(fault_code: int) -> dict:
    """Translate a fault code into a list of human-readable fault messages.

    Args:
        fault_code: The integer fault code from the device.

    Returns:
        A list of fault message strings, or a string describing unknown faults.
    """
    messages = []

    if not fault_code:
        messages.append("No Faults")
        return messages

    # Decode into structured dictionary
    decoded_faults = decode_fault_bitmap(fault_code)

    return [
        f"{item['code']} - {item['description']}" for item in decoded_faults.values()
    ]


def decode_fault_bitmap(bitmap: int) -> dict[int, dict[str, object]]:
    """Convert 64-bit fault bitmap into a structured dictionary of active faults.

    Args:
        bitmap (int): 64-bit fault number from inverter (R103-R106 combined).

    Returns:
        dict[int, dict[str, object]]: Dictionary keyed by fault number with details:
            'code' (str), 'name' (str), 'description' (str), 'bit' (int), 'active' (bool)
    """
    faults: dict[int, dict[str, object]] = {}

    for bit in range(64):
        if bitmap & (1 << bit):
            fault_number = bit + 1
            if fault_number in FAULT_TABLE:
                code, name, description = FAULT_TABLE[fault_number]
            else:
                code, name, description = (
                    f"F{fault_number}",
                    "Unknown_Fault",
                    f"Unknown fault (bit {bit})",
                )

            faults[fault_number] = {
                "code": code,
                "name": name,
                "description": description,
                "bit": bit,
                "active": True,
            }

    return faults
