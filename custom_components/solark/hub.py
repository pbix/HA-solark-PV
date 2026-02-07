"""SolArk Modbus Hub"""
from datetime import timedelta, datetime
import logging
import threading
import pymodbus
from array import array
from urllib.parse import urlparse

from homeassistant.core import CALLBACK_TYPE, callback, HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from pymodbus.client import ModbusSerialClient, ModbusTcpClient
from pymodbus.exceptions import ConnectionException, ParameterException
from pymodbus.logging import Log
from struct import pack, unpack
from voluptuous.validators import Number
from .const import FAULT_MESSAGES

_LOGGER = logging.getLogger(__name__)

#There is another breaking change starting at pymodbus v3.4.7
#HomeAssistant switched to pymodbus v3.4.7 starting at 2025.1. 
#
#Logger output printing pymodbus.__version__
# 025-01-12 19:30:14.751 INFO (ImportExecutor_0) [custom_components.solark_modbus.hub] __version__ 3.7.4

prior347=False
pyversion = list(map(int, pymodbus.__version__.split('.')))

#_LOGGER.info("__version__ %i %i  %i",pyversion[0], pyversion[1], pyversion[2])

if hasattr(pymodbus,'__version__') and ( ((pyversion[0] == 3) and (pyversion[1] <= 1)) or (pyversion[0] <= 2)):
   from pymodbus.register_read_message import ReadHoldingRegistersResponse
   prior347 = True
elif hasattr(pymodbus,'__version__') and ((pyversion[0] == 3) and (pyversion[1] < 8)):
   from pymodbus.pdu.register_read_message import ReadHoldingRegistersResponse
else:
   from pymodbus.pdu.register_message import ReadHoldingRegistersResponse

#Since pymodbus BinaryPayloadDecoder is deprecated, create our own to replace it.
class BinaryPayloadDecoder:
    """A utility that helps decode payload messages from a modbus response message.

    It really is just a simple wrapper around
    the struct module, however it saves time looking up the format
    strings. What follows is a simple example::

        decoder = BinaryPayloadDecoder(payload)
        first   = decoder.decode_8bit_uint()
        second  = decoder.decode_16bit_uint()
    """

    @classmethod
    def deprecate(cls):
        """Log warning."""

    def __init__(self, payload, byteorder='<', wordorder='<'):
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
        byteorder='<',
        wordorder='>',
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
        if '<' in {self._byteorder, self._wordorder}:
            handle = array("H", handle)
            if self._byteorder == '<':
                handle.byteswap()
            if self._wordorder == '<':
                handle.reverse()
            handle = handle.tobytes()
        Log.debug("handle: {}", handle)
        return handle

    def decode_8bit_uint(self):
        """Decode a 8 bit unsigned int from the buffer."""
        # self.deprecate()
        self._pointer += 1
        fstring = self._byteorder + "B"
        handle = self._payload[self._pointer - 1 : self._pointer]
        return unpack(fstring, handle)[0]

    def decode_16bit_uint(self):
        """Decode a 16 bit unsigned int from the buffer."""
        # self.deprecate()
        self._pointer += 2
        fstring = self._byteorder + "H"
        handle = self._payload[self._pointer - 2 : self._pointer]
        return unpack(fstring, handle)[0]

    def decode_32bit_uint(self):
        """Decode a 32 bit unsigned int from the buffer."""
        # self.deprecate()
        self._pointer += 4
        fstring = "I"
        handle = self._payload[self._pointer - 4 : self._pointer]
        handle = self._unpack_words(handle)
        return unpack("!" + fstring, handle)[0]

    def decode_8bit_int(self):
        """Decode a 8 bit signed int from the buffer."""
        # self.deprecate()
        self._pointer += 1
        fstring = self._byteorder + "b"
        handle = self._payload[self._pointer - 1 : self._pointer]
        return unpack(fstring, handle)[0]

    def decode_16bit_int(self):
        """Decode a 16 bit signed int from the buffer."""
        # self.deprecate()
        self._pointer += 2
        fstring = self._byteorder + "h"
        handle = self._payload[self._pointer - 2 : self._pointer]
        return unpack(fstring, handle)[0]

    def decode_32bit_int(self):
        """Decode a 32 bit signed int from the buffer."""
        # self.deprecate()
        self._pointer += 4
        fstring = "i"
        handle = self._payload[self._pointer - 4 : self._pointer]
        handle = self._unpack_words(handle)
        return unpack("!" + fstring, handle)[0]

    def decode_string(self, size=1):
        """Decode a string from the buffer.

        :param size: The size of the string to decode
        """
        # self.deprecate()
        self._pointer += size
        return self._payload[self._pointer - size : self._pointer]

    def skip_bytes(self, nbytes):
        """Skip n bytes in the buffer.

        :param nbytes: The number of bytes to skip
        """
        # self.deprecate()
        self._pointer += nbytes


class SolArkModbusHub(DataUpdateCoordinator[dict]):
    """Thread safe wrapper class for pymodbus."""

    # Maximum age of last successful reading before considering it stale (in seconds)
    MAX_DATA_AGE = 300  # 5 minutes

    def __init__(
        self,
        hass: HomeAssistant,
        name: str,
        hostname: str,
        scan_interval: Number,
    ):
        """Initialize the Modbus hub."""
        super().__init__(
            hass,
            _LOGGER,
            name=name,
            update_interval=timedelta(seconds=scan_interval),
        )

        self.slaveno=1
        self.update_cnt=0
        self.last_successful_data = {}
        self.last_successful_timestamp = None

        #Break the entered hostnames into its component parts.
        parsed=urlparse(f'//{hostname}')
        
        #There is a breaking change in pymodbus starting with version 3.0.0
        #HomeAssistant switched to pymodbus v3.1.1 starting at 2023.2.  The
        #below code makes sure that this integration will work with either version
        #of pymodbus.
        if hasattr(pymodbus,'__version__') and (pyversion[0] == 2):
           from pymodbus.client.sync import ModbusTcpClient, ModbusSerialClient
        else:
           from pymodbus.client import ModbusTcpClient, ModbusSerialClient
       
        #If it not a proper URL it might be a serial port.
        #This logic is tested to work with linux and windows serial port names, port numbers and slaveIDs
        #Tested URLs:
        #  192.168.2.2
        #  192.268.2.2:502
        #  192.168.2.2:502/;3
        #  192.168.2.2/;3
        #  /dev/ttyUSB0
        #  /dev/ttyUDB0/;3
        #  COM1
        #  COM1/;3
        #
        if (parsed.port is None) and ((parsed.hostname is None) or (parsed.hostname[0:3] == "com" )):
            if (prior347):
               self._client = ModbusSerialClient(method='rtu',port=parsed.path.rstrip('/')+parsed.netloc,baudrate=9600,stopbits=1,bytesize=8,timeout=5)
            else:
               self._client = ModbusSerialClient(port=parsed.path.rstrip('/')+parsed.netloc,baudrate=9600,stopbits=1,bytesize=8,timeout=5)
        else:
            if (parsed.port is None):
                localport=502
            else:
                localport=parsed.port

            self._client = ModbusTcpClient(host=parsed.hostname, port=localport, timeout=5)

        #See if a valid, non-default slave number was specified
        if (parsed.params.isdigit()) and (int(parsed.params) < 256):
            self.slaveno = int(parsed.params)
            
        #Make a connection request since for some reasons pymodbus v3.5.0 no longer automatically does this for us.
        #Looks like it is fixed in v3.5.2 but who wants to wait.
        self._client.connect()
        
        self._lock = threading.Lock()
        self.inverter_data: dict = {}
        self.data: dict = {}

    @callback
    def async_remove_listener(self, update_callback: CALLBACK_TYPE) -> None:
        """Remove data update listener."""
        super().async_remove_listener(update_callback)

        """No listeners left then close connection"""
        if not self._listeners:
            self.close()

    def close(self) -> None:
        """Disconnect client."""
        with self._lock:
            self._client.close()

    def _read_holding_registers(
        self, unit, address, count
    ) -> ReadHoldingRegistersResponse:
        """Read holding registers."""

        with self._lock:
            try:

                #pymodbus v3.8.3 seems to have changed to force keyword arguments.
                if hasattr(pymodbus,'__version__') and (pyversion[0] == 2):
                   return self._client.read_holding_registers(address, count, unit)
                #pymodbus v3.10 changed keyword slave to device_id.
                elif hasattr(pymodbus,'__version__') and (pyversion[0] == 3) and (pyversion[1] < 10):
                   return self._client.read_holding_registers(address, count=count, slave=unit)
                else:
                   return self._client.read_holding_registers(address, count=count, device_id=unit)

            except ConnectionException:
                 _LOGGER.warning("Reading realtime data failed! Unable to decode frame.")
                 return None


    async def _async_update_data(self) -> dict:
        realtime_data = {}
        try:
            """Inverter serial number is only fetched once"""
            if not self.inverter_data:
                self.inverter_data = await self.hass.async_add_executor_job(
                    self.read_modbus_inverter_data
                )
            """Read realtime data"""
            realtime_data = await self.hass.async_add_executor_job(
                self.read_modbus_realtime_data
            )
            if realtime_data is None:
                # Check if we have last known values and they're not too old
                if (self.last_successful_data and self.last_successful_timestamp and
                    (datetime.now() - self.last_successful_timestamp).total_seconds() < self.MAX_DATA_AGE):
                    realtime_data = self.last_successful_data
                    _LOGGER.warning("Using last known values (%.1f seconds old) due to communication error",
                                  (datetime.now() - self.last_successful_timestamp).total_seconds())
                else:
                    _LOGGER.error("No recent valid data available (last successful read: %s)",
                                self.last_successful_timestamp.strftime('%Y-%m-%d %H:%M:%S') if self.last_successful_timestamp else "never")
                    realtime_data = {"faultmsg": "Communication lost with inverter"}

        except ConnectionException:
            _LOGGER.warning("Reading realtime data failed! Inverter is unreachable.")
            # Check if we have last known values and they're not too old
            if (self.last_successful_data and self.last_successful_timestamp and
                (datetime.now() - self.last_successful_timestamp).total_seconds() < self.MAX_DATA_AGE):
                realtime_data = self.last_successful_data
                _LOGGER.info("Using last known values (%.1f seconds old)",
                           (datetime.now() - self.last_successful_timestamp).total_seconds())
            else:
                _LOGGER.error("No recent valid data available (last successful read: %s)",
                            self.last_successful_timestamp.strftime('%Y-%m-%d %H:%M:%S') if self.last_successful_timestamp else "never")
                realtime_data = {"faultmsg": "Communication lost with inverter"}

        return {**self.inverter_data, **realtime_data}

    def read_modbus_inverter_data(self) -> dict:

        inverter_data = self._read_holding_registers(unit=self.slaveno, address=3, count=5)

        if inverter_data is None or inverter_data.isError():
            return {}

        data = {}
        decoder = BinaryPayloadDecoder.fromRegisters(
            inverter_data.registers, byteorder='>'
        )

        data["sn"] = decoder.decode_string(10).decode("ascii")

        return data

    def read_modbus_realtime_data(self) -> dict:

        data={}
        updated=False

        realtime_data = self._read_holding_registers(unit=self.slaveno, address=60, count=21)
        if realtime_data is not None and not realtime_data.isError():

            decoder = BinaryPayloadDecoder.fromRegisters(
                realtime_data.registers, byteorder='>', wordorder='<'
            )

            data["dailyinv_e"] = decoder.decode_16bit_int()/10.0 
            decoder.skip_bytes(4)
            data["totalgrid_e"] = decoder.decode_32bit_int()/10.0
            decoder.skip_bytes(10)
            data["daybattc_e"] = decoder.decode_16bit_uint()/10.0
            data["daybattd_e"] = decoder.decode_16bit_uint()/10.0
            decoder.skip_bytes(8)
            data["dailygridbuy_e"] = decoder.decode_16bit_uint()/10.0
            data["dailygridsell_e"] = decoder.decode_16bit_uint()/10.0
            decoder.skip_bytes(2)
            data["gridfreq"] = decoder.decode_16bit_uint()/100.0
            updated=True

        realtime_data = self._read_holding_registers(unit=self.slaveno, address=84, count=8)
        if realtime_data is not None and not realtime_data.isError():

            decoder = BinaryPayloadDecoder.fromRegisters(
                realtime_data.registers, byteorder='>', wordorder='<'
            )

            data["dailyload_e"] = decoder.decode_16bit_uint()/10.0    #R84 power through the breaker labeled "Load" on the inverter
            data["totalload_e"] = decoder.decode_32bit_uint()/10.0    #R85 power through the breaker labeled "Load" on the inverter
            decoder.skip_bytes(6)
            data["dchstempc"] = ((decoder.decode_16bit_uint()-1000)/10.0)
            data["achstempc"] = ((decoder.decode_16bit_uint()-1000)/10.0)
            updated=True


        realtime_data = self._read_holding_registers(unit=self.slaveno, address=96, count=21)
        if realtime_data is not None and not realtime_data.isError():

            decoder = BinaryPayloadDecoder.fromRegisters(
                realtime_data.registers, byteorder='>', wordorder='<'
            )

            data["totalinv_e"] = decoder.decode_32bit_int()/10.0   #R98
            decoder.skip_bytes(10)

            flt = decoder.decode_32bit_uint()                      #R103
            flt = flt + decoder.decode_32bit_uint()*2**32

            data["faultmsg"] = self.translate_fault_code_to_messages(flt, FAULT_MESSAGES) 
            decoder.skip_bytes(2)
            
            data["dailypv_e"] = decoder.decode_16bit_uint()/10.0 
            data["pv1_v"] = decoder.decode_16bit_uint()/10.0 
            data["pv1_c"] = decoder.decode_16bit_uint()/10.0 
            data["pv2_v"] = decoder.decode_16bit_uint()/10.0 
            data["pv2_c"] = decoder.decode_16bit_uint()/10.0 
            data["pv3_v"] = decoder.decode_16bit_uint()/10.0
            data["pv3_c"] = decoder.decode_16bit_uint()/10.0
            updated=True


        realtime_data = self._read_holding_registers(unit=self.slaveno, address=150, count=21)
        if realtime_data is not None and not realtime_data.isError():

            decoder = BinaryPayloadDecoder.fromRegisters(
                realtime_data.registers, byteorder='>'
            )

            data["gridl1n_v"] = decoder.decode_16bit_uint()/10.0    #R150
            data["gridl2n_v"] = decoder.decode_16bit_uint()/10.0    
            data["gridl1l2_v"] = decoder.decode_16bit_uint()/10.0
            data["gridrelay_v"] = decoder.decode_16bit_uint()/10.0
            data["invl1n_v"] = decoder.decode_16bit_uint()/10.0
            data["invl2n_v"] = decoder.decode_16bit_uint()/10.0
            data["invl1l2_v"] = decoder.decode_16bit_uint()/10.0
            data["loadl1n_v"] = decoder.decode_16bit_uint()/10.0
            data["loadl2n_v"] = decoder.decode_16bit_uint()/10.0
            decoder.skip_bytes(2)
            data["gridl1_c"] = decoder.decode_16bit_int()/100.0     #R160
            data["gridl2_c"] = decoder.decode_16bit_int()/100.0
            data["extlmtl1_c"] = decoder.decode_16bit_int()/100.0
            data["extlmtl2_c"] = decoder.decode_16bit_int()/100.0
            data["invl1_c"] = decoder.decode_16bit_int()/100.0
            data["invl2_c"] = decoder.decode_16bit_int()/100.0
            data["gen_p"] = decoder.decode_16bit_int()
            data["gridl1_p"] = decoder.decode_16bit_int()
            data["gridl2_p"] = decoder.decode_16bit_int()
            data["grid_p"] = decoder.decode_16bit_int()
            data["gridlmtl1_p"] = decoder.decode_16bit_int()        #R170
            updated=True

        realtime_data = self._read_holding_registers(unit=self.slaveno, address=171, count=18)
        if realtime_data is not None and not realtime_data.isError():

            decoder = BinaryPayloadDecoder.fromRegisters(
                realtime_data.registers, byteorder='>'
            )

            data["gridlmtl2_p"] = decoder.decode_16bit_int()        #R171
            data["gridext_p"] = decoder.decode_16bit_int()        
            data["invl1_p"] = decoder.decode_16bit_int()        
            data["invl2_p"] = decoder.decode_16bit_int()        
            data["inv_p"] = decoder.decode_16bit_int()        
            data["loadl1_p"] = decoder.decode_16bit_int()        
            data["loadl2_p"] = decoder.decode_16bit_int()        
            data["load_p"] = decoder.decode_16bit_int()        
            data["loadl1_c"] = decoder.decode_16bit_int()/100.0        
            data["loadl2_c"] = decoder.decode_16bit_int()/100.0        
            data["genl1l2_v"] = decoder.decode_16bit_uint()/10.0     #R181     
            data["batttempc"] = (decoder.decode_16bit_uint()-1000)/10.0
            data["batt_v"] = decoder.decode_16bit_uint()/100.0        
            data["batt_soc"] = decoder.decode_16bit_uint()        
            decoder.skip_bytes(2)
            pv1_p = decoder.decode_16bit_uint()        
            pv2_p = decoder.decode_16bit_uint()       
            pv3_p = decoder.decode_16bit_uint()
            data["pv1_p"] = pv1_p        
            data["pv2_p"] = pv2_p
            data["pv3_p"] = pv3_p
            data["pv_p"] = pv1_p+pv2_p+pv3_p;
            updated=True


        realtime_data = self._read_holding_registers(unit=self.slaveno, address=190, count=6)
        if realtime_data is not None and not realtime_data.isError():

            decoder = BinaryPayloadDecoder.fromRegisters(
                realtime_data.registers, byteorder='>'
            )

            data["batt_p"] = decoder.decode_16bit_int()          #R190
            data["batt_c"] = decoder.decode_16bit_int()/100.0    
            decoder.skip_bytes(4)
            data["grid_rly"] = 'Closed' if decoder.decode_16bit_int() == 1 else 'Open'
            updated=True    


        #If there was no response to any read request then return no data.
        if not updated:
           return {}
           
        #Update the counter   
        self.update_cnt = self.update_cnt+1
        if (self.update_cnt >= 65535):
           self.update_cnt=0
           
        data["update_cnt"]=self.update_cnt

        # Store this successful reading
        self.last_successful_data = data.copy()
        self.last_successful_timestamp = datetime.now()
        return data


    def translate_fault_code_to_messages(
        self, fault_code: int, fault_messages: dict
    ) -> dict:
        messages = []
        if not fault_code:
            messages.append("No Faults")
            return messages

        for code in fault_messages:
            if (fault_code & code):
                messages.append(fault_messages[code])

        #In case a bit is set that we do not understand
        if not messages:
            messages = "Fault Code: "+hex(fault_code)

        return messages
