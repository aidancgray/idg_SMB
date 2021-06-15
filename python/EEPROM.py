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

from smbus2 import SMBus, i2c_msg
import time
import logging

BUS_ID = 1
DEV_ID = 0x50
EEPROM_LOADED_ADDR = 8191
EEPROM_LOADED_VAL = b'\xAA'

DEFAULT_DAC_DATA = b'\x00\x00' \
                   b'\x00\x00' \
                   b'\x1e\x00' \
                   b'\x00\x07' \
                   b'\x0f\xf6' \
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

DEFAULT_ADC_DATA_1 =    b'\x13\x04' \
                        b'\x04\x12\x00' \
                        b'\x00\x00' \
                        b'\x00\x00\x40' \
                        b'\x80\x23' \
                        b'\x00\x00' \
                        b'\x01\xE0' \
                        b'\x01\xE0' \
                        b'\x06\x01\x80' \
                        b'\x06\x01\x80' \
                        b'\x80\x00\x00' \
                        b'\x80\x00\x00' 

DEFAULT_ADC_DATA_2 =    b'\x00\x00\x00' \
                        b'\x00\x00\x00'


class EEPROMError(IOError):
    pass


class EEPROM():

    def __init__(self):
        self.logger = logging.getLogger('smb')
        self.i2cBus = SMBus(BUS_ID)  # 1 = /dev/i2c-1
        self.i2cAddr = DEV_ID   # I2C address of EEPROM = 0x50

        #EEProm memory map
        # DAC byte addresses
        self.DACmem = []
        self.DACaddr = []
        for i in range(4):
            self.DACaddr.append(0x20 * i)

        # ADC byte addresses
        self.ADCmem = []
        self.ADCaddr = []
        for i in range(8):
            self.ADCaddr.append(0x0100 + 0x24 * i)
        for i in range(4):
            self.ADCaddr.append(0x0220 + 0x24 * i)

        # ADS1015 byte addresses
        self.ADS1015mem = 0
        self.ADS1015addr = 0x0300

        # BME280 byte addresses
        self.BME280mem = 0
        self.BME280addr = 0x0320

        # PID Heaters byte addresses
        self.PIDmem = []
        self.PIDaddr = []
        for i in range(4):
            self.PIDaddr.append(0x0400 + 0x20 * i)

        # Bang-Bang Heaters byte addresses
        self.BBmem = []
        self.BBaddr = []
        for i in range(2):
            self.BBaddr.append(0x0480 + 0x20 * i)

        # Check if eeprom has been initialized already
        if self.read(EEPROM_LOADED_ADDR, 1) != EEPROM_LOADED_VAL:
            self._initialize_eeprom()
            print('eeprom initialized')

            if self.read(EEPROM_LOADED_ADDR, 1) != EEPROM_LOADED_VAL:
                raise EEPROMError("Failed to initialize eeprom to default values")    
        
        self.readout_eeprom()

    def reset_eeprom(self):
        self.write(EEPROM_LOADED_ADDR, b'\x00')

    def _initialize_eeprom(self):
        """
        Set the default values of the eeprom. This is only done when
        the EEPROM_LOADED_VAL is not set.
        """
        # Write default values to DAC0-3
        for DAC in self.DACaddr:
            self.write(DAC, DEFAULT_DAC_DATA)

        # Write default values to ADC0-11
        for ADC in self.ADCaddr:
            self.write(ADC, DEFAULT_ADC_DATA_1)
            self.write(ADC+32, DEFAULT_ADC_DATA_2)

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
        for n in range(len(self.DACaddr)):
            self.DACmem.append(self.read(self.DACaddr[n], 32))

        # AD7124s
        for n in range(len(self.ADCaddr)):
            self.ADCmem.append(self.read(self.ADCaddr[n], 36))
            
        # ADS1015
        self.ADS1015mem = self.read(self.ADS1015addr, 32)
        
        # BME280
        self.BME280mem = self.read(self.BME280addr, 32)
        
        # PID Heaters
        for n in range(len(self.PIDaddr)):
            self.PIDmem.append(self.read(self.PIDaddr[n], 32))

        # Bang-Bang (HI-POWER) Heaters
        for n in range(len(self.BBaddr)):
            self.BBmem.append(self.read(self.BBaddr[n], 32))

    def fill_eeprom(self):
        """
        Fill the EEPROM according to the memory map.
        """

        # DACs
        for n in range(len(self.DACaddr)):
            self.write(self.DACaddr[n], self.DACmem[n])

        # AD7124s
        for n in range(len(self.ADCaddr)):
            # TODO:
            # - Write 32 bytes then the final 4
            self.write(self.ADCaddr[n], self.ADCmem[n][0:32])
            self.write(self.ADCaddr[n]+32, self.ADCmem[n][32:36])

        # ADS1015
        self.write(self.ADS1015addr, self.ADS1015mem)
        
        # BME280
        self.write(self.BME280addr, self.BME280mem)
        
        # PID Heaters
        for n in range(len(self.PIDaddr)):
            self.write(self.PIDaddr[n], self.PIDmem[n])

        # Bang-Bang (HI-POWER) Heaters
        for n in range(len(self.BBaddr)):
            self.write(self.BBaddr[n], self.BBmem[n])
