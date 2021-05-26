# AD7124.py
# 5/24/2021
# Aidan Gray
# aidan.gray@idg.jhu.edu
#
# 

import RPi.GPIO as GPIO
import logging

class AD7124Error(ValueError):
    pass

class AD7124:

    def __init__(self, idx, io):
        if idx < 0 or idx > 11:
            raise AD7124Error("Failed to initialize AD7124. Index out of range.")
        
        self.logger = logging.getLogger('smb')
        self.idx = idx  # ADC address
        self.io = io    # GPIO

        # GPIO Pins
        self.mosi = self.io.pin_map['SPI0_MOSI']
        self.miso = self.io.pin_map['SPI0_MISO']
        self.sclk = self.io.pin_map['SPI0_SCLK']
        self.sync = self.io.pin_map['nADC_SYNC']

    def adc_xmit_data(self, readWrite, regAddr, data, dataSize):
        """
        Write data to the ADC
        
        Input:
        - regAddr:  int
        - data:     int
        - dataSize: int
        """
        if dataSize <= 3 and dataSize >= 0:
            regAddr = regAddr & 0x3F  # Force WEN and R/W bits to 0
            
            if readWrite == 1:
                regAddr = regAddr | 0x40  # Force R/W bit to 1 (Read) 

            # N-byte array: register address, bytes 0-2
            if dataSize == 0:
                writeByteArray = regAddr.to_bytes(1, byteorder = 'big')
            else:
                writeByteArray = regAddr.to_bytes(1, byteorder = 'big') + data.to_bytes(dataSize, byteorder = 'big')
            
            GPIO.output(self.sync, 1)  # SYNC (CS) HIGH
            
            self.io.adc_sel(self.idx)  # Select the ADC
            
            GPIO.output(self.sync, 0)  # SYNC (CS) LOW

            for byte in writeByteArray:
                self.__adc_write_byte(byte) 
            
        else:
            raise AD7124Error('Max write size = 24bits, Min write size = 8bits.')

    def __adc_write_byte(self, writeByte):
        """
        Write a single byte to the ADC

        Input:
        - writeByte: 1 byte
        """

        GPIO.output(self.sclk, 0)  # set clock low
        
        for i in range(8):         
            if writeByte & 2**(7-i):
                GPIO.output(self.mosi, 1)
            else:
                GPIO.output(self.mosi, 0)
        
        GPIO.output(self.sclk, 1)  # Clock high

    def adc_write_data(self, regAddr, data, dataSize):
        """
        Write data to the ADC

        Input:
        - regAddr:  int
        - data:     int
        - dataSize: int

        Output:
        - returnData: int
        """

        self.adc_xmit_data(0, regAddr, data, dataSize)
        GPIO.output(self.sync, 1)  # SYNC(CS) HIGH

    def __adc_read_byte(self):
        """
        Write a single byte from the ADC

        Output:
        - readByte: 1 byte
        """
        readByte = 0

        GPIO.output(self.sclk, 0)  # set clock low
        
        for i in range(8):         
            GPIO.output(self.sclk, 1)  # Clock high
            bitVal = GPIO.input(self.miso)
            GPIO.output(self.sclk, 0)  # Clock low
            
            if bitVal == 1:
                readByte = readByte | 2**(7-i)
        
        GPIO.output(self.sclk, 1)  # Clock high
        
        return readByte

    def adc_read_data(self, regAddr, readSize):
        """
        Read data from the ADC

        Input:
        - regAddr:  int
        - readSize: int

        Output:
        - returnData: int
        """

        self.adc_xmit_data(1, regAddr, 0, 0)

        nopComm = 0
        nopByteArray = nopComm.to_bytes(readSize, byteorder = 'big')

        returnBytes = bytearray(0)
        for byte in nopByteArray:
            readByte = self.__adc_read_byte()
            returnBytes.append(readByte)
        
        GPIO.output(self.sync, 1)  # SYNC (CS) HIGH

        # convert bytearray to int
        returnData = int.from_bytes(returnBytes, byteorder = 'big')

        return returnData
