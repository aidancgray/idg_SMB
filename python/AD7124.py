# AD7124.py
# 5/24/2021
# Aidan Gray
# aidan.gray@idg.jhu.edu
#
# 

import RPi.GPIO as GPIO
import logging
import time

DELAY = 0.00000000004

class AD7124Error(ValueError):
    pass

class AD7124:

    def __init__(self, idx, io, eeprom):
        if idx < 0 or idx > 11:
            raise AD7124Error("Failed to initialize AD7124. Index out of range.")
        
        self.logger = logging.getLogger('smb')
        self.idx = idx  # ADC address
        self.io = io    # GPIO
        self.eeprom = eeprom

        # GPIO Pins
        self.mosi = self.io.pin_map['SPI0_MOSI']
        self.miso = self.io.pin_map['SPI0_MISO']
        self.sclk = self.io.pin_map['SPI0_SCLK']
        self.sync = self.io.pin_map['nADC_SYNC']

        ## Get initialization data from EEPROM
        # self.AD7124_reg_dict = {
        #                         'ADC_CONTROL':  (0x01, int.from_bytes(self.eeprom.ADCmem[self.idx][0:2], byteorder='big'), 2), 
        #                         'IO_CONTROL_1': (0x03, int.from_bytes(self.eeprom.ADCmem[self.idx][2:5], byteorder='big'), 3),
        #                         'IO_CONTROL_2': (0x04, int.from_bytes(self.eeprom.ADCmem[self.idx][5:7], byteorder='big'), 2),
        #                         'ERROR_EN':     (0x07, int.from_bytes(self.eeprom.ADCmem[self.idx][7:10], byteorder='big'), 3),
        #                         'CHANNEL_0':    (0x09, int.from_bytes(self.eeprom.ADCmem[self.idx][10:12], byteorder='big'), 2),
        #                         'CHANNEL_1':    (0x0A, int.from_bytes(self.eeprom.ADCmem[self.idx][12:14], byteorder='big'), 2),
        #                         'CONFIG_0':     (0x19, int.from_bytes(self.eeprom.ADCmem[self.idx][14:16], byteorder='big'), 2),
        #                         'CONFIG_1':     (0x1A, int.from_bytes(self.eeprom.ADCmem[self.idx][16:18], byteorder='big'), 2),
        #                         'FILTER_0':     (0x21, int.from_bytes(self.eeprom.ADCmem[self.idx][18:21], byteorder='big'), 3),
        #                         'FILTER_1':     (0x22, int.from_bytes(self.eeprom.ADCmem[self.idx][21:24], byteorder='big'), 3),
        #                         'OFFSET_0':     (0x29, int.from_bytes(self.eeprom.ADCmem[self.idx][24:27], byteorder='big'), 3),
        #                         'OFFSET_1':     (0x2A, int.from_bytes(self.eeprom.ADCmem[self.idx][27:30], byteorder='big'), 3),
        #                         'GAIN_0':       (0x31, int.from_bytes(self.eeprom.ADCmem[self.idx][30:33], byteorder='big'), 3),
        #                         'GAIN_1':       (0x32, int.from_bytes(self.eeprom.ADCmem[self.idx][33:36], byteorder='big'), 3)
        #                         }

        # Custom-set initialization data
        self.AD7124_reg_dict = {
                                'ADC_CONTROL':  [0x01, 0x1304, 2], 
                                'IO_CONTROL_1': [0x03, 0x041200, 3],
                                'IO_CONTROL_2': [0x04, 0x0000, 2],
                                'ERROR_EN':     [0x07, 0x000040, 3],
                                'CHANNEL_0':    [0x09, 0x8023, 2],
                                'CHANNEL_1':    [0x0A, 0x0000, 2],
                                'CONFIG_0':     [0x19, 0x01E0, 2],
                                'CONFIG_1':     [0x1A, 0x01E0, 2],
                                'FILTER_0':     [0x21, 0x060180, 3],
                                'FILTER_1':     [0x22, 0x060180, 3]}
                                # 'OFFSET_0':     (0x29, 0x800000, 3),
                                # 'OFFSET_1':     (0x2A, 0x800000, 3),
                                # 'GAIN_0':       (0x31, 0x500000, 3),
                                # 'GAIN_1':       (0x32, 0x500000, 3)
                                # }
        if self.idx == 0:
            self.AD7124_reg_dict['ADC_CONTROL'][1] = 0x1305

        for n in self.AD7124_reg_dict:
            register = self.AD7124_reg_dict[n]
            self.__adc_write_data(register[0], register[1], register[2])
    

    def reset(self):
        data2 = 65535
        data3 = 16777215

        # Write 64 1's in a row to reset the AD7124
        self.__adc_xmit_data(0, 0, data3, 3)
        self.__adc_xmit_data(0, 0, data3, 3)
        self.__adc_xmit_data(0, 0, data2, 2)

        GPIO.output(self.sync, 1)  # SYNC(CS) HIGH
        time.sleep(DELAY)

    def __adc_xmit_data(self, readWrite, regAddr, data, dataSize):
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
            
            GPIO.output(self.sclk, 1)  # set clock high
        
        else:
            raise AD7124Error('Max write size = 24bits, Min write size = 8bits.')

    def __adc_write_byte(self, writeByte):
        """
        Write a single byte to the ADC

        Input:
        - writeByte: 1 byte
        """
        
        for i in range(8):
            GPIO.output(self.sclk, 0)  # set clock low         
            if writeByte & 2**(7-i):
                GPIO.output(self.mosi, 1)
            else:
                GPIO.output(self.mosi, 0)
            GPIO.output(self.sclk, 1)  # Clock high

    def __adc_write_data(self, regAddr, data, dataSize):
        """
        Write data to the ADC

        Input:
        - regAddr:  int
        - data:     int
        - dataSize: int

        Output:
        - returnData: int
        """

        self.__adc_xmit_data(0, regAddr, data, dataSize)
        GPIO.output(self.sync, 1)  # SYNC(CS) HIGH
        time.sleep(DELAY)

    def __adc_read_byte(self):
        """
        Write a single byte from the ADC

        Output:
        - readByte: 1 byte
        """
        readByte = 0

        GPIO.output(self.sclk, 1)  # set clock high
        
        for i in range(8):         
            GPIO.output(self.sclk, 0)  # Clock low
            bitVal = GPIO.input(self.miso)
            GPIO.output(self.sclk, 1)  # Clock high
            
            if bitVal == 1:
                readByte = readByte | 2**(7-i)

        GPIO.output(self.sclk, 1)  # Clock high
        
        return readByte

    def __adc_read_data(self, regAddr, readSize):
        """
        Read data from the ADC

        Input:
        - regAddr:  int
        - readSize: int

        Output:
        - returnData: int
        """

        self.__adc_xmit_data(1, regAddr, 0, 0)

        nopComm = 0
        nopByteArray = nopComm.to_bytes(readSize, byteorder = 'big')

        returnBytes = bytearray(0)
        for byte in nopByteArray:
            readByte = self.__adc_read_byte()
            returnBytes.append(readByte)
        
        GPIO.output(self.sync, 1)  # SYNC (CS) HIGH
        time.sleep(DELAY)

        # convert bytearray to int
        returnData = int.from_bytes(returnBytes, byteorder = 'big')

        return returnData

    def __reset_conversion_mode(self):
        self.__adc_write_data(self.AD7124_reg_dict['ADC_CONTROL'][0], self.AD7124_reg_dict['ADC_CONTROL'][1], self.AD7124_reg_dict['ADC_CONTROL'][2])

    def get_STATUS(self):
        return self.__adc_read_data(0x00, 1)

    def get_ADC_CONTROL(self):
        return self.__adc_read_data(0x01, 2)

    def get_DATA(self):
        data = self.__adc_read_data(0x02, 3)
        self.__reset_conversion_mode()
        return data

    def get_IO_CONTROL_1(self):
        return self.__adc_read_data(0x03, 3)
    
    def get_IO_CONTROL_2(self):
        return self.__adc_read_data(0x04, 2)

    def get_ID(self):
        return self.__adc_read_data(0x05, 1)

    def get_ERROR(self):
        return self.__adc_read_data(0x06, 3)

    def get_ERROR_EN(self):
        return self.__adc_read_data(0x07, 3)

    def get_MCLK_COUNT(self):
        return self.__adc_read_data(0x08, 1)

    def get_CHANNEL_0(self):
        return self.__adc_read_data(0x09, 2)

    def get_CHANNEL_1(self):
        return self.__adc_read_data(0x0A, 2)

    def get_CONFIG_0(self):
        return self.__adc_read_data(0x19, 2)

    def get_CONFIG_1(self):
        return self.__adc_read_data(0x1A, 2)

    def get_FILTER_0(self):
        return self.__adc_read_data(0x21, 3)
    
    def get_FILTER_1(self):
        return self.__adc_read_data(0x22, 3)

    def get_OFFSET_0(self):
        return self.__adc_read_data(0x29, 3)

    def get_OFFSET_1(self):
        return self.__adc_read_data(0x2A, 3)

    def get_GAIN_0(self):
        return self.__adc_read_data(0x31, 3)

    def get_GAIN_1(self):
        return self.__adc_read_data(0x32, 3)