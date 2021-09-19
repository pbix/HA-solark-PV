from dataclasses import dataclass

from homeassistant.components.sensor import (
    STATE_CLASS_MEASUREMENT,
    STATE_CLASS_TOTAL_INCREASING,
    SensorEntityDescription,
)
from homeassistant.const import (
    DEVICE_CLASS_BATTERY,
    DEVICE_CLASS_CURRENT,
    DEVICE_CLASS_ENERGY,
    DEVICE_CLASS_POWER,
    DEVICE_CLASS_POWER_FACTOR,
    DEVICE_CLASS_TEMPERATURE,
    DEVICE_CLASS_VOLTAGE,
    ELECTRIC_CURRENT_AMPERE,
    ELECTRIC_CURRENT_MILLIAMPERE,
    ELECTRIC_POTENTIAL_VOLT,
    ENERGY_KILO_WATT_HOUR,
    FREQUENCY_HERTZ,
    PERCENTAGE,
    POWER_WATT,
    TEMP_CELSIUS,
    TIME_HOURS,
)

DOMAIN = "solark_modbus"
DEFAULT_NAME = "SolArk"
DEFAULT_SCAN_INTERVAL = 60
DEFAULT_PORT = 502
CONF_SOLARK_HUB = "solark_hub"
ATTR_MANUFACTURER = "SolArk"


@dataclass
class SolArkModbusSensorEntityDescription(SensorEntityDescription):
    """A class that describes SolArk sensor entities."""

SENSOR_TYPES: dict[str, list[SolArkModbusSensorEntityDescription]] = {
    "SN": SolArkModbusSensorEntityDescription(
        name="Serial Number",
        key="sn",
        icon="mdi:information-outline",
        entity_registry_enabled_default=False,
    ),
 
    "FaultMSG": SolArkModbusSensorEntityDescription(
        name="Inverter error message",
        key="faultmsg",
        icon="mdi:message-alert-outline",
    ),

    "DailyPV_E": SolArkModbusSensorEntityDescription(
        name="Daily PV Energy",
        key="dailypv_e",
        native_unit_of_measurement=ELECTRIC_POTENTIAL_VOLT,
        device_class=DEVICE_CLASS_VOLTAGE,
        state_class=STATE_CLASS_MEASUREMENT,
        entity_registry_enabled_default=False,
    ),

    "PV1_V": SolArkModbusSensorEntityDescription(
        name="PV1 Voltage",
        key="pv1_v",
        native_unit_of_measurement=ELECTRIC_POTENTIAL_VOLT,
        device_class=DEVICE_CLASS_VOLTAGE,
        state_class=STATE_CLASS_MEASUREMENT,
        entity_registry_enabled_default=False,
    ),

    "PV1_C": SolArkModbusSensorEntityDescription(
        name="PV1 Current",
        key="pv1_c",
        native_unit_of_measurement=ELECTRIC_CURRENT_AMPERE,
        icon="mdi:current-dc",
        device_class=DEVICE_CLASS_CURRENT,
        state_class=STATE_CLASS_MEASUREMENT,
        entity_registry_enabled_default=False,
    ),

    "PV2_V": SolArkModbusSensorEntityDescription(
        name="PV2 Voltage",
        key="pv2_v",
        native_unit_of_measurement=ELECTRIC_POTENTIAL_VOLT,
        device_class=DEVICE_CLASS_VOLTAGE,
        state_class=STATE_CLASS_MEASUREMENT,
        entity_registry_enabled_default=False,
    ),

    "PV2_C": SolArkModbusSensorEntityDescription(
        name="PV2 Current",
        key="pv2_c",
        native_unit_of_measurement=ELECTRIC_CURRENT_AMPERE,
        icon="mdi:current-dc",
        device_class=DEVICE_CLASS_CURRENT,
        state_class=STATE_CLASS_MEASUREMENT,
        entity_registry_enabled_default=False,
    ),


    "GridL1N_V": SolArkModbusSensorEntityDescription(
        name="Grid L1-N voltage",
        key="gridl1n_v",
        native_unit_of_measurement=ELECTRIC_POTENTIAL_VOLT,
        device_class=DEVICE_CLASS_VOLTAGE,
        state_class=STATE_CLASS_MEASUREMENT,
        entity_registry_enabled_default=False,
    ),

    "GridL2N_V": SolArkModbusSensorEntityDescription(
        name="Grid L2-N voltage",
        key="gridl2n_v",
        native_unit_of_measurement=ELECTRIC_POTENTIAL_VOLT,
        device_class=DEVICE_CLASS_VOLTAGE,
        state_class=STATE_CLASS_MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
    "GridL1L2_V": SolArkModbusSensorEntityDescription(
        name="Grid L1-L2 voltage",
        key="gridl1l2_v",
        native_unit_of_measurement=ELECTRIC_POTENTIAL_VOLT,
        device_class=DEVICE_CLASS_VOLTAGE,
        state_class=STATE_CLASS_MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
    "GridRelay_V": SolArkModbusSensorEntityDescription(
        name="Grid Relay voltage",
        key="gridrelay_v",
        native_unit_of_measurement=ELECTRIC_POTENTIAL_VOLT,
        device_class=DEVICE_CLASS_VOLTAGE,
        state_class=STATE_CLASS_MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
    "InvL1N_V": SolArkModbusSensorEntityDescription(
        name="Inverter L1-N voltage",
        key="invl1n_v",
        native_unit_of_measurement=ELECTRIC_POTENTIAL_VOLT,
        device_class=DEVICE_CLASS_VOLTAGE,
        state_class=STATE_CLASS_MEASUREMENT,
        entity_registry_enabled_default=False,
    ),

    "InvL2N_V": SolArkModbusSensorEntityDescription(
        name="Inverter L2-N voltage",
        key="invl2n_v",
        native_unit_of_measurement=ELECTRIC_POTENTIAL_VOLT,
        device_class=DEVICE_CLASS_VOLTAGE,
        state_class=STATE_CLASS_MEASUREMENT,
        entity_registry_enabled_default=False,
    ),

    "InvL1L2_V": SolArkModbusSensorEntityDescription(
        name="Inverter L1-L2 voltage",
        key="invl1l2_v",
        native_unit_of_measurement=ELECTRIC_POTENTIAL_VOLT,
        device_class=DEVICE_CLASS_VOLTAGE,
        state_class=STATE_CLASS_MEASUREMENT,
        entity_registry_enabled_default=False,
    ),

    "LoadL1N_V": SolArkModbusSensorEntityDescription(
        name="Load L1-N voltage",
        key="loadl1n_v",
        native_unit_of_measurement=ELECTRIC_POTENTIAL_VOLT,
        device_class=DEVICE_CLASS_VOLTAGE,
        state_class=STATE_CLASS_MEASUREMENT,
        entity_registry_enabled_default=False,
    ),

    "LoadL2N_V": SolArkModbusSensorEntityDescription(
        name="Load L2-N voltage",
        key="loadl2n_v",
        native_unit_of_measurement=ELECTRIC_POTENTIAL_VOLT,
        device_class=DEVICE_CLASS_VOLTAGE,
        state_class=STATE_CLASS_MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
    "GridL1_C": SolArkModbusSensorEntityDescription(
        name="Grid L1 current",
        key="gridl1_c",
        native_unit_of_measurement=ELECTRIC_CURRENT_AMPERE,
        icon="mdi:current-ac",
        device_class=DEVICE_CLASS_CURRENT,
        state_class=STATE_CLASS_MEASUREMENT,
        entity_registry_enabled_default=False,
    ),

    "GridL2_C": SolArkModbusSensorEntityDescription(
        name="Grid L2 current",
        key="gridl2_c",
        native_unit_of_measurement=ELECTRIC_CURRENT_AMPERE,
        icon="mdi:current-ac",
        device_class=DEVICE_CLASS_CURRENT,
        state_class=STATE_CLASS_MEASUREMENT,
        entity_registry_enabled_default=False,
    ),

    "ExtLmtL1_C": SolArkModbusSensorEntityDescription(
        name="External Lmt L1 current",
        key="extlmtl1_c",
        native_unit_of_measurement=ELECTRIC_CURRENT_AMPERE,
        icon="mdi:current-ac",
        device_class=DEVICE_CLASS_CURRENT,
        state_class=STATE_CLASS_MEASUREMENT,
        entity_registry_enabled_default=False,
    ),

    "ExtLmtL2_C": SolArkModbusSensorEntityDescription(
        name="External Lmt L2 current",
        key="extlmtl2_c",
        native_unit_of_measurement=ELECTRIC_CURRENT_AMPERE,
        icon="mdi:current-ac",
        device_class=DEVICE_CLASS_CURRENT,
        state_class=STATE_CLASS_MEASUREMENT,
        entity_registry_enabled_default=False,
    ),

    "InvL1_C": SolArkModbusSensorEntityDescription(
        name="Inverter L1 current",
        key="invl1_c",
        native_unit_of_measurement=ELECTRIC_CURRENT_AMPERE,
        icon="mdi:current-ac",
        device_class=DEVICE_CLASS_CURRENT,
        state_class=STATE_CLASS_MEASUREMENT,
        entity_registry_enabled_default=False,
    ),

    "InvL2_C": SolArkModbusSensorEntityDescription(
        name="Inverter L2 current",
        key="invl2_c",
        native_unit_of_measurement=ELECTRIC_CURRENT_AMPERE,
        icon="mdi:current-ac",
        device_class=DEVICE_CLASS_CURRENT,
        state_class=STATE_CLASS_MEASUREMENT,
        entity_registry_enabled_default=False,
    ),

    "Gen_P": SolArkModbusSensorEntityDescription(
        name="Gen power",
        key="gen_p",
        native_unit_of_measurement=POWER_WATT,
        icon="mdi:solar-power",
        device_class=DEVICE_CLASS_POWER,
        state_class=STATE_CLASS_MEASUREMENT,
    ),

    "GridL1_P": SolArkModbusSensorEntityDescription(
        name="Grid L1 power",
        key="gridl1_p",
        native_unit_of_measurement=POWER_WATT,
        icon="mdi:solar-power",
        device_class=DEVICE_CLASS_POWER,
        state_class=STATE_CLASS_MEASUREMENT,
        entity_registry_enabled_default=False,
  ),


    "GridL2_P": SolArkModbusSensorEntityDescription(
        name="Grid L2 power",
        key="gridl2_p",
        native_unit_of_measurement=POWER_WATT,
        icon="mdi:solar-power",
        device_class=DEVICE_CLASS_POWER,
        state_class=STATE_CLASS_MEASUREMENT,
        entity_registry_enabled_default=False,
    ),

    "Grid_P": SolArkModbusSensorEntityDescription(
        name="Total Grid power",
        key="grid_p",
        native_unit_of_measurement=POWER_WATT,
        icon="mdi:solar-power",
        device_class=DEVICE_CLASS_POWER,
        state_class=STATE_CLASS_MEASUREMENT,
    ),

    "GridLmtL1_P": SolArkModbusSensorEntityDescription(
        name="Grid Limiter L1 power",
        key="gridlmtl1_p",
        native_unit_of_measurement=POWER_WATT,
        icon="mdi:solar-power",
        device_class=DEVICE_CLASS_POWER,
        state_class=STATE_CLASS_MEASUREMENT,
        entity_registry_enabled_default=False,
    ),

    "GridLmtL2_P": SolArkModbusSensorEntityDescription(
        name="Grid Limiter L2 power",
        key="gridlmtl2_p",
        native_unit_of_measurement=POWER_WATT,
        icon="mdi:solar-power",
        device_class=DEVICE_CLASS_POWER,
        state_class=STATE_CLASS_MEASUREMENT,
        entity_registry_enabled_default=False,
    ),

    "GridExt_P": SolArkModbusSensorEntityDescription(
        name="Grid External total power",
        key="gridext_p",
        native_unit_of_measurement=POWER_WATT,
        icon="mdi:solar-power",
        device_class=DEVICE_CLASS_POWER,
        state_class=STATE_CLASS_MEASUREMENT,
        entity_registry_enabled_default=False,
  ),

    "InvL1_P": SolArkModbusSensorEntityDescription(
        name="Inverter L1 power",
        key="invl1_p",
        native_unit_of_measurement=POWER_WATT,
        icon="mdi:solar-power",
        device_class=DEVICE_CLASS_POWER,
        state_class=STATE_CLASS_MEASUREMENT,
    ),

    "InvL2_P": SolArkModbusSensorEntityDescription(
        name="Inverter L2 power",
        key="invl2_p",
        native_unit_of_measurement=POWER_WATT,
        icon="mdi:solar-power",
        device_class=DEVICE_CLASS_POWER,
        state_class=STATE_CLASS_MEASUREMENT,
    ),

    "Inv_P": SolArkModbusSensorEntityDescription(
        name="Inverter power",
        key="inv_p",
        native_unit_of_measurement=POWER_WATT,
        icon="mdi:solar-power",
        device_class=DEVICE_CLASS_POWER,
        state_class=STATE_CLASS_MEASUREMENT,
    ),

    "LoadL1_P": SolArkModbusSensorEntityDescription(
        name="Load L1 power",
        key="loadl1_p",
        native_unit_of_measurement=POWER_WATT,
        icon="mdi:solar-power",
        device_class=DEVICE_CLASS_POWER,
        state_class=STATE_CLASS_MEASUREMENT,
        entity_registry_enabled_default=False,
    ),

    "LoadL2_P": SolArkModbusSensorEntityDescription(
        name="Load L2 power",
        key="loadl2_p",
        native_unit_of_measurement=POWER_WATT,
        icon="mdi:solar-power",
        device_class=DEVICE_CLASS_POWER,
        state_class=STATE_CLASS_MEASUREMENT,
        entity_registry_enabled_default=False,
    ),

    "Load_P": SolArkModbusSensorEntityDescription(
        name="Load power",
        key="load_p",
        native_unit_of_measurement=POWER_WATT,
        icon="mdi:solar-power",
        device_class=DEVICE_CLASS_POWER,
        state_class=STATE_CLASS_MEASUREMENT,
    ),

    "LoadL1_C": SolArkModbusSensorEntityDescription(
        name="Load L1 current",
        key="loadl1_c",
        native_unit_of_measurement=ELECTRIC_CURRENT_AMPERE,
        icon="mdi:current-ac",
        device_class=DEVICE_CLASS_CURRENT,
        state_class=STATE_CLASS_MEASUREMENT,
        entity_registry_enabled_default=False,
    ),

    "LoadL2_C": SolArkModbusSensorEntityDescription(
        name="Load L2 current",
        key="loadl2_c",
        native_unit_of_measurement=ELECTRIC_CURRENT_AMPERE,
        icon="mdi:current-ac",
        device_class=DEVICE_CLASS_CURRENT,
        state_class=STATE_CLASS_MEASUREMENT,
        entity_registry_enabled_default=False,
    ),

    "GenL1L2_V": SolArkModbusSensorEntityDescription(
        name="Generator L1-L2 voltage",
        key="genl1l2_v",
        native_unit_of_measurement=ELECTRIC_POTENTIAL_VOLT,
        device_class=DEVICE_CLASS_VOLTAGE,
        state_class=STATE_CLASS_MEASUREMENT,
        entity_registry_enabled_default=False,
    ),

    "BattTempC": SolArkModbusSensorEntityDescription(
        name="Battery temperature",
        key="batttempc",
        native_unit_of_measurement=TEMP_CELSIUS,
        device_class=DEVICE_CLASS_TEMPERATURE,
        state_class=STATE_CLASS_MEASUREMENT,
        entity_registry_enabled_default=False,
    ),

    "Batt_v": SolArkModbusSensorEntityDescription(
        name="Battery voltage",
        key="batt_v",
        icon="mdi:battery",
        native_unit_of_measurement=ELECTRIC_POTENTIAL_VOLT,
        device_class=DEVICE_CLASS_VOLTAGE,
        state_class=STATE_CLASS_MEASUREMENT,
        entity_registry_enabled_default=False,
    ),

    "Batt_SOC": SolArkModbusSensorEntityDescription(
        name="Battery State Of Charge",
        key="batt_soc",
        icon="mdi:battery-50",
        native_unit_of_measurement=PERCENTAGE,
        device_class=DEVICE_CLASS_POWER,
        state_class=STATE_CLASS_MEASUREMENT,
        entity_registry_enabled_default=False,
    ),

    "PV1_P": SolArkModbusSensorEntityDescription(
        name="PV1 Input Power",
        key="pv1_p",
        native_unit_of_measurement=POWER_WATT,
        icon="mdi:solar-power",
        device_class=DEVICE_CLASS_POWER,
        state_class=STATE_CLASS_MEASUREMENT,
        entity_registry_enabled_default=False,
    ),

    "PV2_P": SolArkModbusSensorEntityDescription(
        name="PV2 Input Power",
        key="pv2_p",
        native_unit_of_measurement=POWER_WATT,
        icon="mdi:solar-power",
        device_class=DEVICE_CLASS_POWER,
        state_class=STATE_CLASS_MEASUREMENT,
        entity_registry_enabled_default=False,
    ),

    "PV_P": SolArkModbusSensorEntityDescription(
        name="PV Input Power",
        key="pv_p",
        native_unit_of_measurement=POWER_WATT,
        icon="mdi:solar-panel-large",
        device_class=DEVICE_CLASS_POWER,
        state_class=STATE_CLASS_MEASUREMENT,
    ),

    "Batt_P": SolArkModbusSensorEntityDescription(
        name="Battery Power",
        key="batt_p",
        native_unit_of_measurement=POWER_WATT,
        icon="mdi:solar-power",
        device_class=DEVICE_CLASS_POWER,
        state_class=STATE_CLASS_MEASUREMENT,
        entity_registry_enabled_default=True,
    ),

    "Batt_C": SolArkModbusSensorEntityDescription(
        name="Battery current",
        key="batt_c",
        native_unit_of_measurement=ELECTRIC_CURRENT_AMPERE,
        icon="mdi:current-dc",
        device_class=DEVICE_CLASS_CURRENT,
        state_class=STATE_CLASS_MEASUREMENT,
    ),

}

DEVICE_STATUSSES = {
    0: "Not Connected",
    1: "Waiting",
    2: "Normal",
    3: "Error",
}

FAULT_MESSAGES = {
        0b000000000000000000000000010000000: "F08 GFCI Relay Failure",
        0b000000000000000000001000000000000: "F13 Grid Mode Changed",
        0b000000000000000000010000000000000: "F14 DC Over Current",
        0b000000000000000000100000000000000: "F15 Software AC Over Current",
        0b000000000000000001000000000000000: "F16 GFCI Detection",
        0b000000000000000100000000000000000: "F18 Hardware AC Over Current",
        0b000000000000010000000000000000000: "F20 DC Over Current",
        0b000000000001000000000000000000000: "F22 Emergency Stop",
        0b000000000010000000000000000000000: "F23 GFCI Overcurrent",
        0b000000000100000000000000000000000: "F24 DC Insulation (ISO)",
        0b000000010000000000000000000000000: "F26 Bus Unbalance",
        0b000010000000000000000000000000000: "F29 Paralleled System",
        0b100000000000000000000000000000000: "F33 AC Over Current"
}
