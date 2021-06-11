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

    bme280 = BME280(eeprom)  # Onboard Temperature, Pressure, and Humidity Sensor
    ads1015 = ADS1015(eeprom)  # ADS1015
    hi_pwr_htrs = [hi_pwr_htr(i, io, eeprom) for i in range(2)]

    dacList = []
    dac0 = DAC(0, io, eeprom, 'PID')  # initialize DAC0
    dacList.append(dac0)
    dac1 = DAC(1, io, eeprom, 'PID')  # initialize DAC1
    dacList.append(dac1)
    dac2 = DAC(2, io, eeprom, 'BB')  # initialize DAC2
    dacList.append(dac2)
    dac3 = DAC(3, io, eeprom, 'BB')  # initialize DAC3
    dacList.append(dac3)

    adcList = [AD7124(i, io, eeprom) for i in range(12)]

    # print(f'STATUS={"{0:08b}".format(adcList[n].get_STATUS())}')
    # print(f'ADC_CONTROL={"{0:016b}".format(adcList[n].get_ADC_CONTROL())}')
    # print(f'DATA={"{0:024b}".format(adcList[n].get_DATA())}')
    # print(f'IO_CONTROL_1={"{0:024b}".format(adcList[n].get_IO_CONTROL_1())}')
    # print(f'IO_CONTROL_2={"{0:026b}".format(adcList[n].get_IO_CONTROL_2())}')
    # print(f'ID={"{0:08b}".format(adcList[n].get_ID())}')
    # print(f'ERROR={"{0:024b}".format(adcList[n].get_ERROR())}')
    # print(f'ERROR_EN={"{0:024b}".format(adcList[n].get_ERROR_EN())}')
    # print(f'MCLK_COUNT={"{0:08b}".format(adcList[n].get_MCLK_COUNT())}')
    # print(f'CHANNEL_0={"{0:016b}".format(adcList[n].get_CHANNEL_0())}')
    # print(f'CHANNEL_1={"{0:016b}".format(adcList[n].get_CHANNEL_1())}')
    # print(f'CONFIG_0={"{0:016b}".format(adcList[n].get_CONFIG_0())}')
    # print(f'CONFIG_1={"{0:016b}".format(adcList[n].get_CONFIG_1())}')
    # print(f'FILTER_0={"{0:024b}".format(adcList[n].get_FILTER_0())}')
    # print(f'FILTER_1={"{0:024b}".format(adcList[n].get_FILTER_1())}')
    # print(f'OFFSET_0={"{0:024b}".format(adcList[n].get_OFFSET_0())}')
    # print(f'OFFSET_1={"{0:024b}".format(adcList[n].get_OFFSET_1())}')
    # print(f'GAIN_0={"{0:024b}".format(adcList[n].get_GAIN_0())}')
    # print(f'GAIN_1={"{0:024b}".format(adcList[n].get_GAIN_1())}')
    # print(f'STATUS={"{0:08b}".format(adcList[n].get_STATUS())}')

    while True:
        for n in range(len(adcList)):
            print(f'DATA_{n+1}={adcList[n].get_DATA()}')
        time.sleep(1)
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