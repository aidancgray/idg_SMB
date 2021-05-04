#!/usr/local/bin/python3.8

from EEPROM import EEPROM

import logging
import sys
import time
import RPi.GPIO as GPIO
import asyncio
#import spidev

import EEPROM
import GPIO_config
import Gbl
from DAC8775 import DAC
from TCPip import TCPServer
from cmdHandler import CMDLoop

async def runSMB(logLevel=logging.INFO):
    logging.basicConfig(datefmt = "%Y-%m-%d %H:%M:%S",
                        format = "%(asctime)s.%(msecs)03dZ %(name)-10s %(levelno)s %(filename)s:%(lineno)d %(message)s")
    
    logger = logging.getLogger('smb')
    logger.setLevel(logLevel)
    logger.info('starting logging')

    # Read in EEPROM data
    #eeprom = EEPROM()

    #tlm = Gbl.telemetry     # Telemetry dictionary
    #io = GPIO_config.io()   # GPIO pin configuration
    
    #dac0 = DAC(0, io, 'PID')    # initialize DAC0

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
    # uI = input("press any key to finish")

    tcpServer = TCPServer('', 9999)
    cmdHandler = CMDLoop(tcpServer.qCmd, tcpServer.qXmit)

    await asyncio.gather(tcpServer.start(), cmdHandler.start())

def main():
    asyncio.run(runSMB(logging.INFO))

if __name__ == "__main__":
    main()