#!/usr/local/bin/python3.8

from EEPROM import EEPROM

import logging
import sys
import time
import RPi.GPIO as GPIO
import asyncio
import argparse
import shlex
#import spidev

import GPIO_config
import Gbl
from DAC8775 import DAC
from TCPip import TCPServer
from cmdHandler import CMDLoop
from transmitter import Transmitter
from BME280 import BME280
from ADS1015 import ADS1015
from hi_pwr_htr import hi_pwr_htr

async def runSMB(logLevel=logging.INFO):
    logging.basicConfig(datefmt = "%Y-%m-%d %H:%M:%S",
                        format = "%(asctime)s.%(msecs)03dZ %(name)-10s %(levelno)s %(filename)s:%(lineno)d %(message)s")
    
    logger = logging.getLogger('smb')
    logger.setLevel(logLevel)
    logger.info('starting logging')

    eeprom = EEPROM()  # Read in EEPROM data

    tlm = Gbl.telemetry  # Telemetry dictionary
    io = GPIO_config.io()  # GPIO pin configuration

    bme280 = BME280()  # Onboard Temperature, Pressure, and Humidity Sensor
    ads1015 = ADS1015()  # ADS1015
    hi_pwr_htrs = [hi_pwr_htr(i, io) for i in range(2)]

    dacList = []
    dac0 = DAC(0, io, 'PID')  # initialize DAC0
    dacList.append(dac0)

    tcpServer = TCPServer('', 9999)
    cmdHandler = CMDLoop(tcpServer.qCmd, tcpServer.qXmit, eeprom, tlm, io, bme280, ads1015, hi_pwr_htrs, dacList)
    transmitter = Transmitter(tcpServer.qXmit)

    await asyncio.gather(tcpServer.start(), cmdHandler.start(), transmitter.start())

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

    asyncio.run(runSMB(logging.DEBUG))

if __name__ == "__main__":
    main()