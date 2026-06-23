"""Utilities for decoding Sol-Ark fault bitmaps."""

from dataclasses import dataclass

from .const import FAULT_TABLE


@dataclass(frozen=True)
class DecodedFault:
    """Structured representation of a decoded fault from the Sol-Ark inverter."""

    code: str
    name: str
    description: str
    bit: int
    active: bool


def translate_fault_code_to_messages(fault_code: int) -> list[str]:
    """Translate a fault code into a list of human-readable fault messages.

    Args:
        fault_code: The integer fault code from the device.

    Returns:
        A list of fault message strings.
    """
    if fault_code == 0:
        return ["No Faults"]

    decoded_faults: dict[int, DecodedFault] = decode_fault_bitmap(fault_code)

    return [f"{fault.code} - {fault.description}" for fault in decoded_faults.values()]


def decode_fault_bitmap(bitmap: int) -> dict[int, DecodedFault]:
    """Convert 64-bit fault bitmap into a structured dictionary of active faults.

    Args:
        bitmap: 64-bit fault number from inverter (R103-R106 combined).

    Returns:
        Dictionary keyed by fault number with decoded fault details.
    """
    faults: dict[int, DecodedFault] = {}

    for bit in range(64):
        if bitmap & (1 << bit):
            fault_number = bit + 1

            if fault_number in FAULT_TABLE:
                code, name, description = FAULT_TABLE[fault_number]
            else:
                code = f"F{fault_number}"
                name = "Unknown_Fault"
                description = f"Unknown fault (bit {bit})"

            faults[fault_number] = DecodedFault(
                code=code,
                name=name,
                description=description,
                bit=bit,
                active=True,
            )

    return faults
