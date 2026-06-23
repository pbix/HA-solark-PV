from dataclasses import dataclass
from enum import Enum
from urllib.parse import urlparse


class ConnectionType(str, Enum):
    TCP = "tcp"
    SERIAL = "serial"


@dataclass
class SolArkConfig:
    # Common
    connection_type: ConnectionType
    device_id: int

    # TCP
    host: str | None
    port: int

    # Serial
    serial_port: str | None

    @classmethod
    def from_url(cls, connection_url: str):
        """
        Initialize the SolArkConfig object from a single url.

        The hostname can be a valid URL (e.g. 192.168.2.2) or a serial port name (e.g. /dev/ttyUSB0 or COM1).
        If the hostname is not a valid URL, it will be interpreted as a serial port name.

        The device ID is an optional parameter that can be specified as a query parameter in the hostname (e.g. 192.168.2.2/;3).
        If the device ID is not specified, it will default to 1.

        The connection type is determined based on the hostname. If the hostname is a valid URL, it will be interpreted as a TCP connection.
        If the hostname is a serial port name, it will be interpreted as a serial connection."""
        parsed = urlparse(f"//{connection_url}")

        # If it not a proper URL it might be a serial port.
        # This logic is tested to work with linux and windows serial port names,
        # port numbers and device_ids
        #
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

        # Default values
        device_id = 1
        host = None
        port = 502
        serial_port = None

        if (parsed.port is None) and ((parsed.hostname is None) or parsed.hostname.lower().startswith("com")):
            connection_type = ConnectionType.SERIAL
            serial_port = parsed.path.rstrip("/") + parsed.netloc
        else:
            connection_type = ConnectionType.TCP
            host = parsed.hostname
            port = parsed.port or 502

        device_id = 1
        if parsed.params.isdigit() and int(parsed.params) < 256:
            device_id = int(parsed.params)

        return cls(connection_type=connection_type, device_id=device_id, host=host, port=port, serial_port=serial_port)

