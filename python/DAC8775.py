import GPIO_config
import RPi.GPIO as GPIO
import time
import logging
import Gbl

class DACError(IOError):
    pass

class DAC():

    def __init__(self, idx, io):
        if idx < 0 or idx > 3:
            raise DACError("Failed to initialize DAC. Index out of range.")
        self.idx = idx  # DAC address
        self.io = io  # GPIO
        self.logger = logging.getLogger('DAC-'+str(idx))
        self.mosi = self.io.pin_map['SPI1_MOSI']
        self.miso = self.io.pin_map['SPI1_MISO']
        self.sclk = self.io.pin_map['SPI1_SCLK']
        self.ssa0 = self.io.pin_map['nDAC_SSA0']
        self.ssa1 = self.io.pin_map['nDAC_SSA1']
        self.mss = self.io.pin_map['nDAC_MSS']

    def _slave_select(self):
        """
        Set the SSA1 and SSA0 pins for this DAC
        """

        if self.idx == 0:
            GPIO.output(self.ssa1, 0)  # set SSA1
            GPIO.output(self.ssa0, 0)  # set SSA0 to DAC0
        elif self.idx == 1:
            GPIO.output(self.ssa1, 0)  # set SSA1
            GPIO.output(self.ssa0, 1)  # set SSA0 to DAC1
        elif self.idx == 2:
            GPIO.output(self.ssa1, 1)  # set SSA1
            GPIO.output(self.ssa0, 0)  # set SSA0 to DAC1
        else:
            GPIO.output(self.ssa1, 1)  # set SSA1
            GPIO.output(self.ssa0, 1)  # set SSA0 to DAC1

    def dac_write_data(self, regAddr, data):
        """
        Write data to the DAC
        
        Input:
        - regAddr: int
        - data: int
        """

        # 3-byte array: device address, byte 0, byte 1
        writeByteArray = regAddr.to_bytes(1, byteorder = 'big') + data.to_bytes(2, byteorder = 'big')
        
        GPIO.output(self.mss, 1)  # MSS HIGH

        self._slave_select()

        GPIO.output(self.mss, 0)  # MSS LOW
        GPIO.output(self.sclk, 1)  # set clock high

        for byte in writeByteArray:
            readByte = self._dac_write_byte(byte) 
        
        GPIO.output(self.mss, 1)  # MSS HIGH

    def _dac_write_byte(self, writeByte):
        """
        Write a single byte to the DAC

        Input:
        - writeByte: 1 byte

        Output:
        - readByte: 1 byte
        """
        readByte = 0

        for i in range(8):         
            if writeByte & 2**(7-i):
                GPIO.output(self.mosi, 1)
            else:
                GPIO.output(self.mosi, 0)
            
            GPIO.output(self.sclk, 0)  # Clock low
            bitVal = GPIO.input(self.miso)
            GPIO.output(self.sclk, 1)  # Clock high
            
            if bitVal == 1:
                readByte = readByte | 2**(7-i)

        return readByte

    def dac_read_data(self, regAddr):
        """
        Read data from the DAC

        Input:
        - regAddr: int

        Output:
        - returnData: int
        """

        readRegAddr = regAddr | 0x80
        self.dac_write_data(readRegAddr, 0)

        GPIO.output(self.mss, 1)  # MSS HIGH

        self._slave_select()

        GPIO.output(self.sclk, 0)  # Clock low
        GPIO.output(self.mss, 0)  # MSS LOW
        GPIO.output(self.sclk, 1)  # Clock high

        nopComm = 0
        nopByteArray = nopComm.to_bytes(3, byteorder = 'big')

        returnBytes = bytearray(0)
        for byte in nopByteArray:
            readByte = self._dac_write_byte(byte)
            returnBytes.append(readByte)
        
        GPIO.output(self.mss, 1)  # MSS HIGH

        # convert bytearray to int
        returnData = int.from_bytes(returnBytes, byteorder = 'big')

        return returnData
