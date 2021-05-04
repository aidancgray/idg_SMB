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
from BME280 import BME280

async def runSMB(logLevel=logging.INFO):
    logging.basicConfig(datefmt = "%Y-%m-%d %H:%M:%S",
                        format = "%(asctime)s.%(msecs)03dZ %(name)-10s %(levelno)s %(filename)s:%(lineno)d %(message)s")
    
    logger = logging.getLogger('smb')
    logger.setLevel(logLevel)
    logger.info('starting logging')

    #eeprom = EEPROM()  # Read in EEPROM data

    #tlm = Gbl.telemetry  # Telemetry dictionary
    #io = GPIO_config.io()  # GPIO pin configuration

    bme280 = BME280()

    mode = bme280.read(0xF4, 1)    
    print(f'mode: {mode!r}')
    
    ctrl_hum = b'\x01' # oversampling x1 for H
    bme280.write(0xF2, ctrl_hum)

    ctrl_meas = b'\x25' # forcedMode on (1 reading, then back to sleep mode) & oversampling x1 for P & T
    bme280.write(0xF4, ctrl_meas)

    uP = bme280.read(0xF7, 3)
    uT = bme280.read(0xFA, 3)
    uH = bme280.read(0xFD, 2)
    print(f'uP: {uP!r}')
    print(f'uT: {uT!r}')
    print(f'uH: {uH!r}')

    #dacList = []
    #dac0 = DAC(0, io, 'PID')  # initialize DAC0
    #dacList.append(dac0)

    ### DAC READ/WRITE STRUCTURE ######
    # dac0.dac_write_data(0x06, 0x000F) 
    # dac0.dac_write_data(0x07, 0x03C1)
    # dac0.dac_write_data(0x03, 0x01F0)
    # dac0.dac_write_data(0x04, 0x1005)
    # dac0.dac_write_data(0x05, 0x0000)
    # io.dac_ldac(1)
    # io.dac_ldac(0)
    # io.dac_ldac(1)
    # dac0.dac_write_data(0x03, 0x0020)
    # dac0.dac_write_data(0x05, 0xFFFF)
    # io.dac_ldac(1)
    # io.dac_ldac(0)
    # io.dac_ldac(1)

    # readBack = dac0.dac_read_data(11)
    
    # readBytes = readBack.to_bytes(3, byteorder='big')
    # for byte in readBytes:
    #     print(format(byte,"08b"))
    ###################################

    #tcpServer = TCPServer('', 9999)
    #cmdHandler = CMDLoop(tcpServer.qCmd, tcpServer.qXmit, eeprom, tlm, io, dacList)

    #await asyncio.gather(tcpServer.start(), cmdHandler.start())

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