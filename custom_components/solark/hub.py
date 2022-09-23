"""SolArk Modbus Hub"""
from datetime import timedelta
import logging
import threading
from urllib.parse import urlparse

from homeassistant.core import CALLBACK_TYPE, callback
from homeassistant.helpers.typing import HomeAssistantType
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from pymodbus.client.sync import ModbusSerialClient, ModbusTcpClient
from pymodbus.constants import Endian
from pymodbus.exceptions import ConnectionException
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.register_read_message import ReadHoldingRegistersResponse
from voluptuous.validators import Number

from .const import FAULT_MESSAGES

_LOGGER = logging.getLogger(__name__)

update_cnt=0

class SolArkModbusHub(DataUpdateCoordinator[dict]):
    """Thread safe wrapper class for pymodbus."""

    def __init__(
        self,
        hass: HomeAssistantType,
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

        #Break the entered hostnames into its component parts.
        parsed=urlparse(f'//{hostname}')

        #If it not a URL it might be a serial port.
        #This logic is tested to work with linux and windows serial port names.
        if (parsed.port is None) and ((parsed.hostname is None) or (parsed.hostname[0:3] == "com" )):
            self._client = ModbusSerialClient(method='rtu',port=parsed.path+parsed.netloc,baudrate=9600,
                                              stopbits=1,bytesize=8,timeout=5)
        else:

            if (parsed.port is None):
                localport=502
            else:
                localport=parsed.port

            self._client = ModbusTcpClient(host=parsed.hostname, port=localport, timeout=5)

        
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
            kwargs = {"unit": unit} if unit else {}
            return self._client.read_holding_registers(address, count, **kwargs)

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
        except ConnectionException:
            _LOGGER.error("Reading realtime data failed! Inverter is unreachable.")
            realtime_data["faultmsg"] = "Inverter is unreachable."

        return {**self.inverter_data, **realtime_data}

    def read_modbus_inverter_data(self) -> dict:

        inverter_data = self._read_holding_registers(unit=1, address=3, count=5)

        if inverter_data.isError():
            return {}

        data = {}
        decoder = BinaryPayloadDecoder.fromRegisters(
            inverter_data.registers, byteorder=Endian.Big
        )

        data["sn"] = decoder.decode_string(10).decode("ascii")

        return data

    def read_modbus_realtime_data(self) -> dict:

        data={}
        updated=False

        realtime_data = self._read_holding_registers(unit=1, address=60, count=21)
        if not realtime_data.isError():

            decoder = BinaryPayloadDecoder.fromRegisters(
                realtime_data.registers, byteorder=Endian.Big, wordorder=Endian.Little
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

        realtime_data = self._read_holding_registers(unit=1, address=84, count=3)
        if not realtime_data.isError():

            decoder = BinaryPayloadDecoder.fromRegisters(
                realtime_data.registers, byteorder=Endian.Big, wordorder=Endian.Little
            )

            data["dailyload_e"] = decoder.decode_16bit_uint()/10.0    #R84 power through the breaker labeled "Load" on the inverter
            data["totalload_e"] = decoder.decode_32bit_uint()/10.0     #R85 power through the breaker labeled "Load" on the inverter
            updated=True


        realtime_data = self._read_holding_registers(unit=1, address=96, count=21)
        if not realtime_data.isError():

            decoder = BinaryPayloadDecoder.fromRegisters(
                realtime_data.registers, byteorder=Endian.Big, wordorder=Endian.Little
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


        realtime_data = self._read_holding_registers(unit=1, address=150, count=21)
        if not realtime_data.isError():

            decoder = BinaryPayloadDecoder.fromRegisters(
                realtime_data.registers, byteorder=Endian.Big
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

        realtime_data = self._read_holding_registers(unit=1, address=171, count=18)
        if not realtime_data.isError():

            decoder = BinaryPayloadDecoder.fromRegisters(
                realtime_data.registers, byteorder=Endian.Big
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


        realtime_data = self._read_holding_registers(unit=1, address=190, count=6)
        if not realtime_data.isError():

            decoder = BinaryPayloadDecoder.fromRegisters(
                realtime_data.registers, byteorder=Endian.Big
            )

            data["batt_p"] = decoder.decode_16bit_int()          #R190
            data["batt_c"] = decoder.decode_16bit_int()/100.0    
            updated=True    


        #If there was no response to any read request then return no data.
        if not updated:
           return {}
           
        #Update the global counter   
        global update_cnt
        update_cnt = update_cnt+1
        if (update_cnt >= 65535):
           update_cnt=0
           
        data["update_cnt"]=update_cnt
        

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
