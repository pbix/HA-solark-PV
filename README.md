[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs) 
![GitHub all releases](https://img.shields.io/github/downloads/pbix/HA-solark-PV/total.svg) 
![License](https://img.shields.io/github/license/pbix/HA-solark-PV)
# HA-solark-PV
This integration utilizes the MODBUS interface of the Solark 12k inverter to allow local read-only
access to inverter variables.  The integration does a direct MODBUS interface with your inverter.

## Installation
This is a HACS integration.  First get HACS up and running on your system https://hacs.xyz/docs/configuration/basic.  Then go to the HACS page and select the three dots in the upper right and then "custom repositories".  Enter https://github.com/pbix/HA-solark-PV and select "Integration".  The new repository will appear on the HACS page, select install on the card and restart.

Finally head over to Configurations->Integrations->Add Integration and search for SolArk and setup.  If you have your system setup for Modbus/TCP just enter the IP address of your gateway and proceed.  One device will be installed with many entities attached.  The entities map directly to registers in the inverter.  Not all registers are there and many are not enabled by default.  Instead I have made the ones I feel are the most useful to be enabled by default.

You can peruse and enable entities as you like but don't bother asking me what all these registers mean. 

## Connection via Modbus TCP to the SolArk inverter
Your SolArk inverter has a connector which will allow you to talk RS-485.  The exact details of the wiring here depends on your 
model.  

In my system I am using the DSD TECH SH-U11F USB-RS485 converter. This is available from multiple sources for about $30. The reasons I recommend this one:
1) SH-U11F provides isolation which will lower your risk of damaging any circuits.
2) SH-U11F includes termination resistors which are recommended for reliable communications.
3) SH-U11F includes a ground connection terminal recommended by Sol-Ark in the document.

If you have another coverter model that can provide the same features it may work as well.  But I do not recommend that you skimp on a converter.  Once you have a converter working you needed
to provide a TCP/IP gateway to convert your RTU signal to Modbus TCP/IP.  In my case I used an old OpenWRT capabile router with a USB connector on the back and installed the 
excellect mbusd package which you can read about here: https://github.com/3cky/mbusd

If you want to use Modbus/RTU here is a simple hack until I get the UI worked out (or someone helps me with it).  In the hub.py file, around line 39, comment the "ModbusTcpClient" open and uncomment the following line for "ModbusSerialClient" entering the name of your serial port (ie port="/dev/ttyUSB0").  Then save the file, delete the component, restart home assistant and re-install the component.

In the future I hope others will help me to enhance this page to provide more details on the wiring and alternate methods to get your modbus traffic into your Home Assistant.



