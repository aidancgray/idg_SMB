#!/usr/local/bin/python3.8
# main.py
# 5/24/2021
# Aidan Gray
# aidan.gray@idg.jhu.edu
#
# The main script for the Sensor Monitor / Temperature Control Board

from EEPROM import EEPROM

import logging
import sys
import asyncio
import argparse
import shlex
import time

import GPIO_config
import Gbl
from DAC8775 import DAC
from TCPip import TCPServer
from cmdHandler import CMDLoop
from transmitter import Transmitter
from BME280 import BME280
from ADS1015 import ADS1015
from hi_pwr_htr import hi_pwr_htr
from AD7124 import AD7124

def custom_except_hook(loop, context):
    if repr(context['exception']) == 'SystemExit()':
        print('Exiting Program...')

async def runSMB(logLevel=logging.INFO):
    logging.basicConfig(datefmt = "%Y-%m-%d %H:%M:%S",
                        format = "%(asctime)s.%(msecs)03dZ %(name)-10s %(levelno)s %(filename)s:%(lineno)d %(message)s")
    
    logger = logging.getLogger('smb')
    logger.setLevel(logLevel)
    logger.info('starting logging')

    eeprom = EEPROM()  # Read in EEPROM data

    tlm = Gbl.telemetry  # Telemetry dictionary
    cal = Gbl.sensor_cal # Sensor Calibration dictionary
    io = GPIO_config.io()  # GPIO pin configuration

    bme280 = BME280()  # Onboard Temperature, Pressure, and Humidity Sensor
    ads1015 = ADS1015()  # ADS1015
    hi_pwr_htrs = [hi_pwr_htr(i, io) for i in range(2)]

    dacList = []
    dac0 = DAC(0, io, 'PID')  # initialize DAC0
    dacList.append(dac0)
    dac1 = DAC(1, io, 'PID')  # initialize DAC1
    dacList.append(dac1)
    dac2 = DAC(2, io, 'BB')  # initialize DAC2
    dacList.append(dac2)
    dac3 = DAC(3, io, 'BB')  # initialize DAC3
    dacList.append(dac3)

    adcList = [AD7124(i, io) for i in range(12)]
    
    # readData = adcList[0].adc_read_data(5, 1)
    # print(f'ID={readData}')
    
    # readData = adcList[0].adc_read_data(0, 1)
    # print(f'STATUS={readData}')
    
    # readData = adcList[0].adc_read_data(1, 2)
    # print(f'ADC_CONTROL={readData}')
    
    # readData = adcList[0].adc_read_data(2, 3)
    # print(f'DATA={readData}')

    # readData = adcList[0].adc_read_data(3, 3)
    # print(f'IO_CONTROL_1={readData}')

    # readData = adcList[0].adc_read_data(4, 2)
    # print(f'IO_CONTROL_2={readData}')
    
    # readData = adcList[0].adc_read_data(6, 3)
    # print(f'ERROR={readData}')
    
    # readData = adcList[0].adc_read_data(7, 3)
    # print(f'ERROR_EN={readData}')
    
    # readData = adcList[0].adc_read_data(8, 1)
    # print(f'MCLK_COUNT={readData}')

    ### CHANNEL Registers ###
    # for i in range(16):
    #     readData = adcList[0].adc_read_data(9+i, 2)
    #     print(f'CHANNEL_{i}={readData}')

    ### CONFIGURATION Registers ###
    # for i in range(8):
    #     readData = adcList[0].adc_read_data(25+i, 2)
    #     print(f'CONFIG_{i}={readData}')

    ### FILTER Registers ###
    # for i in range(8):
    #     readData = adcList[0].adc_read_data(33+i, 3)
    #     print(f'FILTER_{i}={readData}')

    ### OFFSET Registers ###
    # for i in range(8):
    #     readData = adcList[0].adc_read_data(41+i, 3)
    #     print(f'OFFSET_{i}={readData}')

    ### GAIN Registers ###
    # for i in range(8):
    #     readData = adcList[0].adc_read_data(49+i, 3)
    #     print(f'GAIN_{i}={readData}')

    tcpServer = TCPServer('', 9999)
    cmdHandler = CMDLoop(tcpServer.qCmd, tcpServer.qXmit, eeprom, tlm, cal, io, bme280, ads1015, hi_pwr_htrs, dacList, adcList)
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
    loop = asyncio.get_event_loop()
    loop.set_exception_handler(custom_except_hook)
    try:
        loop.run_until_complete(runSMB(logging.INFO))
    except KeyboardInterrupt:
        print('Exiting Program...')

if __name__ == "__main__":
    main()