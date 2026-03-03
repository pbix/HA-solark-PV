import logging
import threading
from datetime import datetime, timedelta
from typing import Iterator

from homeassistant.core import CALLBACK_TYPE, HomeAssistant, callback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .config import ConnectionType, SolArkConfig
from .const import DEFAULT_MAX_STALE_DATA_AGE, MODBUS_EXCEPTIONS
from .pymodbus_wrapper import ModbusClientWrapper, ModbusResponse
from .register_map import (
    DataType,
    NumericValue,
    RegisterMapEntry,
    RegisterValue,
)
from .solark_binary_payload_decoder import ModbusDecodeError, SolArkBinaryPayloadDecoder
from .solark_register_map import SolArkRegisterMap

_LOGGER = logging.getLogger(__name__)

""" Update the register map with the latest values read from the inverter and return a combined dictionary of all data.

Class is responsible for reading the data from the inverter and returning it as a dictionary.
The class maintains the last successful reading and timestamp, and if a read fails,
it will return the last known values if they are not too old, otherwise it will return an error message.

Philosopy here is  to perform a series of modbus reads, setting a single error flag for the whole dataset
on the failure of any read.
read, check for a successful read of all data, and return the last complete data.
If the read was not successful, then return the last known values if they are not too old, otherwise return an error message.
"""


class SolArkModbusHub(DataUpdateCoordinator[dict]):
    """Thread-safe wrapper for reading inverter data from Modbus using register dictionary."""

    def __init__(self, hass: HomeAssistant, name: str, hostname: str, scan_interval: int) -> None:
        """Initialize the Modbus hub."""
        super().__init__(
            hass,
            _LOGGER,
            name=name,
            update_interval=timedelta(seconds=scan_interval),
        )

        self.device_id = 1
        self.update_cnt = 0
        self.last_successful_data = {}
        self.last_successful_timestamp = None

        config = SolArkConfig.from_url(hostname)

        if config.connection_type == ConnectionType.TCP:
            self._client = ModbusClientWrapper(host=config.host, port=config.port)
        elif config.connection_type == ConnectionType.SERIAL:
            self._client = ModbusClientWrapper(serial_port=config.serial_port, baudrate=9600)

        self.device_id = config.device_id

        self._lock = threading.Lock()

        self.has_inverter_data = False
        self.register_map: SolArkRegisterMap = SolArkRegisterMap()

        self.max_stale_data_age = DEFAULT_MAX_STALE_DATA_AGE  # 5 minutes

    @callback
    def async_remove_listener(self, update_callback: CALLBACK_TYPE) -> None:
        """Remove a callback listener safely."""
        self._listeners.pop(update_callback, None)  # type: ignore[dict-item]
        if not self._listeners:
            self.close()

    async def async_stop(self, *_):
        """Ensure the client is closed on HA shutdown."""
        if self._client:
            await self.hass.async_add_executor_job(self.close)

    def close(self) -> None:
        """Close the Modbus client connection safely."""
        with self._lock:
            self._client.close()

    async def _async_update_data(self) -> dict:
        """Read the data from the inverter and return it as a dictionary."""
        data: dict = {}
        try:
            self.register_map.init()  # Initialize the register map before reading

            if not self.has_inverter_data:  # Inverter serial number is only fetched once
                await self.hass.async_add_executor_job(self._read_modbus_inverter_data)

            # Read realtime data
            await self.hass.async_add_executor_job(self._read_modbus_realtime_data)

            # If we already have a read failure, post processing is unnecessary and may fail as well
            if not self.register_map.is_error():
                await self.hass.async_add_executor_job(self._post_process_register_map_entries)

            data = self._handle_results()

        except Exception as e:
            _LOGGER.exception("Unexpected error reading inverter data: %s", e)
            data = {"faultmsg": "Unexpected error"}

        # Return combined data safely
        return {**data}

    def _read_modbus_inverter_data(self):
        """Read the static inverter data from the inverter and store the results in the register map."""

        self._process_register_range(self.register_map.SN)

        if self.register_map.is_error():
            _LOGGER.error("Reading inverter data failed!")

    def _read_modbus_realtime_data(self):
        """Read the real-time data from the inverter and store the results in the register map."""
        self._process_register_range(self.register_map.DAILYINV_E, self.register_map.GRIDFREQ)  # R60 - R79
        self._process_register_range(self.register_map.DAILYLOAD_E, self.register_map.ACHSTempC)  # R84 - R91

        # self._process_register_range(self.register_map.TOTALINV_E, self.register_map.PV3_C)  # R96 - R114

        self._process_register_range(self.register_map.TOTALINV_E, self.register_map.DAILYPV_E)  # R96 - R108
        self._process_register_range(self.register_map.PV1_V, self.register_map.PV3_C)  # R109 - R114

        self._process_register_range(self.register_map.GRIDL1N_V, self.register_map.GRIDLMTL1_P)  # R150 - R170
        self._process_register_range(self.register_map.GRIDLMTL2_P, self.register_map.PV3_P)  # R171 - R188
        self._process_register_range(self.register_map.BATT_P, self.register_map.GEN_FREQ)  # R190 - R196

    def _post_process_register_map_entries(self):
        """Post-process the register map entries after reading the raw values from the inverter."""
        for entry in self.register_map.entries_post_process:
            entry.post_process(self.register_map)

    def _handle_results(self) -> dict[str, RegisterValue]:
        """Handle both success and failure cases.

        If there was a processing error, then return the last known values if they are not too old,
        otherwise return an error message.

        Changed the logic to return the last known values in the case of a complete read failure,
        as long as they are not too stale, rather than returning no data at all."""

        data: dict[str, RegisterValue] = self.register_map.as_dict()

        if self.register_map.is_error():
            # Check if we have last known values and they're not too old
            if (
                self.last_successful_data
                and self.last_successful_timestamp
                and (datetime.now() - self.last_successful_timestamp).total_seconds() < self.max_stale_data_age
            ):
                data = self.last_successful_data
                _LOGGER.warning(
                    "Using last known values (%.1f seconds old) due to communication error",
                    (datetime.now() - self.last_successful_timestamp).total_seconds(),
                )
            else:
                _LOGGER.error(
                    "No recent valid data available (last successful read: %s)",
                    self.last_successful_timestamp.strftime("%Y-%m-%d %H:%M:%S") if self.last_successful_timestamp else "never",
                )
                data = {"faultmsg": "Communication lost with inverter"}
        else:
            # Update the counter
            self.update_cnt = self.update_cnt + 1
            if self.update_cnt >= 65535:
                self.update_cnt = 0

            data["update_cnt"] = self.update_cnt

            # Store this successful reading
            self.last_successful_data = data.copy()
            self.last_successful_timestamp = datetime.now()

        return data

    def _process_register_range(self, start_register: RegisterMapEntry, end_register: RegisterMapEntry | None = None):
        """Read the holding registers and decode the vlues for a range of RegisterMapEntry objects."""

        if end_register is None:
            end_register = start_register

        register_count = end_register.address + end_register.register_length - start_register.address

        # Read the registers from the inverter
        modbus_response = self._read_holding_registers(address=start_register.address, count=register_count)

        # Process the Modbus response and update the register map entries with the decoded values if successful,
        # otherwise set error state on the register map
        if modbus_response.isError():
            _LOGGER.error(
                "Processing registers %d-%d failed!", start_register.address, end_register.address + end_register.register_length - 1
            )
            self.register_map.set_error()
            return

        decoder = SolArkBinaryPayloadDecoder.fromRegisters(modbus_response.registers)

        entries = self.register_map.entries_register_read_in_range(start_register, end_register)
        self._decode_register_map_entries(decoder, entries)

    def _decode_register_map_entries(self, decoder: SolArkBinaryPayloadDecoder, entries: Iterator[RegisterMapEntry]):
        """Decode the Modbus response registers and update the register map entries with the decoded values."""
        next_address: int | None = None

        for entry in entries:
            # Skip if there is a gap in the registers we want to process.
            if next_address is not None and entry.address != next_address:
                gap = entry.address - next_address
                decoder.skip_registers(gap)

            entry.register_value = self._decode_register_map_entry(decoder, entry)

            if entry.register_value is None:
                _LOGGER.error("Failed to decode register %s with data type %s", entry.address, entry.data_type)
                self.register_map.set_error()
                return

            next_address = entry.address + entry.register_length

    def _decode_register_map_entry(self, decoder: SolArkBinaryPayloadDecoder, entry: RegisterMapEntry) -> RegisterValue:
        """Decode a single register map entry using the specified decoder."""

        if entry.key == "dailypv_e":
            _LOGGER.debug("Starting decod of register %s", entry.key)

        if entry.data_type == DataType.STRING:
            register_value: RegisterValue = decoder.decode_string(entry.register_length * 2).decode("ascii")
        else:
            numeric_value: NumericValue
            if entry.data_type == DataType.INT16:
                numeric_value = decoder.decode_16bit_int()
            elif entry.data_type == DataType.UINT16:
                numeric_value = decoder.decode_16bit_uint()
            elif entry.data_type == DataType.INT32:
                numeric_value = decoder.decode_32bit_int()
            elif entry.data_type == DataType.UINT32:
                numeric_value = decoder.decode_32bit_uint()
            elif entry.data_type == DataType.INT64:
                numeric_value = decoder.decode_64bit_int()
            elif entry.data_type == DataType.UINT64:
                numeric_value = decoder.decode_64bit_uint()
            else:
                raise ModbusDecodeError(f"Failed to decode register {entry.address} having data type {entry.data_type})")

            if entry.key == "dailypv_e":
                _LOGGER.debug("Decoded raw value %d for register %s", numeric_value, entry.key)

            # Apply offset
            numeric_value -= entry.offset

            # Apply scale if needed
            if entry.scale != 1.0:
                numeric_value *= entry.scale

            register_value = numeric_value

        return register_value

    def _read_holding_registers(self, address: int, count: int) -> ModbusResponse:
        """Reads a block of holding registers from the inverter via Modbus

        Catch and handle common exceptions by returning error.
        Should not return NONE, and bubbles up ONLY unexpected exceptions.
        """
        result: ModbusResponse = self._client.read_holding_registers(address, count=count, device_id=self.device_id)

        if result.isError():
            code = getattr(result, "exception_code", None)
            if code:
                err = MODBUS_EXCEPTIONS.get(code, f"Unknown Modbus exception: {code}")
            else:
                err = str(result)

            _LOGGER.warning("Reading holding registers Modbus error: %s", err)

        return result
