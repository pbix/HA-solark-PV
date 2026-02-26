"""Since pymodbus BinaryPayloadDecoder is deprecated, create our own to replace it."""

from array import array
from struct import pack, unpack
import warnings

from pymodbus.exceptions import ParameterException
from pymodbus.logging import Log


class BinaryPayloadDecoder:
    """Utility to decode payload messages from a modbus response message.

    A simple wrapper around the struct module that saves time looking up
    format strings. Example::

        decoder = BinaryPayloadDecoder(payload)
        first   = decoder.decode_8bit_uint()
        second  = decoder.decode_16bit_uint()
    """

    @classmethod
    def deprecate(cls):
        """Log warning."""

    def __init__(self, payload, byteorder="<", wordorder="<"):
        """Initialize a new payload decoder.

        :param payload: The payload to decode with
        :param byteorder: The endianness of the payload
        :param wordorder: The endianness of the word (when wordcount is >= 2)
        """
        # self.deprecate()
        self._payload = payload
        self._pointer = 0x00
        self._byteorder = byteorder
        self._wordorder = wordorder

    @classmethod
    def fromRegisters(
        cls,
        registers,
        byteorder="<",
        wordorder=">",
    ):
        """Initialize a payload decoder.

        With the result of reading a collection of registers from a modbus device.

        The registers are treated as a list of 2 byte values.
        We have to do this because of how the data has already
        been decoded by the rest of the library.

        :param registers: The register results to initialize with
        :param byteorder: The Byte order of each word
        :param wordorder: The endianness of the word (when wordcount is >= 2)
        :returns: An initialized PayloadDecoder
        :raises ParameterException:
        """
        cls.deprecate()
        Log.debug("{}", registers)
        if isinstance(registers, list):  # repack into flat binary
            payload = pack(f"!{len(registers)}H", *registers)
            return cls(payload, byteorder, wordorder)
        raise ParameterException("Invalid collection of registers supplied")

    def _unpack_words(self, handle) -> bytes:
        """Unpack words based on the word order and byte order.

        # ---------------------------------------------- #
        # Unpack in to network ordered unsigned integer  #
        # Change Word order if little endian word order  #
        # Pack values back based on correct byte order   #
        # ---------------------------------------------- #
        """
        if "<" in {self._byteorder, self._wordorder}:
            handle = array("H", handle)
            if self._byteorder == "<":
                handle.byteswap()
            if self._wordorder == "<":
                handle.reverse()
            handle = handle.tobytes()
        Log.debug("handle: {}", handle)
        return handle

    def _decode(self, fmt: str, size: int, use_word_unpack: bool = False):
        """Decode an integer from the payload.

        Args:
            fmt: The struct format string for unpacking (e.g., 'B', 'H', 'i').
            size: Number of bytes to consume from the payload.
            use_word_unpack: Whether to call _unpack_words before unpacking.

        Returns:
            The decoded integer value.
        """
        start = self._pointer
        self._pointer += size
        handle = self._payload[start : self._pointer]

        if use_word_unpack:
            handle = self._unpack_words(handle)

        return unpack(fmt, handle)[0]

    # Unsigned integers
    # def decode_8bit_uint(self):
    #     """Decode 8-bit unsigned integer."""
    #     return self._decode(self._byteorder + "B", 1)

    def decode_16bit_uint(self):
        """Decode 16-bit unsigned integer."""
        return self._decode(self._byteorder + "H", 2)

    def decode_32bit_uint(self):
        """Decode 32-bit unsigned integer."""
        return self._decode("!I", 4, use_word_unpack=True)

    # Signed integers
    # def decode_8bit_int(self):
    #     """Decode 8-bit signed integer."""
    #     return self._decode(self._byteorder + "b", 1)

    def decode_16bit_int(self):
        """Decode 16-bit signed integer."""
        return self._decode(self._byteorder + "h", 2)

    def decode_32bit_int(self):
        """Decode 32-bit signed integer."""
        return self._decode("!i", 4, use_word_unpack=True)

    # Strings and skipping
    def decode_string(self, size=1):
        """Decode bytes string of given size."""
        start = self._pointer
        self._pointer += size
        return self._payload[start : self._pointer]

    def skip_bytes(self, nbytes):
        """Skip given number of bytes."""
        warnings.warn("skip_bytes is deprecated.", category=DeprecationWarning, stacklevel=2)
        self._pointer += nbytes
