#!/usr/local/bin/python3.8
# main.py
# 5/24/2021
# Aidan Gray
# aidan.gray@idg.jhu.edu
#
# The main script for the Sensor Monitor / Temperature Control Board

import logging
import sys
import asyncio
import argparse
import shlex
import netifaces

import GPIO_config
import Gbl
from EEPROM import EEPROM
from DAC8775 import DAC
from TCPip import TCPServer
from cmdHandler import CMDLoop
from transmitter import Transmitter
from BME280 import BME280
from ADS1015 import ADS1015
from pid_htr import pid_htr
from hi_pwr_htr import hi_pwr_htr
from AD7124 import AD7124
from UDPcast import UDPcast

def custom_except_hook(loop, context):
    if repr(context['exception']) == 'SystemExit()':
        print('Exiting Program...')

async def runSMB(opts):
    logging.basicConfig(datefmt = "%Y-%m-%d %H:%M:%S",
                        format = "%(asctime)s.%(msecs)03dZ %(name)-10s %(levelno)s %(filename)s:%(lineno)d %(message)s")
    
    logger = logging.getLogger('smb')
    logger.setLevel(opts.logLevel)
    logger.info('starting logging')

    eeprom = EEPROM(reset=False)  # Read in EEPROM data

    tlm = Gbl.telemetry  # Telemetry dictionary
    cal = Gbl.sensor_cal # Sensor Calibration dictionary
    io = GPIO_config.io()  # GPIO pin configuration

    bme280 = BME280(eeprom)  # Onboard Temperature, Pressure, and Humidity Sensor
    ads1015 = ADS1015(eeprom)  # ADS1015

    hi_pwr_htrs = []
    for i in range (2):
        hi_pwr_htrs.append(hi_pwr_htr(i, io, eeprom, tlm))

    dacList = []
    for i in range(2):
        dacList.append(DAC(i, io, eeprom, tlm))

    adcList = []
    for i in range(12):
        adcList.append(AD7124(i, io, eeprom, tlm, cal))
    
    ip_address = netifaces.ifaddresses('eth0')[netifaces.AF_INET][0]['addr']
    udp_address = netifaces.ifaddresses('eth0')[netifaces.AF_INET][0]['broadcast']
    logger.info(f'IP:  {ip_address}')
    logger.info(f'UDP: {udp_address}')

    tcpServer = TCPServer(ip_address, 1024)
    cmdHandler = CMDLoop(tcpServer.qCmd, tcpServer.qXmit, eeprom, tlm, cal, io, bme280, ads1015, hi_pwr_htrs, dacList, adcList)
    transmitter = Transmitter(tcpServer.qXmit)
    udpServer = UDPcast(udp_address, 8888, cmdHandler.qUDP)

    await asyncio.gather(tcpServer.start(), cmdHandler.start(), transmitter.start(), udpServer.start())

def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    if isinstance(argv, str):
        argv = shlex.split(argv)

    parser = argparse.ArgumentParser(sys.argv[0])
    parser.add_argument('--logLevel', type=int, default=logging.INFO,
                        help='logging threshold. 10=debug, 20=info, 30=warn')
    parser.add_argument('--sensorPeriod', type=float, default=1.0,
                        help='how often to sample the sensors')

    opts = parser.parse_args(argv)
    loop = asyncio.get_event_loop()
    loop.set_exception_handler(custom_except_hook)
    try:
        loop.run_until_complete(runSMB(opts))
    except KeyboardInterrupt:
        print('Exiting Program...')

if __name__ == "__main__":
    main()