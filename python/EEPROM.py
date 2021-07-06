# EEPROM.py
# 5/24/2021
# Aidan Gray
# aidan.gray@idg.jhu.edu
#
# The EEPROM is a 24CW64X (64-Kbit) I2C device for storing data off the
# microSD card, which is unreliable for many write-cycles.
# 
# This module allows for reading and writing to an I2C device given its
# address.
# 
# The location of the data to read/write requires a 2x 1-byte words,
# followed by the number of bytes to read or the data to write.

from ADS1015 import ADS1015
from smbus2 import SMBus, i2c_msg
import time
import logging

BUS_ID = 1
DEV_ID = 0x50
EEPROM_LOADED_ADDR = 8191
EEPROM_LOADED_VAL = b'\xAA'

DEFAULT_DAC_DATA_1 = b'\x00\x00' \
                     b'\x00\x00' \
                     b'\x1e\x00' \
                     b'\x00\x07' \
                     b'\x00\x00' \
                     b'\x00\x00' \
                     b'\x00\x0f' \
                     b'\x00\x01' \
                     b'\x00\x00' \
                     b'\x00\x00' \
                     b'\x00\x00' \
                     b'\x00\x00' \
                     b'\x00\x00' \
                     b'\x00\x00' \
                     b'\x00\x00' \
                     b'\x00\x00'

DEFAULT_DAC_DATA_2 = b'\x00\x00' \
                     b'\x00\x00' \
                     b'\x00\x00\x00\x00' \
                     b'\x00\x00\x00\x00' \
                     b'\x00\x00\x00\x00' \
                     b'\x00\x00\x00\x00' \
                     b'\x00\x00\x00\x00' \
                     b'\x00\x00\x00\x00' \
                     b'\x00\x00\x00\x00'

DAC_MEM_LENGTH = len(DEFAULT_DAC_DATA_1) + len(DEFAULT_DAC_DATA_2)

DEFAULT_ADC_DATA_1 =    b'\x13\xC4' \
                        b'\x04\x00\x00' \
                        b'\x00\x00' \
                        b'\x00\x00\x40' \
                        b'\x80\x23' \
                        b'\x00\x00' \
                        b'\x01\xE0' \
                        b'\x01\xE0' \
                        b'\x16\x07\xFF' \
                        b'\x16\x07\xFF' \
                        b'\x80\x00\x00' \
                        b'\x80\x00\x00' \
                        b'\xff\xff'

DEFAULT_ADC_DATA_2 =    b'\x00\x00\x00' \
                        b'\x00\x00\x00' \
                        b'\x00'\
                        b'\x00'

ADC_MEM_LENGTH = len(DEFAULT_ADC_DATA_1) + len(DEFAULT_ADC_DATA_2)

DEFAULT_ADS1015_DATA =  b'\x89\x83' \
                        b'\xB9\x83'

ADS_MEM_LENGTH = len(DEFAULT_ADS1015_DATA)

DEFAULT_BME280_DATA =   b'\x01' \
                        b'\x27' \
                        b'\x00'

BME_MEM_LENGTH = len(DEFAULT_BME280_DATA)

DEFAULT_HIPWR_DATA =    b'\x00' \
                        b'\x00' \
                        b'\x00\x00\x00\x00'

HIPWR_MEM_LENGTH = len(DEFAULT_HIPWR_DATA)

class EEPROMError(IOError):
    pass


class EEPROM():

    def __init__(self, reset=False):
        self.logger = logging.getLogger('smb')
        self.i2cBus = SMBus(BUS_ID)  # 1 = /dev/i2c-1
        self.i2cAddr = DEV_ID   # I2C address of EEPROM = 0x50
        self.reset = reset

        #EEProm memory map
        # DAC byte addresses
        self.DACmem = []
        self.DACaddr = []
        for i in range(4):
            self.DACaddr.append(0x40 * i)

        # ADC byte addresses
        self.ADCmem = []
        self.ADCaddr = []
        for i in range(8):
            self.ADCaddr.append(0x0100 + 0x40 * i)
        for i in range(4):
            self.ADCaddr.append(0x0300 + 0x40 * i)

        # ADS1015 byte addresses
        self.ADS1015mem = 0
        self.ADS1015addr = 0x0400

        # BME280 byte addresses
        self.BME280mem = 0
        self.BME280addr = 0x0420

        # PID Heaters byte addresses
        self.PIDmem = []
        self.PIDaddr = []
        for i in range(4):
            self.PIDaddr.append(0x0440 + 0x20 * i)

        # HI-PWR (Bang-Bang) Heaters byte addresses
        self.HIPWRmem = []
        self.HIPWRaddr = []
        for i in range(2):
            self.HIPWRaddr.append(0x04C0 + 0x20 * i)

        # Reset the EEPROM if initialized with 'reset=True'
        if self.reset:
            self.reset_eeprom()

        # Check if eeprom has been initialized already
        if self.read(EEPROM_LOADED_ADDR, 1) != EEPROM_LOADED_VAL:
            self._initialize_eeprom()
            print('eeprom initialized')

            if self.read(EEPROM_LOADED_ADDR, 1) != EEPROM_LOADED_VAL:
                raise EEPROMError("Failed to initialize eeprom to default values")    
        
        self.readout_eeprom()

    def reset_eeprom(self):
        '''
        Clear out all of the memory in the EEPROM and clear the 
        EEPROM_LOADED bit.
        '''
        for addr in range(1248):
            self.write(addr, b'\xff')
        self.write(EEPROM_LOADED_ADDR, b'\xff')

    def _initialize_eeprom(self):
        """
        Set the default values of the eeprom. This is only done when
        the EEPROM_LOADED_VAL is not set.
        """
        # Write default values to DAC0-3
        for DAC in self.DACaddr:
            self.write(DAC, DEFAULT_DAC_DATA_1)
            self.write(DAC+len(DEFAULT_DAC_DATA_1), DEFAULT_DAC_DATA_2)

        # Write default values to ADC0-11
        for ADC in self.ADCaddr:
            self.write(ADC, DEFAULT_ADC_DATA_1)
            self.write(ADC+len(DEFAULT_ADC_DATA_1), DEFAULT_ADC_DATA_2)

        # Write default values to ADS1015
        self.write(self.ADS1015addr, DEFAULT_ADS1015_DATA)

        # Write default values to BME280
        self.write(self.BME280addr, DEFAULT_BME280_DATA)

        # Write default values to HIPWR0-1
        for hipwr in self.HIPWRaddr:
            self.write(hipwr, DEFAULT_HIPWR_DATA)

        # Set the check byte
        self.write(EEPROM_LOADED_ADDR, EEPROM_LOADED_VAL)

    def write(self, regAddr, data):
        """ 
        Write byte data (max 32 bytes) to the eeprom given regAddr.
        5ms sleep is necessary after writes.

        Input:
         - regAddr: int
         - data:    byte Array 
        """

        if len(data) > 32:
            raise EEPROMError(f"Cannot write {len(data)} bytes. Max write size is 32.")

        writeData = regAddr.to_bytes(2, byteorder = 'big') + data
        write = i2c_msg.write(self.i2cAddr, writeData)

        with SMBus(BUS_ID) as bus:
            bus.i2c_rdwr(write)    

        time.sleep(0.005)  
    
    def read(self, regAddr, numBytes):
        """ 
        Read numBytes of data from the eeprom given the regAddr.
        0.5ms sleep is necessary after reads.
        
        Input:
         - regAddr:     int
         - numBytes:    int

        Output:
         - returnBytes: byte array
        """

        write = i2c_msg.write(self.i2cAddr, regAddr.to_bytes(2, byteorder = 'big'))
        read = i2c_msg.read(self.i2cAddr, numBytes)
        
        with SMBus(BUS_ID) as bus:
            bus.i2c_rdwr(write,read)

        time.sleep(0.0005)

        returnBytes = bytearray()
        
        for value in read:
            returnBytes.append(value)

        return returnBytes

    def readout_eeprom(self):
        """
        Read out all contents of the EEPROM according to the memory map
        and stuff the data into the appropriate memory lists.
        """

        # DACs
        self.DACmem = []
        for n in range(len(self.DACaddr)):
            self.DACmem.append(self.read(self.DACaddr[n], DAC_MEM_LENGTH))

        # AD7124s
        self.ADCmem = []
        for n in range(len(self.ADCaddr)):
            self.ADCmem.append(self.read(self.ADCaddr[n], ADC_MEM_LENGTH))

        # ADS1015
        self.ADS1015mem = []
        self.ADS1015mem = self.read(self.ADS1015addr, ADS_MEM_LENGTH)

        # BME280
        self.BME280mem = []
        self.BME280mem = self.read(self.BME280addr, BME_MEM_LENGTH)
        
        # PID Heaters
        self.PIDmem = []
        for n in range(len(self.PIDaddr)):
            self.PIDmem.append(self.read(self.PIDaddr[n], 32))

        # HI-PWR (Bang-Bang) Heaters
        self.HIPWRmem = []
        for n in range(len(self.HIPWRaddr)):
            self.HIPWRmem.append(self.read(self.HIPWRaddr[n], HIPWR_MEM_LENGTH))

    def printout_eeprom(self):
        for n in range(len(self.DACmem)):
            self.logger.info(f'DACmem_{n}={self.DACmem[n]}')

        for n in range(len(self.ADCmem)):
            self.logger.info(f'ADCmem_{n}={self.ADCmem[n]}')

        self.logger.info(f'ADS1015mem={self.ADS1015mem}')

        self.logger.info(f'BME280mem={self.BME280mem}')

        for n in range(len(self.PIDmem)):
            self.logger.info(f'PIDmem_{n}={self.PIDmem[n]}')

        for n in range(len(self.HIPWRmem)):
            self.logger.info(f'HIPWRmem_{n}={self.HIPWRmem[n]}')

    def fill_eeprom(self):
        """
        Fill the EEPROM according to the memory map.
        """

        # DACs
        for n in range(len(self.DACaddr)):
            self.write(self.DACaddr[n], self.DACmem[n][0:len(DEFAULT_DAC_DATA_1)])
            self.write(self.DACaddr[n]+len(DEFAULT_DAC_DATA_1), self.DACmem[n][len(DEFAULT_DAC_DATA_1):DAC_MEM_LENGTH])

        # AD7124s
        for n in range(len(self.ADCaddr)):
            self.write(self.ADCaddr[n], self.ADCmem[n][0:len(DEFAULT_ADC_DATA_1)])
            self.write(self.ADCaddr[n]+len(DEFAULT_ADC_DATA_1), self.ADCmem[n][len(DEFAULT_ADC_DATA_1):ADC_MEM_LENGTH])

        # ADS1015
        self.write(self.ADS1015addr, self.ADS1015mem)
        
        # BME280
        self.write(self.BME280addr, self.BME280mem)
        
        # PID Heaters
        for n in range(len(self.PIDaddr)):
            self.write(self.PIDaddr[n], self.PIDmem[n])

        # HI-PWR (Bang-Bang) Heaters
        for n in range(len(self.HIPWRaddr)):
            self.write(self.HIPWRaddr[n], self.HIPWRmem[n][0:len(DEFAULT_HIPWR_DATA)])

        self.readout_eeprom()