import GPIO_config
import RPi.GPIO as GPIO
import time
import Gbl

class DAC():

    def __init__(self, idx, io):
        self.idx = idx  # DAC address
        self.io = io  # GPIO
        self.mosi = self.io.pin_map['SPI1_MOSI']
        self.miso = self.io.pin_map['SPI1_MISO']
        self.sclk = self.io.pin_map['SPI1_SCLK']

    def dac_write_data(self, data):
        """
        Write data to the DAC
        
        Input:
        - data: int
        """

        # 3-byte array: device address, byte 0, byte 1
        writeByteArray = idx.to_bytes(1, byteorder = 'big') + data.to_bytes(2, byteorder = 'big')
        
        # set clock high
        GPIO.output(self.sclk, 1)

        # set chip select (SYNC) low

        for byte in dataByteArray:
            self._dac_write_byte(byte) 
        
        # set chip select (SYNC) high


    def _dac_write_byte(self, byte):
        """
        Write a single byte to the DAC

        Input:
        - byte: 8-bit byte
        """

        for i in range(8):         
            if byte & 2^^(7-i):
                GPIO.output(self.mosi, 1)
            else:
                GPIO.output(self.mosi, 0)
            
            GPIO.output(self.sclk, 0)
            GPIO.output(self.sclk, 1)

