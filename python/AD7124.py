# AD7124.py
# 5/24/2021
# Aidan Gray
# aidan.gray@idg.jhu.edu
#
# AD7124 Analog-Digital Converter for the 12 temperature sensors.

import RPi.GPIO as GPIO
import logging
import time

from polyFit import polyFit

DELAY = 0.00000000004

class AD7124Error(ValueError):
    pass

class AD7124:

    def __init__(self, idx, io, eeprom, sns_typ=None, sns_units=None):
        if idx < 0 or idx > 11:
            raise AD7124Error("Failed to initialize AD7124. Index out of range.")
        
        self.logger = logging.getLogger('smb')
        self.idx = idx  # ADC address
        self.io = io    # GPIO
        self.eeprom = eeprom
        self.sns_typ = sns_typ
        self.sns_units = sns_units

        # GPIO Pins
        self.mosi = self.io.pin_map['SPI0_MOSI']
        self.miso = self.io.pin_map['SPI0_MISO']
        self.sclk = self.io.pin_map['SPI0_SCLK']
        self.sync = self.io.pin_map['nADC_SYNC']

        # Get initialization data from EEPROM
        self.AD7124_reg_dict = {
                                'ADC_CONTROL':  [0x01, int.from_bytes(self.eeprom.ADCmem[self.idx][0:2], byteorder='big'), 2], 
                                'IO_CONTROL_1': [0x03, int.from_bytes(self.eeprom.ADCmem[self.idx][2:5], byteorder='big'), 3],
                                'IO_CONTROL_2': [0x04, int.from_bytes(self.eeprom.ADCmem[self.idx][5:7], byteorder='big'), 2],
                                'ERROR_EN':     [0x07, int.from_bytes(self.eeprom.ADCmem[self.idx][7:10], byteorder='big'), 3],
                                'CHANNEL_0':    [0x09, int.from_bytes(self.eeprom.ADCmem[self.idx][10:12], byteorder='big'), 2],
                                'CHANNEL_1':    [0x0A, int.from_bytes(self.eeprom.ADCmem[self.idx][12:14], byteorder='big'), 2],
                                'CONFIG_0':     [0x19, int.from_bytes(self.eeprom.ADCmem[self.idx][14:16], byteorder='big'), 2],
                                'CONFIG_1':     [0x1A, int.from_bytes(self.eeprom.ADCmem[self.idx][16:18], byteorder='big'), 2],
                                'FILTER_0':     [0x21, int.from_bytes(self.eeprom.ADCmem[self.idx][18:21], byteorder='big'), 3],
                                'FILTER_1':     [0x22, int.from_bytes(self.eeprom.ADCmem[self.idx][21:24], byteorder='big'), 3],
                                'OFFSET_0':     [0x29, int.from_bytes(self.eeprom.ADCmem[self.idx][24:27], byteorder='big'), 3],
                                'OFFSET_1':     [0x2A, int.from_bytes(self.eeprom.ADCmem[self.idx][27:30], byteorder='big'), 3],
                                'GAIN_0':       [0x31, int.from_bytes(self.eeprom.ADCmem[self.idx][30:33], byteorder='big'), 3],
                                'GAIN_1':       [0x32, int.from_bytes(self.eeprom.ADCmem[self.idx][33:36], byteorder='big'), 3]
                                }

        if self.idx == 0:
            self.AD7124_reg_dict['ADC_CONTROL'][1] = 0x1305
        
        for n in list(self.AD7124_reg_dict)[0:10]:
            register = self.AD7124_reg_dict[n]
            self.__adc_write_data(register[0], register[1], register[2])

        if self.sns_typ == 1:
            # PT-100
            self.set_excitation_current(3)
            self.set_pga(16)
            self.set_refV('lo')
            self.vref = 0.98
            self.excit_cur = 0.000250
            self.gain = 16

            #self.calib_fit = polyFit(coeffs=)

        elif self.sns_typ == 2:
            # PT-1000
            self.set_excitation_current(3)
            self.set_pga(2)
            self.set_refV('lo')
            self.vref = 0.98
            self.excit_cur = 0.000250
            self.gain = 2
        
        elif self.sns_typ == 3:
            # DIODE
            self.set_excitation_current(1)
            self.set_pga(1)
            self.set_refV('hi')
            self.vref = 1.96
            self.excit_cur = 0.000050
            self.gain = 1

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

    ### GETTERS ###
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

    def get_excitation_current(self):
        io_control_1 = self.get_IO_CONTROL_1()
        return io_control_1 >> 11 & 0b111

    def get_temperature(self):
        data = self.get_DATA()
        resistance = ((float(data) * float(self.vref)) / (float(2**24) * float(self.excit_cur))) / float(self.gain)
        # TODO:
        # get calibration
        temperature = resistance
        
        return temperature

    ### SETTERS ###
    def set_ADC_CONTROL(self, data):
        self.AD7124_reg_dict['ADC_CONTROL'][1] = data
        self.__adc_write_data(0x01, data, 2)
    
    def set_IO_CONTROL_1(self, data):
        self.AD7124_reg_dict['IO_CONTROL_1'][1] = data
        self.__adc_write_data(0x03, data, 3)
    
    def set_IO_CONTROL_2(self, data):
        self.AD7124_reg_dict['IO_CONTROL_2'][1] = data
        self.__adc_write_data(0x04, data, 2)

    def set_ERROR_EN(self, data):
        self.AD7124_reg_dict['ERROR_EN'][1] = data
        self.__adc_write_data(0x07, data, 3)

    def set_CHANNEL_0(self, data):
        self.AD7124_reg_dict['CHANNEL_0'][1] = data
        self.__adc_write_data(0x09, data, 2)

    def set_CHANNEL_1(self, data):
        self.AD7124_reg_dict['CHANNEL_1'][1] = data
        self.__adc_write_data(0x0A, data, 2)

    def set_CONFIG_0(self, data):
        self.AD7124_reg_dict['CONFIG_0'][1] = data
        self.__adc_write_data(0x19, data, 2)

    def set_CONFIG_1(self, data):
        self.AD7124_reg_dict['CONFIG_1'][1] = data
        self.__adc_write_data(0x1A, data, 2)

    def set_FILTER_0(self, data):
        self.AD7124_reg_dict['FILTER_0'][1] = data
        self.__adc_write_data(0x21, data, 3)
    
    def set_FILTER_1(self, data):
        self.AD7124_reg_dict['FILTER_1'][1] = data
        self.__adc_write_data(0x22, data, 3)

    def set_OFFSET_0(self, data):
        self.AD7124_reg_dict['OFFSET_0'][1] = data
        self.__adc_write_data(0x29, data, 3)

    def set_OFFSET_1(self, data):
        self.AD7124_reg_dict['OFFSET_1'][1] = data
        self.__adc_write_data(0x2A, data, 3)

    def set_GAIN_0(self, data):
        self.AD7124_reg_dict['GAIN_0'][1] = data
        self.__adc_write_data(0x31, data, 3)

    def set_GAIN_1(self, data):
        self.AD7124_reg_dict['GAIN_1'][1] = data
        self.__adc_write_data(0x32, data, 3)

    def set_excitation_current(self, val):
        io_control_1 = self.get_IO_CONTROL_1()
        
        if val == 0:
            io_control_1 &=~ (1<<11)
            io_control_1 &=~ (1<<12)
            io_control_1 &=~ (1<<13)
        elif val == 1:
            io_control_1 |= (1<<11)
            io_control_1 &=~ (1<<12)
            io_control_1 &=~ (1<<13)
        elif val == 2:
            io_control_1 &=~ (1<<11)
            io_control_1 |= (1<<12)
            io_control_1 &=~ (1<<13)
        elif val == 3:
            io_control_1 |= (1<<11)
            io_control_1 |= (1<<12)
            io_control_1 &=~ (1<<13)
        elif val == 4:
            io_control_1 &=~ (1<<11)
            io_control_1 &=~ (1<<12)
            io_control_1 |= (1<<13)
        elif val == 5:
            io_control_1 |= (1<<11)
            io_control_1 &=~ (1<<12)
            io_control_1 |= (1<<13)
        elif val == 6 or val == 7:
            io_control_1 |= (1<<11)
            io_control_1 |= (1<<12)
            io_control_1 |= (1<<13)
        
        self.set_IO_CONTROL_1(io_control_1)

    def set_pga(self, val):
        config_0 = self.get_CONFIG_0()
        
        if val == 1:
            config_0 &=~ (1<<0)
            config_0 &=~ (1<<1)
            config_0 &=~ (1<<2)
        elif val == 2:
            config_0 |= (1<<0)
            config_0 &=~ (1<<1)
            config_0 &=~ (1<<2)
        elif val == 4:
            config_0 &=~ (1<<0)
            config_0 |= (1<<1)
            config_0 &=~ (1<<2)
        elif val == 8:
            config_0 |= (1<<0)
            config_0 |= (1<<1)
            config_0 &=~ (1<<2)
        elif val == 16:
            config_0 &=~ (1<<0)
            config_0 &=~ (1<<1)
            config_0 |= (1<<2)
        elif val == 32:
            config_0 |= (1<<0)
            config_0 &=~ (1<<1)
            config_0 |= (1<<2)
        elif val == 64:
            config_0 &=~ (1<<0)
            config_0 |= (1<<1)
            config_0 |= (1<<2)
        elif val == 128:
            config_0 |= (1<<0)
            config_0 |= (1<<1)
            config_0 |= (1<<2)
        
        self.set_CONFIG_0(config_0)

    def set_refV(self, val):
        io_control_1 = self.get_IO_CONTROL_1()
        
        if val == 'hi':
            io_control_1 &=~ (1<<22)
        elif val == 'lo':
            io_control_1 |= (1<<22)

        self.set_IO_CONTROL_1(io_control_1)

    def update_eeprom_mem(self):
        ADCbyteArray = bytearray()

        for reg in self.AD7124_reg_dict:
            register = self.AD7124_reg_dict[reg]
            regByteArray = register[1].to_bytes(register[2], byteorder='big')
            ADCbyteArray.extend(regByteArray)

        self.eeprom.ADCmem[self.idx] = ADCbyteArray