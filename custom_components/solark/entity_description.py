"""Entity descriptions for SolArk Modbus."""
from dataclasses import dataclass
from homeassistant.helpers.entity import EntityDescription

@dataclass(kw_only=True, frozen=True)
class SolArkModbusEntityDescription(EntityDescription):
    """Base class for SolArk Modbus entity descriptions."""
    address: int = -1
    scale: float = 1.0
