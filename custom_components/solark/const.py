from dataclasses import dataclass

from homeassistant.components.sensor import (
    STATE_CLASS_MEASUREMENT,
    STATE_CLASS_TOTAL_INCREASING,
    STATE_CLASS_TOTAL,
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

    "DailyInv_E": SolArkModbusSensorEntityDescription(
        name="Daily Inverter Energy",
        key="dailyinv_e",
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
        device_class=DEVICE_CLASS_ENERGY,
        state_class=STATE_CLASS_TOTAL_INCREASING,
        entity_registry_enabled_default=False,
    ),

    "DailyPV_E": SolArkModbusSensorEntityDescription(
        name="Daily PV Energy",
        key="dailypv_e",
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
        device_class=DEVICE_CLASS_ENERGY,
        state_class=STATE_CLASS_TOTAL_INCREASING,
    ),

    "DailyBattC_E": SolArkModbusSensorEntityDescription(
        name="Daily Battery Charge Energy",
        key="daybattc_e",
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
        device_class=DEVICE_CLASS_ENERGY,
        state_class=STATE_CLASS_TOTAL_INCREASING,
    ),

    "DailyBattD_E": SolArkModbusSensorEntityDescription(
        name="Daily Battery Discharge Energy",
        key="daybattd_e",
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
        device_class=DEVICE_CLASS_ENERGY,
        state_class=STATE_CLASS_TOTAL_INCREASING,
    ),

    "DailyGridBuy_E": SolArkModbusSensorEntityDescription(
        name="Daily Grid Buy Energy",
        key="dailygridbuy_e",
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
        device_class=DEVICE_CLASS_ENERGY,
        state_class=STATE_CLASS_TOTAL_INCREASING,
    ),

    "DailyGridSell_E": SolArkModbusSensorEntityDescription(
        name="Daily Grid Sell Energy",
        key="dailygridsell_e",
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
        device_class=DEVICE_CLASS_ENERGY,
        state_class=STATE_CLASS_TOTAL_INCREASING,
    ),

    "GridFreq": SolArkModbusSensorEntityDescription(
        name="Grid Frequency",
        key="gridfreq",
        native_unit_of_measurement=FREQUENCY_HERTZ,
        state_class=STATE_CLASS_MEASUREMENT,
    ),

    "TotalGrid_E": SolArkModbusSensorEntityDescription(
        name="Total Grid Breaker Energy",
        key="totalgrid_e",
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
        device_class=DEVICE_CLASS_ENERGY,
        state_class=STATE_CLASS_TOTAL_INCREASING,
    ),

    "TotalInv_E": SolArkModbusSensorEntityDescription(
        name="Total PV Energy",
        key="totalinv_e",
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
        device_class=DEVICE_CLASS_ENERGY,
        state_class=STATE_CLASS_TOTAL_INCREASING,
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
        name="Grid L1-N Voltage",
        key="gridl1n_v",
        native_unit_of_measurement=ELECTRIC_POTENTIAL_VOLT,
        device_class=DEVICE_CLASS_VOLTAGE,
        state_class=STATE_CLASS_MEASUREMENT,
        entity_registry_enabled_default=False,
    ),

    "GridL2N_V": SolArkModbusSensorEntityDescription(
        name="Grid L2-N Voltage",
        key="gridl2n_v",
        native_unit_of_measurement=ELECTRIC_POTENTIAL_VOLT,
        device_class=DEVICE_CLASS_VOLTAGE,
        state_class=STATE_CLASS_MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
    "GridL1L2_V": SolArkModbusSensorEntityDescription(
        name="Grid L1-L2 Voltage",
        key="gridl1l2_v",
        native_unit_of_measurement=ELECTRIC_POTENTIAL_VOLT,
        device_class=DEVICE_CLASS_VOLTAGE,
        state_class=STATE_CLASS_MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
    "GridRelay_V": SolArkModbusSensorEntityDescription(
        name="Grid Relay Voltage",
        key="gridrelay_v",
        native_unit_of_measurement=ELECTRIC_POTENTIAL_VOLT,
        device_class=DEVICE_CLASS_VOLTAGE,
        state_class=STATE_CLASS_MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
    "InvL1N_V": SolArkModbusSensorEntityDescription(
        name="Inverter L1-N Voltage",
        key="invl1n_v",
        native_unit_of_measurement=ELECTRIC_POTENTIAL_VOLT,
        device_class=DEVICE_CLASS_VOLTAGE,
        state_class=STATE_CLASS_MEASUREMENT,
        entity_registry_enabled_default=False,
    ),

    "InvL2N_V": SolArkModbusSensorEntityDescription(
        name="Inverter L2-N Voltage",
        key="invl2n_v",
        native_unit_of_measurement=ELECTRIC_POTENTIAL_VOLT,
        device_class=DEVICE_CLASS_VOLTAGE,
        state_class=STATE_CLASS_MEASUREMENT,
        entity_registry_enabled_default=False,
    ),

    "InvL1L2_V": SolArkModbusSensorEntityDescription(
        name="Inverter L1-L2 Voltage",
        key="invl1l2_v",
        native_unit_of_measurement=ELECTRIC_POTENTIAL_VOLT,
        device_class=DEVICE_CLASS_VOLTAGE,
        state_class=STATE_CLASS_MEASUREMENT,
    ),

    "LoadL1N_V": SolArkModbusSensorEntityDescription(
        name="Load L1-N Voltage",
        key="loadl1n_v",
        native_unit_of_measurement=ELECTRIC_POTENTIAL_VOLT,
        device_class=DEVICE_CLASS_VOLTAGE,
        state_class=STATE_CLASS_MEASUREMENT,
        entity_registry_enabled_default=False,
    ),

    "LoadL2N_V": SolArkModbusSensorEntityDescription(
        name="Load L2-N Voltage",
        key="loadl2n_v",
        native_unit_of_measurement=ELECTRIC_POTENTIAL_VOLT,
        device_class=DEVICE_CLASS_VOLTAGE,
        state_class=STATE_CLASS_MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
    "GridL1_C": SolArkModbusSensorEntityDescription(
        name="Grid L1 Current",
        key="gridl1_c",
        native_unit_of_measurement=ELECTRIC_CURRENT_AMPERE,
        icon="mdi:current-ac",
        device_class=DEVICE_CLASS_CURRENT,
        state_class=STATE_CLASS_MEASUREMENT,
        entity_registry_enabled_default=False,
    ),

    "GridL2_C": SolArkModbusSensorEntityDescription(
        name="Grid L2 Current",
        key="gridl2_c",
        native_unit_of_measurement=ELECTRIC_CURRENT_AMPERE,
        icon="mdi:current-ac",
        device_class=DEVICE_CLASS_CURRENT,
        state_class=STATE_CLASS_MEASUREMENT,
        entity_registry_enabled_default=False,
    ),

    "ExtLmtL1_C": SolArkModbusSensorEntityDescription(
        name="External Lmt L1 Current",
        key="extlmtl1_c",
        native_unit_of_measurement=ELECTRIC_CURRENT_AMPERE,
        icon="mdi:current-ac",
        device_class=DEVICE_CLASS_CURRENT,
        state_class=STATE_CLASS_MEASUREMENT,
        entity_registry_enabled_default=False,
    ),

    "ExtLmtL2_C": SolArkModbusSensorEntityDescription(
        name="External Lmt L2 Current",
        key="extlmtl2_c",
        native_unit_of_measurement=ELECTRIC_CURRENT_AMPERE,
        icon="mdi:current-ac",
        device_class=DEVICE_CLASS_CURRENT,
        state_class=STATE_CLASS_MEASUREMENT,
        entity_registry_enabled_default=False,
    ),

    "InvL1_C": SolArkModbusSensorEntityDescription(
        name="Inverter L1 Current",
        key="invl1_c",
        native_unit_of_measurement=ELECTRIC_CURRENT_AMPERE,
        icon="mdi:current-ac",
        device_class=DEVICE_CLASS_CURRENT,
        state_class=STATE_CLASS_MEASUREMENT,
        entity_registry_enabled_default=False,
    ),

    "InvL2_C": SolArkModbusSensorEntityDescription(
        name="Inverter L2 Current",
        key="invl2_c",
        native_unit_of_measurement=ELECTRIC_CURRENT_AMPERE,
        icon="mdi:current-ac",
        device_class=DEVICE_CLASS_CURRENT,
        state_class=STATE_CLASS_MEASUREMENT,
        entity_registry_enabled_default=False,
    ),

    "Gen_P": SolArkModbusSensorEntityDescription(
        name="Gen Power",
        key="gen_p",
        native_unit_of_measurement=POWER_WATT,
        icon="mdi:solar-power",
        device_class=DEVICE_CLASS_POWER,
        state_class=STATE_CLASS_MEASUREMENT,
    ),

    "GridL1_P": SolArkModbusSensorEntityDescription(
        name="Grid L1 Power",
        key="gridl1_p",
        native_unit_of_measurement=POWER_WATT,
        icon="mdi:solar-power",
        device_class=DEVICE_CLASS_POWER,
        state_class=STATE_CLASS_MEASUREMENT,
        entity_registry_enabled_default=False,
  ),


    "GridL2_P": SolArkModbusSensorEntityDescription(
        name="Grid L2 Power",
        key="gridl2_p",
        native_unit_of_measurement=POWER_WATT,
        icon="mdi:solar-power",
        device_class=DEVICE_CLASS_POWER,
        state_class=STATE_CLASS_MEASUREMENT,
        entity_registry_enabled_default=False,
    ),

    "Grid_P": SolArkModbusSensorEntityDescription(
        name="Total Grid Power",
        key="grid_p",
        native_unit_of_measurement=POWER_WATT,
        icon="mdi:solar-power",
        device_class=DEVICE_CLASS_POWER,
        state_class=STATE_CLASS_MEASUREMENT,
    ),

    "GridLmtL1_P": SolArkModbusSensorEntityDescription(
        name="Grid Limiter L1 Power",
        key="gridlmtl1_p",
        native_unit_of_measurement=POWER_WATT,
        icon="mdi:solar-power",
        device_class=DEVICE_CLASS_POWER,
        state_class=STATE_CLASS_MEASUREMENT,
        entity_registry_enabled_default=False,
    ),

    "GridLmtL2_P": SolArkModbusSensorEntityDescription(
        name="Grid Limiter L2 Power",
        key="gridlmtl2_p",
        native_unit_of_measurement=POWER_WATT,
        icon="mdi:solar-power",
        device_class=DEVICE_CLASS_POWER,
        state_class=STATE_CLASS_MEASUREMENT,
        entity_registry_enabled_default=False,
    ),

    "GridExt_P": SolArkModbusSensorEntityDescription(
        name="Grid External total Power",
        key="gridext_p",
        native_unit_of_measurement=POWER_WATT,
        icon="mdi:solar-power",
        device_class=DEVICE_CLASS_POWER,
        state_class=STATE_CLASS_MEASUREMENT,
        entity_registry_enabled_default=False,
  ),

    "InvL1_P": SolArkModbusSensorEntityDescription(
        name="Inverter L1 Power",
        key="invl1_p",
        native_unit_of_measurement=POWER_WATT,
        icon="mdi:solar-power",
        device_class=DEVICE_CLASS_POWER,
        state_class=STATE_CLASS_MEASUREMENT,
    ),

    "InvL2_P": SolArkModbusSensorEntityDescription(
        name="Inverter L2 Power",
        key="invl2_p",
        native_unit_of_measurement=POWER_WATT,
        icon="mdi:solar-power",
        device_class=DEVICE_CLASS_POWER,
        state_class=STATE_CLASS_MEASUREMENT,
    ),

    "Inv_P": SolArkModbusSensorEntityDescription(
        name="Inverter Power",
        key="inv_p",
        native_unit_of_measurement=POWER_WATT,
        icon="mdi:solar-power",
        device_class=DEVICE_CLASS_POWER,
        state_class=STATE_CLASS_MEASUREMENT,
    ),

    "LoadL1_P": SolArkModbusSensorEntityDescription(
        name="Load L1 Power",
        key="loadl1_p",
        native_unit_of_measurement=POWER_WATT,
        icon="mdi:solar-power",
        device_class=DEVICE_CLASS_POWER,
        state_class=STATE_CLASS_MEASUREMENT,
        entity_registry_enabled_default=False,
    ),

    "LoadL2_P": SolArkModbusSensorEntityDescription(
        name="Load L2 Power",
        key="loadl2_p",
        native_unit_of_measurement=POWER_WATT,
        icon="mdi:solar-power",
        device_class=DEVICE_CLASS_POWER,
        state_class=STATE_CLASS_MEASUREMENT,
        entity_registry_enabled_default=False,
    ),

    "Load_P": SolArkModbusSensorEntityDescription(
        name="Load Power",
        key="load_p",
        native_unit_of_measurement=POWER_WATT,
        icon="mdi:solar-power",
        device_class=DEVICE_CLASS_POWER,
        state_class=STATE_CLASS_MEASUREMENT,
    ),

    "LoadL1_C": SolArkModbusSensorEntityDescription(
        name="Load L1 Current",
        key="loadl1_c",
        native_unit_of_measurement=ELECTRIC_CURRENT_AMPERE,
        icon="mdi:current-ac",
        device_class=DEVICE_CLASS_CURRENT,
        state_class=STATE_CLASS_MEASUREMENT,
        entity_registry_enabled_default=False,
    ),

    "LoadL2_C": SolArkModbusSensorEntityDescription(
        name="Load L2 Current",
        key="loadl2_c",
        native_unit_of_measurement=ELECTRIC_CURRENT_AMPERE,
        icon="mdi:current-ac",
        device_class=DEVICE_CLASS_CURRENT,
        state_class=STATE_CLASS_MEASUREMENT,
        entity_registry_enabled_default=False,
    ),

    "GenL1L2_V": SolArkModbusSensorEntityDescription(
        name="Generator L1-L2 Voltage",
        key="genl1l2_v",
        native_unit_of_measurement=ELECTRIC_POTENTIAL_VOLT,
        device_class=DEVICE_CLASS_VOLTAGE,
        state_class=STATE_CLASS_MEASUREMENT,
        entity_registry_enabled_default=False,
    ),

    "BattTempC": SolArkModbusSensorEntityDescription(
        name="Battery Temperature",
        key="batttempc",
        native_unit_of_measurement=TEMP_CELSIUS,
        device_class=DEVICE_CLASS_TEMPERATURE,
        state_class=STATE_CLASS_MEASUREMENT,
        entity_registry_enabled_default=False,
    ),

    "Batt_v": SolArkModbusSensorEntityDescription(
        name="Battery Voltage",
        key="batt_v",
        icon="mdi:battery",
        native_unit_of_measurement=ELECTRIC_POTENTIAL_VOLT,
        device_class=DEVICE_CLASS_VOLTAGE,
        state_class=STATE_CLASS_MEASUREMENT,
    ),

    "Batt_SOC": SolArkModbusSensorEntityDescription(
        name="Battery State of Charge",
        key="batt_soc",
        icon="mdi:battery-50",
        native_unit_of_measurement=PERCENTAGE,
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
    ),

    "PV2_P": SolArkModbusSensorEntityDescription(
        name="PV2 Input Power",
        key="pv2_p",
        native_unit_of_measurement=POWER_WATT,
        icon="mdi:solar-power",
        device_class=DEVICE_CLASS_POWER,
        state_class=STATE_CLASS_MEASUREMENT,
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
    ),

    "Batt_C": SolArkModbusSensorEntityDescription(
        name="Battery Current",
        key="batt_c",
        native_unit_of_measurement=ELECTRIC_CURRENT_AMPERE,
        icon="mdi:current-dc",
        device_class=DEVICE_CLASS_CURRENT,
        state_class=STATE_CLASS_MEASUREMENT,
    ),

    "Update_Cnt": SolArkModbusSensorEntityDescription(
        name="Update Counter",
        key="update_cnt",
        state_class=STATE_CLASS_TOTAL,
        entity_registry_enabled_default=False,
    ),
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
