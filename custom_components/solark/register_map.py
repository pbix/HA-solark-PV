import logging
from dataclasses import dataclass
from enum import Enum, StrEnum
from typing import Any, Callable, Generic, Iterator, Optional, TypeVar, Union

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.const import (
    PERCENTAGE,
    EntityCategory,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfFrequency,
    UnitOfPower,
    UnitOfTemperature,
)

from .sensor_entity_description import SolArkModbusSensorEntityDescription

_LOGGER = logging.getLogger(__name__)


class BatteryChargeHelper(StrEnum):
    AH = "Ah"


# ----------------------------------
# Native Unit of Measurement Enum
# ----------------------------------
class NativeUnit(Enum):
    KWH = UnitOfEnergy.KILO_WATT_HOUR
    WATT = UnitOfPower.WATT
    V = UnitOfElectricPotential.VOLT
    A = UnitOfElectricCurrent.AMPERE
    AH = BatteryChargeHelper.AH
    CELSIUS = UnitOfTemperature.CELSIUS
    PERCENT = PERCENTAGE
    HZ = UnitOfFrequency.HERTZ
    NONE = None  # for sensors without a unit


# ----------------------------------
# Device Class Enum
# ----------------------------------
class DeviceClass(Enum):
    ENERGY = SensorDeviceClass.ENERGY
    POWER = SensorDeviceClass.POWER
    VOLTAGE = SensorDeviceClass.VOLTAGE
    CURRENT = SensorDeviceClass.CURRENT
    TEMPERATURE = SensorDeviceClass.TEMPERATURE
    BATTERY = SensorDeviceClass.BATTERY
    NONE = None  # for sensors without a device class


# ----------------------------------
# State Class Enum
# ----------------------------------
class StateClass(Enum):
    TOTAL = SensorStateClass.TOTAL
    TOTAL_INCREASING = SensorStateClass.TOTAL_INCREASING
    MEASUREMENT = SensorStateClass.MEASUREMENT
    NONE = None  # for sensors without a state class


# ----------------------------------
# Data Type Enum
# ----------------------------------
class DataType(Enum):
    INT16 = "int16"
    UINT16 = "uint16"
    INT32 = "int32"
    UINT32 = "uint32"
    INT64 = "int64"
    UINT64 = "uint64"
    STRING = "string"


RegisterValue = Union[int, float, str, None]
NumericValue = Union[int, float]
DIAGNOSTIC = EntityCategory.DIAGNOSTIC
# TODO - Add config entities
CONFIG = EntityCategory.CONFIG


# ----------------------------------
# Register Map Entry
# ----------------------------------
@dataclass()
class RegisterMapEntry:
    key: str
    data_type: DataType
    name: str
    source_is_register_read: bool = True  # True if value comes directly from register read, False if calculated from other values
    address: int = -1
    register_value: RegisterValue = (
        None  # This will hold the decoded value after reading registers, or the calculated value if source_is_register_read is False
    )
    icon: str = ""
    scale: float = 1.0
    offset: int = 0
    string_register_length: int | None = None  # Only needed for string registers to know how many registers to read
    native_unit_of_measurement: NativeUnit = NativeUnit.NONE
    device_class: DeviceClass = DeviceClass.NONE
    state_class: StateClass = StateClass.NONE
    entity_registry_enabled_default: bool = True
    entity_category: EntityCategory | None = None
    post_process_method: Optional[Callable[[Any, "RegisterMapEntry"], None]] = None
    description: str | None = None

    last_read_successful: bool = False

    def __post_init__(self):
        if self.source_is_register_read:
            # If reading directly from register, address must be non-negative
            if self.address < 0:
                raise ValueError(f"RegisterMapEntry {self.key} must have a non-negative address if source_is_register_read is True")

            # If reading directly from register, STRING type must have string_register_length defined
            if self.data_type == DataType.STRING and self.string_register_length is None:
                raise ValueError(f"STRING type RegisterMapEntry {self.key} must have string_register_length")

        else:
            # If not read from register, must have a post_process_method
            if self.post_process_method is None:
                raise ValueError(f"RegisterMapEntry {self.key} must have post_process_method if source_is_register_read is False")

            # If not read from register, address must be -1
            if self.address != -1:
                raise ValueError(f"RegisterMapEntry {self.key} should not have an address since it's not read directly from a register")

    def __add__(self, other: Union["RegisterMapEntry", NumericValue]) -> NumericValue:
        """Add this entry to another entry or numeric value."""
        self_val: NumericValue
        if isinstance(self.register_value, (int, float)):
            self_val = self.register_value
        else:
            raise TypeError(f"Cannot use non-numeric register_value {self.register_value}")

        if isinstance(other, RegisterMapEntry):
            if isinstance(other.register_value, (int, float)):
                return self_val + other.register_value
            else:
                raise TypeError(f"Cannot add non-numeric register_value {other.register_value}")
        elif isinstance(other, (int, float)):
            return self_val + other
        else:
            raise TypeError(f"Cannot add RegisterMapEntry with {type(other)}")

    def __radd__(self, other: NumericValue) -> NumericValue:
        """Support int/float + RegisterMapEntry"""
        if isinstance(other, (int, float)):
            if isinstance(self.register_value, (int, float)):
                return other + self.register_value
            else:
                raise TypeError(f"Cannot use non-numeric register_value {self.register_value}")
        return NotImplemented

    def __int__(self) -> int:
        if isinstance(self.register_value, (int, float)):
            return int(self.register_value)
        raise TypeError(f"Cannot convert non-numeric register_value {self.register_value} to int")

    def __float__(self) -> float:
        if isinstance(self.register_value, (int, float)):
            return float(self.register_value)
        raise TypeError(f"Cannot convert non-numeric register_value {self.register_value} to float")

    def post_process(self, register_map: Any) -> None:
        if self.post_process_method is not None:
            try:
                self.post_process_method(register_map, self)
            except Exception:
                _LOGGER.exception("Error post-processing register %s", self.key)

    @property
    def register_length(self) -> int:
        """Calculate the register count based on the data type, including string length if applicable."""
        if self.data_type in (DataType.INT16, DataType.UINT16):
            return 1
        if self.data_type in (DataType.INT32, DataType.UINT32):
            return 2
        if self.data_type in (DataType.INT64, DataType.UINT64):
            return 4
        if self.data_type == DataType.STRING:
            if not self.string_register_length:
                raise ValueError(f"STRING type missing string_register_length for {self.key}")
            if self.string_register_length < 1:
                raise ValueError(f"STRING with string_register_length < 1 for {self.key}")
            return self.string_register_length
        raise ValueError(f"Unknown DataType {self.data_type} for {self.key}")

    @classmethod
    def from_register_map_entry(self) -> SolArkModbusSensorEntityDescription:
        return SolArkModbusSensorEntityDescription(
            name=self.name,
            key=self.key,
            native_unit_of_measurement=self.native_unit_of_measurement.value,
            device_class=self.device_class.value,
            state_class=self.state_class.value,
            icon=self.icon or None,
            entity_registry_enabled_default=self.entity_registry_enabled_default,
            entity_category=self.entity_category,
            description=self.description,
        )


# ----------------------------------
# Type variable for the real subclass
# ----------------------------------
T = TypeVar("T", bound="RegisterMap")


# ----------------------------------
# Register Map
# ----------------------------------
@dataclass
class RegisterMap(Generic[T]):
    """Base class for register maps that collects RegisterMapEntry class attributes across inheritance."""

    def __init__(self):
        # Collect all RegisterMapEntry attributes from the class and parent classes
        entries_to_sort: dict[str, "RegisterMapEntry"] = {}

        # Collect all RegisterMapEntry attributes from the base and derived classes.
        # Iterate the class hierarchy (MRO) from base → derived so that derived
        # class entries override any entries with the same name from the base class.
        for cls in reversed(self.__class__.__mro__):
            for attr_name, attr_value in cls.__dict__.items():
                if isinstance(attr_value, RegisterMapEntry):
                    entries_to_sort[attr_name] = attr_value

        # Sorted list of entries by address
        self._sorted: list["RegisterMapEntry"] = sorted(entries_to_sort.values(), key=lambda e: e.address)

        # Ensure no overlapping address ranges
        prev = None
        for entry in self.entries_register_read:
            if prev is not None:
                prev_end = prev.address + prev.register_length - 1
                if entry.address <= prev_end:
                    raise ValueError(
                        f"Register overlap detected: "
                        f"{prev} [{prev.address}-{prev_end}] overlaps "
                        f"{entry} [{entry.address}-{entry.address + entry.register_length - 1}]"
                    )
            prev = entry

        # Error flag
        self._error: bool = False

    # TODO - deduplicate this with __init__ and __init_subclass__. We should be able to just do this in __init_subclass__ and
    #  then the instance can just copy the class-level _map and _sorted to instance-level variables if needed.
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Collect all RegisterMapEntry class attributes
        entries = {name: value for name, value in cls.__dict__.items() if isinstance(value, RegisterMapEntry)}
        cls._map = entries
        cls._sorted = sorted(entries.values(), key=lambda e: e.address)
        cls._error = False

    def get_entry(self, key: str) -> "RegisterMapEntry | None":
        """Get a RegisterMapEntry by key."""
        return self._map.get(key)

    def is_error(self) -> bool:
        """Return whether an error occurred."""
        return self._error

    def set_error(self, value: bool = True):
        """Set error flag."""
        self._error = value

    def __getitem__(self, key: str) -> "RegisterMapEntry":
        return self._map[key]

    def __iter__(self) -> Iterator["RegisterMapEntry"]:
        return iter(self._sorted)

    def as_dict(self) -> dict[str, "RegisterValue"]:
        return {entry.key: entry.register_value for entry in self._sorted}

    def is_empty(self) -> bool:
        return len(self._map) == 0

    def sensor_types(self) -> dict[str, SolArkModbusSensorEntityDescription]:
        return {entry.key: entry.from_register_map_entry() for entry in self._sorted}

    def init(self):
        """Initialize the register map before reading registers. This can be used to reset any calculated values or error flags."""
        self.set_error(False)
        for entry in self._sorted:
            entry.register_value = None
            entry.last_read_successful = False

    #
    # Iterators
    #
    @property
    def entries_register_read(self) -> Iterator[RegisterMapEntry]:
        """Return all register map entries that have a post_process_method."""
        for entry in self:
            if entry.source_is_register_read:
                yield entry

    @property
    def entries_post_process(self) -> Iterator[RegisterMapEntry]:
        """Return all register map entries that have a post_process_method."""
        for entry in self:
            if entry.post_process_method is not None:
                yield entry

    @property
    def entries_sensor_only(self) -> Iterator[RegisterMapEntry]:
        """Return all register map entries that are sensor only."""
        for entry in self._sorted:
            if not entry.source_is_register_read:
                yield entry

    def entries_register_read_in_range(self, start: RegisterMapEntry, end: RegisterMapEntry | None = None) -> Iterator[RegisterMapEntry]:
        """Yield registers from start to end (inclusive). If end is None, yield only start."""
        end = end or start  # if end is None, just use start

        for entry in self.entries_register_read:
            if entry.address < start.address:
                continue
            if entry.address > end.address:
                break
            yield entry
