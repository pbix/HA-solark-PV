"""Read-only, thread-safe, and async wrapper for PyModbus >=3.1.1 with full backwards compatibility.

Provides:
- Automatic client import handling for TCP and Serial
- Automatic keyword argument mapping for slave/device_id
- Thread-safe read/write operations
- Normalized response object with `.registers` and `.isError()`

Home Assistant Version  Pymodbus Version   Python Version
2023.2                  3.1.1              3.10
2024.3                  3.6.5 - 3.6.6      3.12
2024.4                  3.6.6 - 3.6.7      3.12
2025.1                  3.7.4              3.12
2025.2                  3.8.3              3.13
2025.7                  3.9.2              3.13
2025.9                  3.11.0 - 3.11.1    3.13
2025.10                 3.11.2             3.13

"""

from __future__ import annotations

import asyncio
import threading

import pymodbus
from packaging import version
from pymodbus.exceptions import ConnectionException, ModbusException, ModbusIOException

# ---- Version parsing ----
PYMODBUS_VERSION = version.parse(pymodbus.__version__)

# ---- Version flags ----
IS_PRIOR_TO_V3_5_0 = PYMODBUS_VERSION < version.parse("3.5.0")  # noqa: SIM300
IS_PRIOR_TO_V3_10_0 = PYMODBUS_VERSION < version.parse("3.10.0")  # noqa: SIM300

# ---- Client imports ----
if IS_PRIOR_TO_V3_5_0:
    # Older PyModbus before 3.5 requires method="rtu"
    from pymodbus.client import ModbusSerialClient as OldModbusSerialClient
    from pymodbus.client import ModbusTcpClient
else:
    from pymodbus.client import ModbusSerialClient, ModbusTcpClient


# ---- Response abstraction ----
class ModbusResponse:
    """Thread-safe wrapper for Modbus read responses for PyModbus 3.1.1 → current."""

    __slots__ = ("_response",)

    def __init__(self, response: object | None) -> None:
        """Initialize ModbusResponse with a PyModbus response object."""
        self._response = response

    @property
    def registers(self) -> list[int] | None:
        """Return the list of registers or None if unavailable."""
        return getattr(self._response, "registers", None)

    def isError(self) -> bool:  # pylint: disable=invalid-name
        """Return True if the response indicates an error."""
        if self._response is None:
            return True

        if hasattr(self._response, "isError"):
            return self._response.isError()  # type: ignore[call-arg] optional if needed

        # If no 'isError' method, consider it an error if it has no 'registers'
        return not hasattr(self._response, "registers")

    def get_exception(self) -> Exception | None:
        """Return the exception if the response contains one."""
        return getattr(self._response, "error_message", None)

    def __repr__(self) -> str:
        """Return a string representation of the ModbusResponse."""
        return f"<ModbusResponse error={self.isError()} registers={self.registers} exception={self.get_exception()}>"


class ModbusResponseError(ModbusResponse):
    """Represents an error condition."""

    __slots__ = ("_exception",)

    def __init__(self, exception: Exception) -> None:
        """Initialize a ModbusResponseError with an exception."""
        self._exception = exception
        super().__init__(None)

    def isError(self) -> bool:  # pylint: disable=invalid-name
        """Return True if the response indicates an error."""
        return True

    def get_exception(self) -> Exception:
        """Return the exception."""
        return self._exception


class ModbusClientWrapper:
    """Thread-safe and async wrapper for Modbus TCP/Serial."""

    __slots__ = ("_client", "_lock")

    def __init__(
        self,
        host: str | None = None,
        port: int = 502,
        serial_port: str | None = None,
        baudrate: int = 9600,
    ) -> None:
        """Create a Modbus client wrapper (TCP or Serial)."""
        self._lock = threading.Lock()

        if serial_port is not None:
            if IS_PRIOR_TO_V3_5_0:
                self._client = OldModbusSerialClient(  # pylint: disable=E1123
                    method="rtu",  # type: ignore[call-arg]
                    port=serial_port,
                    baudrate=baudrate,
                    timeout=5,
                )
            else:
                self._client = ModbusSerialClient(port=serial_port, baudrate=baudrate, timeout=5)
        elif host is not None:
            self._client = ModbusTcpClient(host=host, port=port, timeout=5)
        else:
            raise ValueError("Either host or serial_port must be provided")

        if not self._client.connect():
            raise ConnectionException("Modbus connection failed")

    # ---- Sync read ----
    def read_holding_registers(self, address: int, count: int, device_id: int) -> ModbusResponse:
        """Read holding registers in a thread-safe way."""
        with self._lock:
            try:
                device_kw = self._get_device_id_param_name(device_id)

                resp = self._client.read_holding_registers(address=address, count=count, **device_kw)  # type: ignore[arg-type]
                return ModbusResponse(resp)
            except (ModbusIOException, ConnectionException, ModbusException) as exc:
                return ModbusResponseError(exc)

    # ---- Async helper ----
    async def async_read_holding_registers(self, address: int, count: int, device_id: int) -> ModbusResponse:
        """Async wrapper for read_holding_registers."""
        # TODO - Move to real async.  Eliminate run_in_executor calls.
        #  This will require a move to pymodbus >= 3.5 thus Home Assistant 2024.3 or later
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self.read_holding_registers, address, count, device_id)

    # ---- Helper for slave/device_id ------
    def _get_device_id_param_name(self, device_id: int) -> dict[str, int]:
        """Return the correct keyword argument for PyModbus >=3.1.1."""
        if IS_PRIOR_TO_V3_10_0:
            return {"slave": device_id}  # 3.1.1 → 3.9.x
        return {"device_id": device_id}  # 3.10+

    # ---- Close client ----
    def close(self) -> None:
        """Close the underlying client."""
        with self._lock:
            self._client.close()
