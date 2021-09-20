[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs) ![GitHub all releases](https://img.shields.io/github/downloads/pbix/HA-solark-PV/total.svg) ![License](https://img.shields.io/github/license/pbix/HA-solark-PV)]
# HA-solar-PV
This integration utilizes the MODBUS interface of the Solark 12k inverter to allow local read-only
access to inverter variables.  The integration does a direct MODBUS interface with your inverter.

## Installation
Using the HACS page add this repository to your installation.  Then under the configuration tab search for "SolArk Inverter Modbus" and install it.
One device will be installed with many entities attached.  The entities map directly to registers in the inverter.  Not all registers are there and many are not enabled by default.
Instead I have made the ones I feel are the most useful to be enabled by default.

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

In the future I hope others will help me to enhance this page to provide more details on the wiring and alternate methods to get your modbus traffic into your Home Assistant.



