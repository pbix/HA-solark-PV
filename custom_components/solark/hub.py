"""SolArk Modbus Hub."""

from datetime import datetime, timedelta
import logging
import threading
from urllib.parse import urlparse

import pymodbus
from pymodbus.exceptions import ConnectionException, ModbusException, ModbusIOException
from voluptuous.validators import Number

from homeassistant.core import CALLBACK_TYPE, HomeAssistant, callback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .binary_payload_decoder import BinaryPayloadDecoder
from .const import MODBUS_EXCEPTIONS
from .fault_info import translate_fault_code_to_messages

_LOGGER = logging.getLogger(__name__)

# There is another breaking change starting at pymodbus v3.4.7
# HomeAssistant switched to pymodbus v3.4.7 starting at 2025.1.
#
# Logger output printing pymodbus.__version__
# 025-01-12 19:30:14.751 INFO (ImportExecutor_0) [custom_components.solark_modbus.hub] __version__ 3.7.4

prior347 = False
pyversion = list(map(int, pymodbus.__version__.split(".")))

# _LOGGER.info("__version__ %i %i  %i",pyversion[0], pyversion[1], pyversion[2])

if hasattr(pymodbus, "__version__") and (
    ((pyversion[0] == 3) and (pyversion[1] <= 1)) or (pyversion[0] <= 2)
):
    from pymodbus.register_read_message import ReadHoldingRegistersResponse

    prior347 = True
elif hasattr(pymodbus, "__version__") and ((pyversion[0] == 3) and (pyversion[1] < 8)):
    from pymodbus.pdu.register_read_message import ReadHoldingRegistersResponse
else:
    from pymodbus.pdu.register_message import ReadHoldingRegistersResponse


class SolArkModbusHub(DataUpdateCoordinator[dict]):
    """Thread safe wrapper class for pymodbus."""

    # Maximum age of last successful reading before considering it stale (in seconds)
    MAX_DATA_AGE = 300  # 5 minutes

    def __init__(
        self, hass: HomeAssistant, name: str, hostname: str, scan_interval: Number
    ) -> None:
        """Initialize the Modbus hub."""
        super().__init__(
            hass,
            _LOGGER,
            name=name,
            update_interval=timedelta(seconds=scan_interval),
        )

        self.slaveno = 1
        self.update_cnt = 0
        self.last_successful_data = {}
        self.last_successful_timestamp = None

        # Break the entered hostnames into its component parts.
        parsed = urlparse(f"//{hostname}")

        # There is a breaking change in pymodbus starting with version 3.0.0
        # HomeAssistant switched to pymodbus v3.1.1 starting at 2023.2.  The
        # below code makes sure that this integration will work with either version
        # of pymodbus.
        if hasattr(pymodbus, "__version__") and (pyversion[0] == 2):
            from pymodbus.client.sync import ModbusTcpClient, ModbusSerialClient
        else:
            from pymodbus.client import ModbusTcpClient, ModbusSerialClient

        # If it not a proper URL it might be a serial port.
        # This logic is tested to work with linux and windows serial port names, port numbers and slaveIDs
        # Tested URLs:
        #  192.168.2.2
        #  192.268.2.2:502
        #  192.168.2.2:502/;3
        #  192.168.2.2/;3
        #  /dev/ttyUSB0
        #  /dev/ttyUDB0/;3
        #  COM1
        #  COM1/;3
        #
        if (parsed.port is None) and (
            (parsed.hostname is None) or (parsed.hostname[0:3] == "com")
        ):
            if prior347:
                self._client = ModbusSerialClient(
                    method="rtu",
                    port=parsed.path.rstrip("/") + parsed.netloc,
                    baudrate=9600,
                    stopbits=1,
                    bytesize=8,
                    timeout=5,
                )
            else:
                self._client = ModbusSerialClient(
                    port=parsed.path.rstrip("/") + parsed.netloc,
                    baudrate=9600,
                    stopbits=1,
                    bytesize=8,
                    timeout=5,
                )
        else:
            if parsed.port is None:
                localport = 502
            else:
                localport = parsed.port

            self._client = ModbusTcpClient(
                host=parsed.hostname, port=localport, timeout=5
            )

        # See if a valid, non-default slave number was specified
        if (parsed.params.isdigit()) and (int(parsed.params) < 256):
            self.slaveno = int(parsed.params)

        # Make a connection request since for some reasons pymodbus v3.5.0 no longer automatically does this for us.
        # Looks like it is fixed in v3.5.2 but who wants to wait.
        self._client.connect()

        self._lock = threading.Lock()
        self.inverter_data: dict = {}
        self.data: dict = {}

    @callback
    def async_remove_listener(self, update_callback: CALLBACK_TYPE) -> None:
        """Remove data update listener."""
        # super().async_remove_listener(update_callback)
        self._listeners.pop(update_callback, None)

        # No listeners left then close connection
        if not self._listeners:
            self.close()

    def close(self) -> None:
        """Disconnect client."""
        with self._lock:
            self._client.close()

    def _read_holding_registers(
        self, unit, address, count
    ) -> ReadHoldingRegistersResponse:
        """Read holding registers.

        Catch and handle common exceptions by returning error.
        Should not return NONE, and bubbles up ONLY unexpected exceptions.
        """
        with self._lock:
            result: ReadHoldingRegistersResponse
            try:
                # pymodbus v3.8.3 seems to have changed to force keyword arguments.
                if hasattr(pymodbus, "__version__") and (pyversion[0] == 2):
                    result = self._client.read_holding_registers(address, count, unit)

                # pymodbus v3.10 changed keyword slave to device_id.
                if (
                    hasattr(pymodbus, "__version__")
                    and (pyversion[0] == 3)
                    and (pyversion[1] < 10)
                ):
                    result = self._client.read_holding_registers(
                        address, count=count, slave=unit
                    )

                result = self._client.read_holding_registers(
                    address, count=count, device_id=unit
                )

                if result.isError():
                    code = getattr(result, "exception_code", None)
                    if code:
                        err = MODBUS_EXCEPTIONS.get(
                            code, f"Unknown Modbus exception: {code}"
                        )
                    else:
                        err = str(result)

                    _LOGGER.warning("Reading holding registers Modbus error: %s", err)
                else:
                    # Success
                    return result

            except ModbusIOException as e:
                return self._get_exception_result(e)
            except ConnectionException as e:
                return self._get_exception_result(e)
            except ModbusException as e:
                return self._get_exception_result(e)

    def _get_exception_result(self, exception) -> ReadHoldingRegistersResponse:
        if isinstance(exception, ModbusIOException):
            err = f"Reading holding registers I/O error: {exception}"
        elif isinstance(exception, ConnectionException):
            err = f"Reading holding registers connection error: {exception}"
        elif isinstance(exception, ModbusException):
            err = f"Reading holding registers Modbus exception: {exception}"
        else:
            err = f"Unexpected error reading holding registers: {exception}"

        _LOGGER.warning("Reading holding registers error: %s", err)

        result = ReadHoldingRegistersResponse(0)
        result.isError = lambda: True
        result.error_message = ModbusException(err)
        return result

    async def _async_update_data(self) -> dict:
        """Read the data from the inverter and return it as a dictionary."""
        realtime_data = {}
        try:
            if not self.inverter_data:  # Inverter serial number is only fetched once
                self.inverter_data = await self.hass.async_add_executor_job(
                    self.read_modbus_inverter_data
                )
            # Read realtime data
            realtime_data = await self.hass.async_add_executor_job(
                self.read_modbus_realtime_data
            )
            if not realtime_data:
                # Check if we have last known values and they're not too old
                if (
                    self.last_successful_data
                    and self.last_successful_timestamp
                    and (
                        datetime.now() - self.last_successful_timestamp
                    ).total_seconds()
                    < self.MAX_DATA_AGE
                ):
                    realtime_data = self.last_successful_data
                    _LOGGER.warning(
                        "Using last known values (%.1f seconds old) due to communication error",
                        (
                            datetime.now() - self.last_successful_timestamp
                        ).total_seconds(),
                    )
                else:
                    _LOGGER.error(
                        "No recent valid data available (last successful read: %s)",
                        self.last_successful_timestamp.strftime("%Y-%m-%d %H:%M:%S")
                        if self.last_successful_timestamp
                        else "never",
                    )
                    realtime_data = {"faultmsg": "Communication lost with inverter"}
        except Exception as e:
            # Log unexpected exceptions
            _LOGGER.exception("Unexpected error reading inverter data: %s", e)
            realtime_data = {"faultmsg": "Unexpected error"}

        # Return combined data safely
        return {**self.inverter_data, **realtime_data}

    def read_modbus_inverter_data(self) -> dict:
        """Read the inverter data and return it as a dictionary."""
        inverter_data = self._read_holding_registers(
            unit=self.slaveno, address=3, count=5
        )

        if inverter_data.isError():
            _LOGGER.error("Reading inverter data failed!")
            return {}

        data = {}
        decoder = BinaryPayloadDecoder.fromRegisters(
            inverter_data.registers, byteorder=">"
        )

        data["sn"] = decoder.decode_string(10).decode("ascii")

        return data

    def read_modbus_realtime_data(self) -> dict:
        """Read the real-time data from the inverter and return it as a dictionary."""

        # Empty dictionary is returned if errors prevented the reading of any data
        data = {}
        updated = False

        realtime_data = self._read_holding_registers(
            unit=self.slaveno, address=60, count=21
        )
        if not realtime_data.isError():
            decoder = BinaryPayloadDecoder.fromRegisters(
                realtime_data.registers, byteorder=">", wordorder="<"
            )

            data["dailyinv_e"] = decoder.decode_16bit_int() / 10.0
            decoder.skip_bytes(4)
            data["totalgrid_e"] = decoder.decode_32bit_int() / 10.0
            decoder.skip_bytes(10)
            data["daybattc_e"] = decoder.decode_16bit_uint() / 10.0
            data["daybattd_e"] = decoder.decode_16bit_uint() / 10.0
            decoder.skip_bytes(8)
            data["dailygridbuy_e"] = decoder.decode_16bit_uint() / 10.0
            data["dailygridsell_e"] = decoder.decode_16bit_uint() / 10.0
            decoder.skip_bytes(2)
            data["gridfreq"] = decoder.decode_16bit_uint() / 100.0
            updated = True

        realtime_data = self._read_holding_registers(
            unit=self.slaveno, address=84, count=8
        )
        if not realtime_data.isError():
            decoder = BinaryPayloadDecoder.fromRegisters(
                realtime_data.registers, byteorder=">", wordorder="<"
            )

            data["dailyload_e"] = (
                decoder.decode_16bit_uint() / 10.0
            )  # R84 power through the breaker labeled "Load" on the inverter
            data["totalload_e"] = (
                decoder.decode_32bit_uint() / 10.0
            )  # R85 power through the breaker labeled "Load" on the inverter
            decoder.skip_bytes(6)
            data["dchstempc"] = (decoder.decode_16bit_uint() - 1000) / 10.0
            data["achstempc"] = (decoder.decode_16bit_uint() - 1000) / 10.0
            updated = True

        realtime_data = self._read_holding_registers(
            unit=self.slaveno, address=96, count=21
        )
        if not realtime_data.isError():
            decoder = BinaryPayloadDecoder.fromRegisters(
                realtime_data.registers, byteorder=">", wordorder="<"
            )

            data["totalinv_e"] = decoder.decode_32bit_int() / 10.0  # R98
            decoder.skip_bytes(10)

            low = decoder.decode_32bit_uint()  # R103-104
            high = decoder.decode_32bit_uint()  # R105-106
            flt = (high << 32) | low

            data["faultmsg"] = translate_fault_code_to_messages(flt)

            decoder.skip_bytes(2)

            data["dailypv_e"] = decoder.decode_16bit_uint() / 10.0  # R108
            data["pv1_v"] = decoder.decode_16bit_uint() / 10.0
            data["pv1_c"] = decoder.decode_16bit_uint() / 10.0
            data["pv2_v"] = decoder.decode_16bit_uint() / 10.0
            data["pv2_c"] = decoder.decode_16bit_uint() / 10.0
            data["pv3_v"] = decoder.decode_16bit_uint() / 10.0
            data["pv3_c"] = decoder.decode_16bit_uint() / 10.0
            updated = True

        realtime_data = self._read_holding_registers(
            unit=self.slaveno, address=150, count=21
        )
        if not realtime_data.isError():
            decoder = BinaryPayloadDecoder.fromRegisters(
                realtime_data.registers, byteorder=">"
            )

            data["gridl1n_v"] = decoder.decode_16bit_uint() / 10.0  # R150
            data["gridl2n_v"] = decoder.decode_16bit_uint() / 10.0
            data["gridl1l2_v"] = decoder.decode_16bit_uint() / 10.0
            data["gridrelay_v"] = decoder.decode_16bit_uint() / 10.0
            data["invl1n_v"] = decoder.decode_16bit_uint() / 10.0
            data["invl2n_v"] = decoder.decode_16bit_uint() / 10.0
            data["invl1l2_v"] = decoder.decode_16bit_uint() / 10.0
            data["loadl1n_v"] = decoder.decode_16bit_uint() / 10.0
            data["loadl2n_v"] = decoder.decode_16bit_uint() / 10.0
            decoder.skip_bytes(2)
            data["gridl1_c"] = decoder.decode_16bit_int() / 100.0  # R160
            data["gridl2_c"] = decoder.decode_16bit_int() / 100.0
            data["extlmtl1_c"] = decoder.decode_16bit_int() / 100.0
            data["extlmtl2_c"] = decoder.decode_16bit_int() / 100.0
            data["invl1_c"] = decoder.decode_16bit_int() / 100.0
            data["invl2_c"] = decoder.decode_16bit_int() / 100.0
            data["gen_p"] = decoder.decode_16bit_int()
            data["gridl1_p"] = decoder.decode_16bit_int()
            data["gridl2_p"] = decoder.decode_16bit_int()
            data["grid_p"] = decoder.decode_16bit_int()
            data["gridlmtl1_p"] = decoder.decode_16bit_int()  # R170
            updated = True

        realtime_data = self._read_holding_registers(
            unit=self.slaveno, address=171, count=18
        )
        if not realtime_data.isError():
            decoder = BinaryPayloadDecoder.fromRegisters(
                realtime_data.registers, byteorder=">"
            )

            data["gridlmtl2_p"] = decoder.decode_16bit_int()  # R171
            data["gridext_p"] = decoder.decode_16bit_int()
            data["invl1_p"] = decoder.decode_16bit_int()
            data["invl2_p"] = decoder.decode_16bit_int()
            data["inv_p"] = decoder.decode_16bit_int()
            data["loadl1_p"] = decoder.decode_16bit_int()
            data["loadl2_p"] = decoder.decode_16bit_int()
            data["load_p"] = decoder.decode_16bit_int()
            data["loadl1_c"] = decoder.decode_16bit_int() / 100.0
            data["loadl2_c"] = decoder.decode_16bit_int() / 100.0
            data["genl1l2_v"] = decoder.decode_16bit_uint() / 10.0  # R181
            data["batttempc"] = (decoder.decode_16bit_uint() - 1000) / 10.0
            data["batt_v"] = decoder.decode_16bit_uint() / 100.0
            data["batt_soc"] = decoder.decode_16bit_uint()
            decoder.skip_bytes(2)
            pv1_p = decoder.decode_16bit_uint()
            pv2_p = decoder.decode_16bit_uint()
            pv3_p = decoder.decode_16bit_uint()
            data["pv1_p"] = pv1_p
            data["pv2_p"] = pv2_p
            data["pv3_p"] = pv3_p
            data["pv_p"] = pv1_p + pv2_p + pv3_p
            updated = True

        realtime_data = self._read_holding_registers(
            unit=self.slaveno, address=190, count=6
        )
        if not realtime_data.isError():
            decoder = BinaryPayloadDecoder.fromRegisters(
                realtime_data.registers, byteorder=">"
            )

            data["batt_p"] = decoder.decode_16bit_int()  # R190
            data["batt_c"] = decoder.decode_16bit_int() / 100.0
            decoder.skip_bytes(4)
            data["grid_rly"] = "Closed" if decoder.decode_16bit_int() == 1 else "Open"
            updated = True

        # If there was no response to any read request then return no data.
        if not updated:
            return {}

        # Update the counter
        self.update_cnt = self.update_cnt + 1
        if self.update_cnt >= 65535:
            self.update_cnt = 0

        data["update_cnt"] = self.update_cnt

        # Store this successful reading
        self.last_successful_data = data.copy()
        self.last_successful_timestamp = datetime.now()
        return data
