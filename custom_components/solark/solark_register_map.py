"""SolArk Modbus Register Map."""

from typing import TypeVar

from .const import GEN_RELAY_STATUS, GRID_RELAY_STATUS
from .fault_info import translate_fault_code_to_messages
from .register_map import DIAGNOSTIC, DataType, DeviceClass, NativeUnit, RegisterMap, RegisterMapEntry, StateClass

T = TypeVar("T", bound="RegisterMap")  # T is the real subclass

"""SolArk Modbus Register Map class"""


class SolArkRegisterMap(RegisterMap["SolArkRegisterMap"]):
    SN = RegisterMapEntry(
        address=3,
        string_register_length=5,
        key="sn",
        data_type=DataType.STRING,
        name="Serial Number",
        icon="mdi:information-outline",
        state_class=StateClass.NONE,
        entity_registry_enabled_default=False,
    )
    DAILYINV_E = RegisterMapEntry(
        address=60,
        key="dailyinv_e",
        data_type=DataType.INT16,
        scale=0.1,
        name="Daily Inverter Energy",
        native_unit_of_measurement=NativeUnit.KWH,
        device_class=DeviceClass.ENERGY,
        state_class=StateClass.TOTAL,
    )
    TOTALGRID_E = RegisterMapEntry(
        address=63,
        key="totalgrid_e",
        data_type=DataType.INT32,
        scale=0.1,
        name="Total Grid Breaker Energy",
        native_unit_of_measurement=NativeUnit.KWH,
        device_class=DeviceClass.ENERGY,
        state_class=StateClass.TOTAL,
    )
    DAILYBATT_C_E = RegisterMapEntry(
        address=70,
        key="daybattc_e",
        data_type=DataType.UINT16,
        scale=0.1,
        name="Daily Battery Charge Energy",
        native_unit_of_measurement=NativeUnit.KWH,
        device_class=DeviceClass.ENERGY,
        state_class=StateClass.TOTAL_INCREASING,
    )
    DAILYBATT_D_E = RegisterMapEntry(
        address=71,
        key="daybattd_e",
        data_type=DataType.UINT16,
        scale=0.1,
        name="Daily Battery Discharge Energy",
        native_unit_of_measurement=NativeUnit.KWH,
        device_class=DeviceClass.ENERGY,
        state_class=StateClass.TOTAL_INCREASING,
    )
    DAILYGRIDBUY_E = RegisterMapEntry(
        address=76,
        key="dailygridbuy_e",
        data_type=DataType.UINT16,
        scale=0.1,
        name="Daily Grid Buy Energy",
        native_unit_of_measurement=NativeUnit.KWH,
        device_class=DeviceClass.ENERGY,
        state_class=StateClass.TOTAL_INCREASING,
    )
    DAILYGRIDSELL_E = RegisterMapEntry(
        address=77,
        key="dailygridsell_e",
        data_type=DataType.UINT16,
        scale=0.1,
        name="Daily Grid Sell Energy",
        native_unit_of_measurement=NativeUnit.KWH,
        device_class=DeviceClass.ENERGY,
        state_class=StateClass.TOTAL_INCREASING,
    )
    GRIDFREQ = RegisterMapEntry(
        address=79,
        key="gridfreq",
        data_type=DataType.UINT16,
        scale=0.01,
        name="Grid Frequency",
        icon="mdi:sine-wave",
        native_unit_of_measurement=NativeUnit.HZ,
        state_class=StateClass.MEASUREMENT,
    )
    DAILYLOAD_E = RegisterMapEntry(
        address=84,
        key="dailyload_e",
        data_type=DataType.UINT16,
        scale=0.1,
        name="Daily Load Energy",
        native_unit_of_measurement=NativeUnit.KWH,
        device_class=DeviceClass.ENERGY,
        state_class=StateClass.TOTAL_INCREASING,
    )
    TOTALLOAD_E = RegisterMapEntry(
        address=85,
        key="totalload_e",
        data_type=DataType.UINT32,
        scale=0.1,
        name="Total Load Energy",
        native_unit_of_measurement=NativeUnit.KWH,
        device_class=DeviceClass.ENERGY,
        state_class=StateClass.TOTAL,
    )
    DCHSTempC = RegisterMapEntry(
        address=90,
        key="dchstempc",
        data_type=DataType.UINT16,
        scale=0.1,
        offset=1000,
        name="DC Heatsink Temperature",
        native_unit_of_measurement=NativeUnit.CELSIUS,
        device_class=DeviceClass.TEMPERATURE,
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    ACHSTempC = RegisterMapEntry(
        address=91,
        key="achstempc",
        data_type=DataType.UINT16,
        scale=0.1,
        offset=1000,
        name="AC Heatsink Temperature",
        native_unit_of_measurement=NativeUnit.CELSIUS,
        device_class=DeviceClass.TEMPERATURE,
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    TOTALINV_E = RegisterMapEntry(
        address=96,
        key="totalinv_e",
        data_type=DataType.INT64,
        scale=0.1,
        name="Total PV Energy",
        native_unit_of_measurement=NativeUnit.KWH,
        device_class=DeviceClass.ENERGY,
        state_class=StateClass.TOTAL_INCREASING,
    )
    FAULT_INFO_RAW = RegisterMapEntry(
        address=103,
        key="fault_info_raw",
        data_type=DataType.UINT64,
        name="Inverter Fault Information Raw Value",
        icon="mdi:message-alert-outline",
        entity_category=DIAGNOSTIC,
    )
    CORR_BATT_CAP = RegisterMapEntry(
        address=107,
        key="corr_batt_cap",
        data_type=DataType.UINT16,
        name="Corrected Battery Capacity",
        icon="mdi:battery",
        native_unit_of_measurement=NativeUnit.AH,
        state_class=StateClass.NONE,
        entity_registry_enabled_default=False,
    )
    DAILYPV_E = RegisterMapEntry(
        address=108,
        key="dailypv_e",
        data_type=DataType.UINT16,
        scale=0.1,
        name="Daily PV Energy",
        native_unit_of_measurement=NativeUnit.KWH,
        device_class=DeviceClass.ENERGY,
        state_class=StateClass.TOTAL_INCREASING,
    )
    PV1_V = RegisterMapEntry(
        address=109,
        key="pv1_v",
        data_type=DataType.UINT16,
        scale=0.1,
        name="PV1 Voltage",
        native_unit_of_measurement=NativeUnit.V,
        device_class=DeviceClass.VOLTAGE,
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    PV1_C = RegisterMapEntry(
        address=110,
        key="pv1_c",
        data_type=DataType.UINT16,
        scale=0.1,
        name="PV1 Current",
        native_unit_of_measurement=NativeUnit.A,
        device_class=DeviceClass.CURRENT,
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    PV2_V = RegisterMapEntry(
        address=111,
        key="pv2_v",
        data_type=DataType.UINT16,
        scale=0.1,
        name="PV2 Voltage",
        native_unit_of_measurement=NativeUnit.V,
        device_class=DeviceClass.VOLTAGE,
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    PV2_C = RegisterMapEntry(
        address=112,
        key="pv2_c",
        data_type=DataType.UINT16,
        scale=0.1,
        name="PV2 Current",
        native_unit_of_measurement=NativeUnit.A,
        device_class=DeviceClass.CURRENT,
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    PV3_V = RegisterMapEntry(
        address=113,
        key="pv3_v",
        data_type=DataType.UINT16,
        scale=0.1,
        name="PV3 Voltage",
        native_unit_of_measurement=NativeUnit.V,
        device_class=DeviceClass.VOLTAGE,
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    PV3_C = RegisterMapEntry(
        address=114,
        key="pv3_c",
        data_type=DataType.UINT16,
        scale=0.1,
        name="PV3 Current",
        native_unit_of_measurement=NativeUnit.A,
        device_class=DeviceClass.CURRENT,
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    GRIDL1N_V = RegisterMapEntry(
        address=150,
        key="gridl1n_v",
        data_type=DataType.UINT16,
        scale=0.1,
        name="Grid L1-N Voltage",
        native_unit_of_measurement=NativeUnit.V,
        device_class=DeviceClass.VOLTAGE,
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    GRIDL2N_V = RegisterMapEntry(
        address=151,
        key="gridl2n_v",
        data_type=DataType.UINT16,
        scale=0.1,
        name="Grid L2-N Voltage",
        native_unit_of_measurement=NativeUnit.V,
        device_class=DeviceClass.VOLTAGE,
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    GRIDL1L2_V = RegisterMapEntry(
        address=152,
        key="gridl1l2_v",
        data_type=DataType.UINT16,
        scale=0.1,
        name="Grid L1-L2 Voltage",
        native_unit_of_measurement=NativeUnit.V,
        device_class=DeviceClass.VOLTAGE,
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    GRIDRELAY_V = RegisterMapEntry(
        address=153,
        key="gridrelay_v",
        data_type=DataType.UINT16,
        scale=0.1,
        name="Grid Relay Voltage",
        native_unit_of_measurement=NativeUnit.V,
        device_class=DeviceClass.VOLTAGE,
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    INVL1N_V = RegisterMapEntry(
        address=154,
        key="invl1n_v",
        data_type=DataType.UINT16,
        scale=0.1,
        name="Inverter L1-N Voltage",
        native_unit_of_measurement=NativeUnit.V,
        device_class=DeviceClass.VOLTAGE,
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    INVL2N_V = RegisterMapEntry(
        address=155,
        key="invl2n_v",
        data_type=DataType.UINT16,
        scale=0.1,
        name="Inverter L2-N Voltage",
        native_unit_of_measurement=NativeUnit.V,
        device_class=DeviceClass.VOLTAGE,
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    INVL1L2_V = RegisterMapEntry(
        address=156,
        key="invl1l2_v",
        data_type=DataType.UINT16,
        scale=0.1,
        name="Inverter L1-L2 Voltage",
        native_unit_of_measurement=NativeUnit.V,
        device_class=DeviceClass.VOLTAGE,
        state_class=StateClass.MEASUREMENT,
    )
    LOADL1N_V = RegisterMapEntry(
        address=157,
        key="loadl1n_v",
        data_type=DataType.UINT16,
        scale=0.1,
        name="Load L1-N Voltage",
        native_unit_of_measurement=NativeUnit.V,
        device_class=DeviceClass.VOLTAGE,
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    LOADL2N_V = RegisterMapEntry(
        address=158,
        key="loadl2n_v",
        data_type=DataType.UINT16,
        scale=0.1,
        name="Load L2-N Voltage",
        native_unit_of_measurement=NativeUnit.V,
        device_class=DeviceClass.VOLTAGE,
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    GRIDL1_C = RegisterMapEntry(
        address=160,
        key="gridl1_c",
        data_type=DataType.INT16,
        scale=0.01,
        name="Grid L1 Current",
        icon="mdi:current-ac",
        native_unit_of_measurement=NativeUnit.A,
        device_class=DeviceClass.CURRENT,
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    GRIDL2_C = RegisterMapEntry(
        address=161,
        key="gridl2_c",
        data_type=DataType.INT16,
        scale=0.01,
        name="Grid L2 Current",
        icon="mdi:current-ac",
        native_unit_of_measurement=NativeUnit.A,
        device_class=DeviceClass.CURRENT,
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    EXTLMTL1_C = RegisterMapEntry(
        address=162,
        key="extlmtl1_c",
        data_type=DataType.INT16,
        scale=0.01,
        name="External Lmt L1 Current",
        icon="mdi:current-ac",
        native_unit_of_measurement=NativeUnit.A,
        device_class=DeviceClass.CURRENT,
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    EXTLMTL2_C = RegisterMapEntry(
        address=163,
        key="extlmtl2_c",
        data_type=DataType.INT16,
        scale=0.01,
        name="External Lmt L2 Current",
        icon="mdi:current-ac",
        native_unit_of_measurement=NativeUnit.A,
        device_class=DeviceClass.CURRENT,
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    INVL1_C = RegisterMapEntry(
        address=164,
        key="invl1_c",
        data_type=DataType.INT16,
        scale=0.01,
        name="Inverter L1 Current",
        icon="mdi:current-ac",
        native_unit_of_measurement=NativeUnit.A,
        device_class=DeviceClass.CURRENT,
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    INVL2_C = RegisterMapEntry(
        address=165,
        key="invl2_c",
        data_type=DataType.INT16,
        scale=0.01,
        name="Inverter L2 Current",
        icon="mdi:current-ac",
        native_unit_of_measurement=NativeUnit.A,
        device_class=DeviceClass.CURRENT,
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    GEN_P = RegisterMapEntry(
        address=166,
        key="gen_p",
        data_type=DataType.INT16,
        name="Gen Power",
        icon="mdi:solar-power",
        native_unit_of_measurement=NativeUnit.WATT,
        device_class=DeviceClass.POWER,
        state_class=StateClass.MEASUREMENT,
    )
    GRIDL1_P = RegisterMapEntry(
        address=167,
        key="gridl1_p",
        data_type=DataType.INT16,
        name="Grid L1 Power",
        icon="mdi:solar-power",
        native_unit_of_measurement=NativeUnit.WATT,
        device_class=DeviceClass.POWER,
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    GRIDL2_P = RegisterMapEntry(
        address=168,
        key="gridl2_p",
        data_type=DataType.INT16,
        name="Grid L2 Power",
        icon="mdi:solar-power",
        native_unit_of_measurement=NativeUnit.WATT,
        device_class=DeviceClass.POWER,
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    GRID_P = RegisterMapEntry(
        address=169,
        key="grid_p",
        data_type=DataType.INT16,
        name="Total Grid Power",
        icon="mdi:solar-power",
        native_unit_of_measurement=NativeUnit.WATT,
        device_class=DeviceClass.POWER,
        state_class=StateClass.MEASUREMENT,
    )
    GRIDLMTL1_P = RegisterMapEntry(
        address=170,
        key="gridlmtl1_p",
        data_type=DataType.INT16,
        name="Grid Limiter L1 Power",
        icon="mdi:solar-power",
        native_unit_of_measurement=NativeUnit.WATT,
        device_class=DeviceClass.POWER,
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    GRIDLMTL2_P = RegisterMapEntry(
        address=171,
        key="gridlmtl2_p",
        data_type=DataType.INT16,
        name="Grid Limiter L2 Power",
        icon="mdi:solar-power",
        native_unit_of_measurement=NativeUnit.WATT,
        device_class=DeviceClass.POWER,
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    GRIDEXT_P = RegisterMapEntry(
        address=172,
        key="gridext_p",
        data_type=DataType.INT16,
        name="Grid External total Power",
        icon="mdi:solar-power",
        native_unit_of_measurement=NativeUnit.WATT,
        device_class=DeviceClass.POWER,
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    INVL1_P = RegisterMapEntry(
        address=173,
        key="invl1_p",
        data_type=DataType.INT16,
        name="Inverter L1 Power",
        icon="mdi:solar-power",
        native_unit_of_measurement=NativeUnit.WATT,
        device_class=DeviceClass.POWER,
        state_class=StateClass.MEASUREMENT,
    )
    INVL2_P = RegisterMapEntry(
        address=174,
        key="invl2_p",
        data_type=DataType.INT16,
        name="Inverter L2 Power",
        icon="mdi:solar-power",
        native_unit_of_measurement=NativeUnit.WATT,
        device_class=DeviceClass.POWER,
        state_class=StateClass.MEASUREMENT,
    )
    INV_P = RegisterMapEntry(
        address=175,
        key="inv_p",
        data_type=DataType.INT16,
        name="Inverter Power",
        icon="mdi:solar-power",
        native_unit_of_measurement=NativeUnit.WATT,
        device_class=DeviceClass.POWER,
        state_class=StateClass.MEASUREMENT,
    )
    LOADL1_P = RegisterMapEntry(
        address=176,
        key="loadl1_p",
        data_type=DataType.INT16,
        name="Load L1 Power",
        icon="mdi:solar-power",
        native_unit_of_measurement=NativeUnit.WATT,
        device_class=DeviceClass.POWER,
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    LOADL2_P = RegisterMapEntry(
        address=177,
        key="loadl2_p",
        data_type=DataType.INT16,
        name="Load L2 Power",
        icon="mdi:solar-power",
        native_unit_of_measurement=NativeUnit.WATT,
        device_class=DeviceClass.POWER,
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    LOAD_P = RegisterMapEntry(
        address=178,
        key="load_p",
        data_type=DataType.INT16,
        name="Load Power",
        icon="mdi:solar-power",
        native_unit_of_measurement=NativeUnit.WATT,
        device_class=DeviceClass.POWER,
        state_class=StateClass.MEASUREMENT,
    )
    LOADL1_C = RegisterMapEntry(
        address=179,
        key="loadl1_c",
        data_type=DataType.INT16,
        scale=0.01,
        name="Load L1 Current",
        icon="mdi:current-ac",
        native_unit_of_measurement=NativeUnit.A,
        device_class=DeviceClass.CURRENT,
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    LOADL2_C = RegisterMapEntry(
        address=180,
        key="loadl2_c",
        data_type=DataType.INT16,
        scale=0.01,
        name="Load L2 Current",
        icon="mdi:current-ac",
        native_unit_of_measurement=NativeUnit.A,
        device_class=DeviceClass.CURRENT,
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    GENL1L2_V = RegisterMapEntry(
        address=181,
        key="genl1l2_v",
        data_type=DataType.UINT16,
        scale=0.1,
        name="Generator L1-L2 Voltage",
        native_unit_of_measurement=NativeUnit.V,
        device_class=DeviceClass.VOLTAGE,
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    BATTTEMP_C = RegisterMapEntry(
        address=182,
        key="batttempc",
        data_type=DataType.UINT16,
        scale=0.1,
        offset=1000,
        name="Battery Temperature",
        native_unit_of_measurement=NativeUnit.CELSIUS,
        device_class=DeviceClass.TEMPERATURE,
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    BATT_V = RegisterMapEntry(
        address=183,
        key="batt_v",
        data_type=DataType.UINT16,
        scale=0.01,
        name="Battery Voltage",
        icon="mdi:battery",
        native_unit_of_measurement=NativeUnit.V,
        device_class=DeviceClass.VOLTAGE,
        state_class=StateClass.MEASUREMENT,
    )
    BATT_SOC = RegisterMapEntry(
        address=184,
        key="batt_soc",
        data_type=DataType.UINT16,
        name="Battery State of Charge",
        icon="mdi:battery-50",
        native_unit_of_measurement=NativeUnit.PERCENT,
        device_class=DeviceClass.BATTERY,
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    PV1_P = RegisterMapEntry(
        address=186,
        key="pv1_p",
        data_type=DataType.UINT16,
        name="PV1 Input Power",
        icon="mdi:solar-power",
        native_unit_of_measurement=NativeUnit.WATT,
        device_class=DeviceClass.POWER,
        state_class=StateClass.MEASUREMENT,
    )
    PV2_P = RegisterMapEntry(
        address=187,
        key="pv2_p",
        data_type=DataType.UINT16,
        name="PV2 Input Power",
        icon="mdi:solar-power",
        native_unit_of_measurement=NativeUnit.WATT,
        device_class=DeviceClass.POWER,
        state_class=StateClass.MEASUREMENT,
    )
    PV3_P = RegisterMapEntry(
        address=188,
        key="pv3_p",
        data_type=DataType.UINT16,
        name="PV3 Input Power",
        icon="mdi:solar-power",
        native_unit_of_measurement=NativeUnit.WATT,
        device_class=DeviceClass.POWER,
        state_class=StateClass.MEASUREMENT,
    )
    BATT_P = RegisterMapEntry(
        address=190,
        key="batt_p",
        data_type=DataType.INT16,
        name="Battery Power",
        icon="mdi:solar-power",
        native_unit_of_measurement=NativeUnit.WATT,
        device_class=DeviceClass.POWER,
        state_class=StateClass.MEASUREMENT,
    )
    BATT_C = RegisterMapEntry(
        address=191,
        key="batt_c",
        data_type=DataType.INT16,
        scale=0.01,
        name="Battery Current",
        icon="mdi:current-dc",
        native_unit_of_measurement=NativeUnit.A,
        device_class=DeviceClass.CURRENT,
        state_class=StateClass.MEASUREMENT,
    )
    LOAD_FREQ = RegisterMapEntry(
        address=192,
        key="loadfreq",
        data_type=DataType.UINT16,
        scale=0.01,
        name="Load Frequency",
        icon="mdi:sine-wave",
        native_unit_of_measurement=NativeUnit.HZ,
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    INVERTER_FREQ = RegisterMapEntry(
        address=193,
        key="inverterfreq",
        data_type=DataType.UINT16,
        scale=0.01,
        name="Inverter Output Frequency",
        icon="mdi:sine-wave",
        native_unit_of_measurement=NativeUnit.HZ,
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    GRID_RLY_RAW = RegisterMapEntry(
        address=194,
        key="grid_rly_raw",
        data_type=DataType.INT16,
        name="Grid Relay Raw Value",
        icon="mdi:electric-switch",
        state_class=StateClass.NONE,
        entity_registry_enabled_default=False,
        entity_category=DIAGNOSTIC,
    )
    GEN_RLY_RAW = RegisterMapEntry(
        address=195,
        key="gen_rly_raw",
        data_type=DataType.INT16,
        name="Generator Relay Raw Value",
        icon="mdi:electric-switch",
        state_class=StateClass.NONE,
        entity_registry_enabled_default=False,
        entity_category=DIAGNOSTIC,
    )
    GEN_FREQ = RegisterMapEntry(
        address=196,
        key="genfreq",
        data_type=DataType.UINT16,
        scale=0.01,
        name="Generator Relay Frequency",
        icon="mdi:sine-wave",
        native_unit_of_measurement=NativeUnit.HZ,
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )

    @staticmethod
    def fault_code_to_message(register_map: "SolArkRegisterMap", entry: RegisterMapEntry):
        fault_message_list = translate_fault_code_to_messages(int(register_map.FAULT_INFO_RAW))
        entry.register_value = ", ".join(fault_message_list)

    @staticmethod
    def pv_input_power(register_map: "SolArkRegisterMap", entry: RegisterMapEntry):
        entry.register_value = register_map.PV1_P + register_map.PV2_P + register_map.PV3_P

    @staticmethod
    def grid_relay_status(register_map: "SolArkRegisterMap", entry: RegisterMapEntry):
        raw: int = int(register_map.GRID_RLY_RAW)
        entry.register_value = GRID_RELAY_STATUS.get(int(raw), "Unknown") if raw is not None else "Unknown"

    @staticmethod
    def gen_relay_status(register_map: "SolArkRegisterMap", entry: RegisterMapEntry):
        raw: int = int(register_map.GEN_RLY_RAW) & 0x0F  # mask low 4 bits
        entry.register_value = GEN_RELAY_STATUS.get(int(raw), "Unknown") if raw is not None else "Unknown"

    FAULTMSG = RegisterMapEntry(
        source_is_register_read=False,
        key="faultmsg",
        data_type=DataType.STRING,
        name="Inverter error Message",
        # name="Inverter Fault Message", # TODO - get concensus on changing entiity name(s) to match the SolArk documentation.
        # Caution: this is used by the hub to indicate a communication error with the device.
        # TODO - Another option is to create another entity, with the old one set to be not enabled buy default.
        icon="mdi:message-alert-outline",
        state_class=StateClass.NONE,
        post_process_method=fault_code_to_message,
    )
    PV_P = RegisterMapEntry(
        source_is_register_read=False,
        key="pv_p",
        data_type=DataType.UINT16,
        name="PV Input Power",
        icon="mdi:solar-power",
        native_unit_of_measurement=NativeUnit.WATT,
        device_class=DeviceClass.POWER,
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
        post_process_method=pv_input_power,
    )
    GRID_RLY = RegisterMapEntry(
        source_is_register_read=False,
        key="grid_rly",
        data_type=DataType.INT16,
        name="Grid Relay",
        icon="mdi:electric-switch",
        state_class=StateClass.NONE,
        entity_registry_enabled_default=False,
        post_process_method=grid_relay_status,
    )
    GEN_RLY = RegisterMapEntry(
        source_is_register_read=False,
        key="gen_rly",
        data_type=DataType.INT16,
        name="Generator Relay",
        icon="mdi:electric-switch",
        state_class=StateClass.NONE,
        entity_registry_enabled_default=False,
        post_process_method=gen_relay_status,
        description="Indicates the status of the generator relay based on raw register values.",
    )
