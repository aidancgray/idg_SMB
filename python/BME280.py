# The BME280 is a combined digital humidity, pressure, and temperature
# sensor based on proven sensing principles. It uses the I2C interface.
# 
# This module allows for reading and writing to an I2C device given its
# address.
# 

from smbus2 import SMBus, i2c_msg
import time
import logging

BUS_ID = 1
DEV_ID = 0x76

class BME280:
    def __init__(self):
        self.i2cBus = SMBus(BUS_ID)
        self.i2cAddr = DEV_ID

    def write(self, regAddr, data):
        """ 
        Input:
         - regAddr: int
         - data:    byte Array 
        """

        if len(data) > 1:
            raise EEPROMError(f"Cannot write {len(data)} bytes. Max write size is 1 byte.")

        writeData = regAddr.to_bytes(1, byteorder = 'big') + data
        write = i2c_msg.write(self.i2cAddr, writeData)

        with SMBus(BUS_ID) as bus:
            bus.i2c_rdwr(write)    

        time.sleep(0.005)  
        
    def read(self, regAddr, numBytes):
        """
        Input:
         - regAddr:     int
         - numBytes:    int

        Output:
         - returnBytes: byte array
        """

        write = i2c_msg.write(self.i2cAddr, regAddr.to_bytes(1, byteorder='big'))
        read = i2c_msg.read(self.i2cAddr, numBytes)
        
        with SMBus(BUS_ID) as bus:
            bus.i2c_rdwr(write,read)

        time.sleep(0.0005)

        returnBytes = bytearray()
        
        for value in read:
            returnBytes.append(value)

        return returnBytes