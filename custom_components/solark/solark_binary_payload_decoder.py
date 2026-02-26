import warnings

from .binary_payload_decoder import BinaryPayloadDecoder


class SolArkBinaryPayloadDecoder(BinaryPayloadDecoder):
    """Custom BinaryPayloadDecoder to replace the deprecated one from pymodbus."""

    def skip_registers(self, nregisters):
        """Skip given number of registers."""
        self._pointer += nregisters * 2  # Each register is 2 bytes

    @classmethod
    def deprecate(cls, message: str | None = None):
        """Issue a deprecation warning for this class or method."""
        if message is None:
            message = f"{cls.__name__} is deprecated and may be removed in a future version."
        warnings.warn(message, category=DeprecationWarning, stacklevel=2)

    @classmethod
    def fromRegisters(cls, registers):  # pylint: disable=W0221
        """Simplify calls to the base class fromRegisters()
        All calls to this method in the original code were either 16 bit exclusive,
        or used wordorder="<" and byteorder=">", which is the default for this class.
        We can safely ignore the parameters and just call the base class method with the defaults,
        which will work for all the existing calls in the codebase.
        """
        return super().fromRegisters(registers, byteorder=">", wordorder="<")

    def decode_64bit_int(self):
        """Decode 64-bit signed integer."""
        return self._decode("!q", 8, use_word_unpack=True)

    def decode_64bit_uint(self):
        """Decode 64-bit unsigned integer."""
        return self._decode("!Q", 8, use_word_unpack=True)


class ModbusDecodeError(RuntimeError):
    """Raised when Modbus register decoding fails."""
