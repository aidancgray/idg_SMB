#!/usr/local/bin/python3.8

from EEPROM import EEPROM

import logging
import sys
import time
import RPi.GPIO as GPIO
import spidev

import EEPROM
import GPIO_config
import Gbl


def runSMB(logLevel=logging.INFO):
    logging.basicConfig(datefmt = "%Y-%m-%d %H:%M:%S",
                        format = "%(asctime)s.%(msecs)03dZ %(name)-10s %(levelno)s %(filename)s:%(lineno)d %(message)s")
    
    logger = logging.getLogger('smb')
    logger.setLevel(logLevel)
    logger.info('starting logging')

    # Read in EEPROM data
    eeprom = EEPROM()

    tlm = Gbl.telemetry

    io = GPIO_config.io()
    # reset both DACs
    io.dac_reset(0)
    time.sleep(0.001)
    io.dac_reset(1)
    time.sleep(0.001)

    #io.dac_bank_sel(1)


def main():
    # runSMB(logging.INFO)

if __name__ == "__main__":
    main()