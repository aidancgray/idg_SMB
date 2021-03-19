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

BUS_ID = 1
DEV_ID = 0x50

# defaultDACData = b'\x00\x00' \
#                  b'\x00\x00' \
#                  b'\x1e\x00' \
#                  b'\x00\x07' \
#                  b'\x0f\xf6' \
#                  b'\x00\x00' \
#                  b'\x00\x0f' \
#                  b'\x00\x01' \
#                  b'\x00\x00' \
#                  b'\x00\x00' \
#                  b'\x00\x00' \
#                  b'\x00\x00' \
#                  b'\x00\x00' \
#                  b'\x00\x00' \
#                  b'\x00\x00' \
#                  b'\x00\x00'
#
# defaultADCData = b'\x00' \
#                  b'\x00' \
#                  b'\x00\x00' \
#                  b'\x00\x00\x00' \
#                  b'\x00\x00\x00' \
#                  b'\x00\x00' \
#                  b'\x00\x00\x00' \
#                  b'\x00\x00\x00' \
#                  b'\x00' \
#                  b'\x00\x00' \
#                  b'\x00\x00' \
#                  b'\x00\x00\x00' \
#                  b'\x00\x00\x00' \
#                  b'\x00\x00\x00'



class EEPROMError(IOError):
    pass


class EEPROM():


    def __init__(self, addr):
        self.i2cBus = SMBus(BUS_ID)  # 1 = /dev/i2c-1
        self.i2cAddr = addr    # I2C address of EEPROM

        #EEProm memory map

        # DAC byte addresses
        self.DACaddr = []
        for i in range(4):
            self.DACaddr.append(0x20 * i)

        # ADC byte addresses
        self.ADCaddr = []
        for i in range(8):
            self.DACaddr.append(0x0100 + 0x20 * i)
        for i in range(4):
            self.DACaddr.append(0x0200 + 0x20 * i)

        # ADS1015 byte addresses
        self.ADS1015addr = 0x0300

        # BME280 byte addresses
        self.BME280addr = 0x0320

        # PID Heaters byte addresses
        self.PIDaddr = []
        for i in range(4):
            self.PIDaddr.append(0x0400 + 0x20 * i)

        # Bang-Bang Heaters byte addresses
        self.BBaddr = []
        for i in range(4):
            self.BBaddr.append(0x0480 + 0x20 * i)


    def write(self, regAddr, data):
        """ 
        Write byte data (max 32 bytes) to the eeprom given regAddr
        5ms sleep is necessary after writes.

         Input:
         - regAddr:     int
         - data:   byte Array
        
        wordAddr0:  1-byte word address  0 - x -A13-A12-A11-A10-A9 -A8
        wordAddr1:  1-byte word address A7 -A6 -A5 -A4 -A3 -A2 -A1 -A0
        data:       1-byte data         D7 -D6 -D5 -D4 -D3 -D2 -D1 -D0
        """

        if len(data) > 32:
            raise EEPROMError(f"Cannot write {len(data)} bytes. Max write size is 32.")

        writeData = regAddr.to_bytes(2, byteorder = 'big') + data
        write = i2c_msg.write(self.i2cAddr, writeData)

        with SMBus(1) as bus:
            bus.i2c_rdwr(write)    

        time.sleep(0.005)  
    
    def read(self, regAddr, numBytes):
        """ 
        Read numBytes of data from the eeprom given the regAddr.
        0.5ms sleep is necessary after reads.
        
        Input:
         - regAddr:     int
         - numBytes:   int

        Output:
         - returnBytes: A bytearray of the read bytes
        """

        write = i2c_msg.write(self.i2cAddr, regAddr.to_bytes(2, byteorder = 'big'))
        read = i2c_msg.read(self.i2cAddr, numBytes)
        
        with SMBus(1) as bus:
            self.i2cBus.i2c_rdwr(write,read)

        time.sleep(0.0005)

        returnBytes = bytearray()
        
        for value in read:
            returnBytes.append(value)

        return returnBytes

    # def readout(self):
    #
    #     # Readout DAC Params
    #     dacMem = []
    #     for dac in self.DACaddr:
    #         dacMem.append(self.read(dac[0], dac[1], 0x0020))
    #
    #     return dacMem