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

class EEPROMError(IOError):
    pass

class EEPROM():

    def __init__(self, addr):
        self.i2cBus = SMBus(1)  # 1 = /dev/i2c-1
        self.i2cAddr = addr     # I2C address of EEPROM
        
        # DAC byte addresses
        self.DACaddr = []
        for i in range(4):
            self.DACaddr.append([0x00, 0x20 * i])

        # ADC byte addresses
        self.ADCaddr = []
        for i in range(8):
            self.DACaddr.append([0x01, 0x20 * i])
        for i in range(4):
            self.DACaddr.append([0x02, 0x20 * i])

        # ADS1015
        self.ADS1015addr = [0x03, 0x00]

        # BME280
        self.BME280addr = [0x03, 0x20]

        # PID Heaters
        self.PIDaddr = []
        for i in range(4):
            self.PIDaddr.append([0x04, 0x20 * i])

        # Bang-Bang Heaters
        self.BBaddr = []
        self.BBaddr.append([0x04, 0x80])
        self.BBaddr.append([0x04, 0xA0])

    def write(self, wordAddr0, wordAddr1, data):
        """ 
        Write data to the eeprom given the 2-byte word address and 1-byte data.
        5ms sleep is necessary after writes.
        
        wordAddr0:  1-byte word address  0 - x -A13-A12-A11-A10-A9 -A8
        wordAddr1:  1-byte word address A7 -A6 -A5 -A4 -A3 -A2 -A1 -A0
        data:       1-byte data         D7 -D6 -D5 -D4 -D3 -D2 -D1 -D0
        """
        if len(data) > 32:
            raise EEPROMError(f"Cannot write {len(data)} bytes. Max write size is 32.")

        writeData = [wordAddr0, wordAddr1] + data
        write = i2c_msg.write(self.i2cAddr, writeData)

        with SMBus(1) as bus:
            bus.i2c_rdwr(write)    

        time.sleep(0.005)  
    
    def read(self, wordAddr0, wordAddr1, readBytes):
        """ 
        Read data from the eeprom given the 2-byte word address and 
        number of bytes to read.
        0.5ms sleep is necessary after reads.
        
        Input:
         - wordAddr0:  1-byte word address  0 - x -A13-A12-A11-A10-A9 -A8
         - wordAddr1:  1-byte word address A7 -A6 -A5 -A4 -A3 -A2 -A1 -A0
         - readBytes:  int

        Output:
         - returnBytes: A bytearray of the read bytes
        """

        readData = [wordAddr0, wordAddr1]
        write = i2c_msg.write(self.i2cAddr, readData)
        read = i2c_msg.read(self.i2cAddr, readBytes)
        
        with SMBus(1) as bus:
            self.i2cBus.i2c_rdwr(write,read)

        time.sleep(0.0005)

        returnBytes = bytearray()
        
        for value in read:
            returnBytes.append(value)

        return returnBytes

    def readout(self):

        # Readout DAC Params
        dacMem = []
        for dac in self.DACaddr:
            dacMem.append(self.read(dac[0], dac[1], 0x0020))

        return dacMem