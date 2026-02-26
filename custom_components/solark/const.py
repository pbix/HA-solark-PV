"""Constants."""

from __future__ import annotations

DOMAIN = "solark_modbus"
DEFAULT_NAME = "SolArk"
DEFAULT_HOST = "localhost"
DEFAULT_SCAN_INTERVAL: int = 20
DEFAULT_PORT: int = 502
ATTR_MANUFACTURER = "SolArk"
DEFAULT_DEVICE_ID: int = 1
DEFAULT_MAX_STALE_DATA_AGE: int = 300  # 5 minutes


# Define FAULT_TABLE as dict[int, tuple[str, str, str]]
FAULT_TABLE: dict[int, tuple[str, str, str]] = {
    1: ("F1", "DC_Inversed_Failure", "Parallel unit off — notification, not a fault."),
    8: ("F8", "GFDI_Relay_Failure", "Check continuity on inverter neutral and ground; single neutral-to-ground bond."),
    13: ("F13", "Grid_Mode_change", "Grid/battery mode change — informational, not a fault."),
    14: ("F14", "DC_OverCurr_Failure", "High DC current; check loads and PV input."),
    15: ("F15", "AC_OverCurr_Failure", "AC load too large or battery discharge amps too low; reduce loads."),
    16: ("F16", "GFCI_Failure", "Ground fault circuit interrupter failure; check PV wiring and grounding."),
    18: ("F18", "Tz_AC_OverCurr_Fault", "AC overload or generator overload; inspect AC wiring and loads."),
    20: ("F20", "Tz_Dc_OverCurr_Fault", "DC current too high — excess PV or battery current."),
    22: ("F22", "Tz_EmergStop_Fault", "Emergency stop signal detected; verify stops/sensors."),
    23: ("F23", "Tz_GFCI_OC_Fault", "GFCI/PV overcurrent fault; check PV conductor insulation."),
    24: ("F24", "DC_Insulation_Fault", "PV insulation failure (moisture/exposed conductor)."),
    25: ("F25", "DC_Feedback_Fault", "No battery connected but 'Activate Battery' enabled."),
    26: ("F26", "BusUnbalance_Fault", "Uneven AC leg load or DC on AC output when off-grid."),
    29: ("F29", "Parallel_CANBus_Fault", "Parallel system communication error; check comm cables/MODBUS IDs."),
    30: ("F30", "AC_MainContactor_Fault", "AC main contactor fault — service contactor hardware."),
    31: ("F31", "Soft_Start_Failed", "Soft start of large motor failed; inspect load startup current."),
    34: ("F34", "AC_Overload_Fault", "AC overload/short; reduce heavy or faulty loads."),
    35: ("F35", "AC_NoUtility_Fault", "Grid connection lost — check utility supply."),
    37: ("F37", "DCLLC_Soft_Over_Cur", "Software DC overcurrent; inspect PV/battery inputs."),
    39: ("F39", "DCLLC_Over_Current", "Hardware DC overcurrent; reduce DC input."),
    40: ("F40", "Batt_Over_Current", "Battery discharge exceeds current limit; check battery settings."),
    41: ("F41", "Parallel_System_Stop_Fault", "A parallel master/slave disconnect triggered stop."),
    45: ("F45", "AC_UV_OverVolt_Fault", "AC undervoltage/overvoltage — self reset when grid stabilizes."),
    46: ("F46", "Battery_Backup_Fault", "No communication with parallel systems; check Master/Slave & ethernet."),
    47: ("F47", "AC_OverFreq_Fault", "Grid over-frequency disconnect — self reset when stable."),
    48: ("F48", "AC_UnderFreq_Fault", "Grid under-frequency disconnect — self reset when stable."),
    55: ("F55", "DC_VoltHigh_Fault", "PV voltage above spec (>500V) or high battery voltage."),
    56: ("F56", "DC_VoltLow_Fault", "Batteries over-discharged or incorrect batt settings."),
    58: ("F58", "BMS_Communication_Fault", "Cannot communicate with Lithium BMS while enabled."),
    60: ("F60", "Gen_Volt_or_Fre_Fault", "Generator voltage or frequency out of allowable range."),
    61: ("F61", "Button_Manual_OFF", "Parallel slave turned off without Master."),
    63: ("F63", "Arc_Fault", "Arc fault — check PV connectors/cabling."),
    64: ("F64", "Heatsink_HighTemp_Fault", "Heatsink over-temperature; check fans & cooling clearance."),
}

MODBUS_EXCEPTIONS = {
    0x01: "Illegal Function - Function code not supported",
    0x02: "Illegal Data Address - Address not allowed",
    0x03: "Illegal Data Value - Value out of range",
    0x04: "Slave Device Failure - Device error",
    0x05: "Acknowledge - Request accepted, processing",
    0x06: "Slave Device Busy - Try again later",
    0x07: "Negative acknowledgment",
    0x08: "Memory Parity Error - Device memory error",
    0x0A: "Gateway Path Unavailable - Gateway error",
    0x0B: "Gateway Target Failed - Target not responding",
    0x0C: "Timeout",
    0x0D: "Invalid data type",
}

GRID_RELAY_STATUS: dict[int, str] = {
    0: "Closed",
    1: "Open",
}

GEN_RELAY_STATUS: dict[int, str] = {
    0: "Open",
    1: "Closed",
    2: "No Connection",
    3: "Closed when Generator is on",
}
