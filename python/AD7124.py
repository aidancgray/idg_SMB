# AD7124.py
# 5/24/2021
# Aidan Gray
# aidan.gray@idg.jhu.edu
#
# AD7124 Analog-Digital Converter for the 12 temperature sensors.

import RPi.GPIO as GPIO
import logging
import time
import struct

from polyFit import polyFit

DELAY = 0.00000000004

class AD7124Error(ValueError):
    pass

class AD7124:

    def __init__(self, idx, io, eeprom, tlm, cal):
        if idx < 0 or idx > 11:
            raise AD7124Error("Failed to initialize AD7124. Index out of range.")
        
        self.logger = logging.getLogger('smb')
        self.idx = idx  # ADC address
        self.io = io    # GPIO
        self.eeprom = eeprom
        self.tlm = tlm
        self.cal_dict = cal
        self.calib_fit = None

        # GPIO Pins
        self.mosi = self.io.pin_map['SPI0_MOSI']
        self.miso = self.io.pin_map['SPI0_MISO']
        self.sclk = self.io.pin_map['SPI0_SCLK']
        self.sync = self.io.pin_map['nADC_SYNC']

        # Get initialization data from EEPROM
        self.AD7124_reg_dict = {
                                'ADC_CONTROL':  [0x01, int.from_bytes(self.eeprom.ADCmem[self.idx][0:2], byteorder='big', signed=False), 2], 
                                'IO_CONTROL_1': [0x03, int.from_bytes(self.eeprom.ADCmem[self.idx][2:5], byteorder='big', signed=False), 3],
                                'IO_CONTROL_2': [0x04, int.from_bytes(self.eeprom.ADCmem[self.idx][5:7], byteorder='big', signed=False), 2],
                                'ERROR_EN':     [0x07, int.from_bytes(self.eeprom.ADCmem[self.idx][7:10], byteorder='big', signed=False), 3],
                                'CHANNEL_0':    [0x09, int.from_bytes(self.eeprom.ADCmem[self.idx][10:12], byteorder='big', signed=False), 2],
                                'CHANNEL_1':    [0x0A, int.from_bytes(self.eeprom.ADCmem[self.idx][12:14], byteorder='big', signed=False), 2],
                                'CONFIG_0':     [0x19, int.from_bytes(self.eeprom.ADCmem[self.idx][14:16], byteorder='big', signed=False), 2],
                                'CONFIG_1':     [0x1A, int.from_bytes(self.eeprom.ADCmem[self.idx][16:18], byteorder='big', signed=False), 2],
                                'FILTER_0':     [0x21, int.from_bytes(self.eeprom.ADCmem[self.idx][18:21], byteorder='big', signed=False), 3],
                                'FILTER_1':     [0x22, int.from_bytes(self.eeprom.ADCmem[self.idx][21:24], byteorder='big', signed=False), 3],
                                'OFFSET_0':     [0x29, int.from_bytes(self.eeprom.ADCmem[self.idx][24:27], byteorder='big', signed=False), 3],
                                'OFFSET_1':     [0x2A, int.from_bytes(self.eeprom.ADCmem[self.idx][27:30], byteorder='big', signed=False), 3],
                                'filler':       [0x00, int.from_bytes(self.eeprom.ADCmem[self.idx][30:32], byteorder='big', signed=False), 2],
                                'GAIN_0':       [0x31, int.from_bytes(self.eeprom.ADCmem[self.idx][32:35], byteorder='big', signed=False), 3],
                                'GAIN_1':       [0x32, int.from_bytes(self.eeprom.ADCmem[self.idx][35:38], byteorder='big', signed=False), 3],
                                'SNS_TYP':      [0x00, int.from_bytes(self.eeprom.ADCmem[self.idx][38:39], byteorder='big', signed=False), 1],
                                'SNS_UNITS':    [0x00, int.from_bytes(self.eeprom.ADCmem[self.idx][39:40], byteorder='big', signed=False), 1],
                                'CAL_MODE':     [0x00, int.from_bytes(self.eeprom.ADCmem[self.idx][40:41], byteorder='big', signed=False), 1],
                                'CAL_COEFF_0':  [0x00, int.from_bytes(self.eeprom.ADCmem[self.idx][41:45], byteorder='big', signed=True), 4],
                                'CAL_COEFF_1':  [0x00, int.from_bytes(self.eeprom.ADCmem[self.idx][45:49], byteorder='big', signed=True), 4],
                                'CAL_COEFF_2':  [0x00, int.from_bytes(self.eeprom.ADCmem[self.idx][49:53], byteorder='big', signed=True), 4],
                                'CAL_COEFF_3':  [0x00, int.from_bytes(self.eeprom.ADCmem[self.idx][53:57], byteorder='big', signed=True), 4],
                                'CAL_COEFF_4':  [0x00, int.from_bytes(self.eeprom.ADCmem[self.idx][57:61], byteorder='big', signed=True), 4],
                                'CAL_COEFF_5':  [0x00, int.from_bytes(self.eeprom.ADCmem[self.idx][61:65], byteorder='big', signed=True), 4],
                                'CAL_COEFF_6':  [0x00, int.from_bytes(self.eeprom.ADCmem[self.idx][65:69], byteorder='big', signed=True), 4],
                                'CAL_COEFF_7':  [0x00, int.from_bytes(self.eeprom.ADCmem[self.idx][69:73], byteorder='big', signed=True), 4],
                                'CAL_COEFF_8':  [0x00, int.from_bytes(self.eeprom.ADCmem[self.idx][73:77], byteorder='big', signed=True), 4],
                                'CAL_COEFF_9':  [0x00, int.from_bytes(self.eeprom.ADCmem[self.idx][77:81], byteorder='big', signed=True), 4],
                                'CAL_COEFF_10': [0x00, int.from_bytes(self.eeprom.ADCmem[self.idx][81:85], byteorder='big', signed=True), 4]
                                }

        if self.idx == 0:
            self.AD7124_reg_dict['ADC_CONTROL'][1] += 1
        
        for n in list(self.AD7124_reg_dict)[0:10]:
            register = self.AD7124_reg_dict[n]
            self.__adc_write_data(register[0], register[1], register[2])

        temp_calMode = self.AD7124_reg_dict['CAL_MODE'][1]  # 0=Default Calibration, 1=User set
        self.sns_typ = self.AD7124_reg_dict['SNS_TYP'][1]  # 0=Not set, 1=PT100, 2=PT1000, 3=DIODE
        self.set_sns_units(self.AD7124_reg_dict['SNS_UNITS'][1])  # 0=K, 1=C, 2=F
        self.set_sns_typ()

        if temp_calMode == 1:
            calCoeffs = []
            for i in range(11):
                coeff_int = self.AD7124_reg_dict[f'CAL_COEFF_{i}'][1]
                coeff_float = self.int_to_float(coeff_int, sign=True)
                calCoeffs.append(coeff_float)
            self.calib_fit = polyFit(coeffs=calCoeffs)

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
        self.__adc_write_data(self.AD7124_reg_dict['ADC_CONTROL'][0],
                                self.AD7124_reg_dict['ADC_CONTROL'][1],
                                self.AD7124_reg_dict['ADC_CONTROL'][2])

    def float_to_int(self, f, sign=False):
        i = int.from_bytes(bytearray(struct.pack(">f", f)), byteorder='big', signed=sign)
        return i

    def int_to_float(self, i, sign=False):
        fTmp = struct.unpack(">f", i.to_bytes(4, byteorder='big', signed=sign))
        f= fTmp[0]
        return f

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

    def get_sns_typ(self):
        return self.sns_typ

    def get_sns_units(self):
        return self.sns_units

    def get_calibration_coeffs(self):
        coeffList = []

        for i in range(11):
            coeff_int = self.AD7124_reg_dict[f'CAL_COEFF_{i}'][1]
            coeff_float = self.int_to_float(coeff_int, sign=True)
            coeffList.append(coeff_float)

        return coeffList

    def get_temperature(self):
        if self.calib_fit != None:
            data = self.get_DATA()
            dataTmp = ((float(data) * float(self.vref)) / (float(2**24) * float(self.excit_cur))) / float(self.gain)
            print(f'tmpData={dataTmp}')

            ## For reading diode voltage w/o conversion
            # if self.sns_typ == 3:
            #     temperature = dataTmp
            # else:
            #     temperature = self.calib_fit.calib_t(dataTmp)

            temperature = self.calib_fit.calib_t(dataTmp)

            if self.sns_units == 0:
                temperature = temperature
            elif self.sns_units == 1:
                temperature -= 273.15
            elif self.sns_units == 2:
                temperature = (((temperature - 273.15) * 9) / 5) + 32
        else:
            temperature = -999
        
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

    def set_refin(self, val):
        config_0 = self.get_CONFIG_0()
        
        if val == 1:
            config_0 &=~ (1<<3)
            config_0 &=~ (1<<4)
        elif val == 2:
            config_0 |= (1<<3)
            config_0 &=~ (1<<4)
        elif val == 3:
            config_0 &=~ (1<<3)
            config_0 |= (1<<4)
        elif val == 4:
            config_0 |= (1<<3)
            config_0 |= (1<<4)
        
        self.set_CONFIG_0(config_0)

    def set_refV(self, val):
        io_control_1 = self.get_IO_CONTROL_1()
        
        if val == 'hi':
            io_control_1 &=~ (1<<22)
        elif val == 'lo':
            io_control_1 |= (1<<22)

        self.set_IO_CONTROL_1(io_control_1)

    def set_2_4_wire(self, val):
        io_control_1 = self.get_IO_CONTROL_1()
        
        if val == 2:
            io_control_1 &=~ (1<<15)
        elif val == 4:
            io_control_1 |= (1<<15)

        self.set_IO_CONTROL_1(io_control_1)

    def set_sns_typ(self, sns=None):
        if sns != None:
            self.sns_typ = sns

        self.AD7124_reg_dict['SNS_TYP'][1] = self.sns_typ

        if self.sns_typ == 1:
            # PT-100 2-Wire
            self.set_excitation_current(3)  # 3=250uA
            self.set_pga(16)  # 16=16x Gain
            self.set_refin(1)  # 1=REFIN1(+)/REFIN1(-)
            self.set_refV('lo')  # 'lo'=small resistor
            self.set_2_4_wire(2)
            self.vref = 0.98
            self.excit_cur = 0.000250
            self.gain = 16
            calCoeffs = self.cal_dict['PT100']
            self.calib_fit = polyFit(coeffs=calCoeffs)
            self.calMode = 0
            self.AD7124_reg_dict['CAL_MODE'][1] = 0
        
        elif self.sns_typ == 2:
            # PT-100 4-Wire
            self.set_excitation_current(3)  # 3=250uA
            self.set_pga(16)  # 16=16x Gain
            self.set_refin(1)  # 1=REFIN1(+)/REFIN1(-)
            self.set_refV('lo')  # 'lo'=small resistor
            self.set_2_4_wire(4)
            self.vref = 0.98
            self.excit_cur = 0.000250
            self.gain = 16
            calCoeffs = self.cal_dict['PT100']
            self.calib_fit = polyFit(coeffs=calCoeffs)
            self.calMode = 0
            self.AD7124_reg_dict['CAL_MODE'][1] = 0

        elif self.sns_typ == 3:
            # PT-1000 2-Wire
            self.set_excitation_current(3)  # 3=250uA
            self.set_pga(2)  # 2=2x Gain
            self.set_refin(1)  # 1=REFIN1(+)/REFIN1(-)
            self.set_refV('lo')  # 'lo'=small resistor
            self.set_2_4_wire(2)
            self.vref = 0.98
            self.excit_cur = 0.000250
            self.gain = 2
            calCoeffs = self.cal_dict['PT1000']
            self.calib_fit = polyFit(coeffs=calCoeffs)
            self.calMode = 0
            self.AD7124_reg_dict['CAL_MODE'][1] = 0

        elif self.sns_typ == 4:
            # PT-1000 4-Wire
            self.set_excitation_current(3)  # 3=250uA
            self.set_pga(2)  # 2=2x Gain
            self.set_refin(1)  # 1=REFIN1(+)/REFIN1(-)
            self.set_refV('lo')  # 'lo'=small resistor
            self.set_2_4_wire(4)
            self.vref = 0.98
            self.excit_cur = 0.000250
            self.gain = 2
            calCoeffs = self.cal_dict['PT1000']
            self.calib_fit = polyFit(coeffs=calCoeffs)
            self.calMode = 0
            self.AD7124_reg_dict['CAL_MODE'][1] = 0
        
        elif self.sns_typ == 5:
            # DIODE 2-Wire
            self.set_excitation_current(1)  # 1=50uA
            self.set_pga(1)  # 1=1x Gain
            self.set_refin(3)  # 3=internal reference
            self.set_refV('lo')  # 'lo'=small resistor
            self.set_2_4_wire(2)
            self.vref = 2.5
            self.excit_cur = 1.0  # measuring voltage, so don't divide by excitation current
            self.gain = 1
            calCoeffs = self.cal_dict['DIODE']
            self.calib_fit = polyFit(coeffs=calCoeffs)
            self.calMode = 0
            self.AD7124_reg_dict['CAL_MODE'][1] = 0

        elif self.sns_typ == 6:
            # DIODE 4-Wire
            self.set_excitation_current(4)  # 1=50uA
            self.set_pga(1)  # 1=1x Gain
            self.set_refin(3)  # 3=internal reference
            self.set_refV('lo')  # 'lo'=small resistor
            self.set_2_4_wire(4)
            self.vref = 2.5
            self.excit_cur = 1.0  # measuring voltage, so don't divide by excitation current
            self.gain = 1
            calCoeffs = self.cal_dict['DIODE']
            self.calib_fit = polyFit(coeffs=calCoeffs)
            self.calMode = 0
            self.AD7124_reg_dict['CAL_MODE'][1] = 0
        
        else:
            self.vref = 0
            self.excit_cur = 0
            self.gain = 0
            self.calib_fit = None
            self.calMode = 0
            self.AD7124_reg_dict['CAL_MODE'][1] = 0

    def set_sns_units(self, units):
        if units == 0 or units == 1 or units == 2:
            self.AD7124_reg_dict['SNS_UNITS'][1] = units
            self.sns_units = units

            if units == 0:
                sns_units = 'K'
            elif units == 1:
                sns_units = 'C'
            elif units == 2:
                sns_units = 'F'
            else:
                raise ValueError(f"Unknown Sensor Units:{units} 0=K, 1=C, 2=F")

            self.tlm['sns_temp_'+str(self.idx+1)] = sns_units
        else:
            raise AD7124Error("Invalid sensor unit type. Must be 0, 1, 2.")

    def set_calibration(self, calData):
        polyCal = polyFit(calData, 10)
        self.calib_fit = polyCal
    
    def set_calibration_coeffs(self, calCoeffs):
        calCoeffs_float = []

        # Clear out all coefficients
        for i in range(11):
            coeff_int = self.float_to_int(0.0, sign=True)
            self.AD7124_reg_dict[f'CAL_COEFF_{i}'][1] = coeff_int

        # Fill in new coefficients
        for i in range(len(calCoeffs)):
            coeff_string = calCoeffs[i]

            try:
                coeff_float = float(coeff_string)
            except ValueError:
                return 'BAD: Coefficient not of type float.'

            calCoeffs_float.append(coeff_float)
            coeff_int = self.float_to_int(coeff_float, sign=True)
            self.AD7124_reg_dict[f'CAL_COEFF_{i}'][1] = coeff_int
        
        polyCal = polyFit(coeffs=calCoeffs_float)
        self.calib_fit = polyCal
        self.calMode = 1
        self.AD7124_reg_dict['CAL_MODE'][1] = 1
        return 'OK'

    def update_eeprom_mem(self):
        ADCbyteArray = bytearray()

        for reg in self.AD7124_reg_dict:
            register = self.AD7124_reg_dict[reg]

            if 'CAL_COEFF_' in reg:
                regByteArray = register[1].to_bytes(register[2], byteorder='big', signed=True)
            else:
                regByteArray = register[1].to_bytes(register[2], byteorder='big', signed=False)

            ADCbyteArray.extend(regByteArray)

        self.eeprom.ADCmem[self.idx] = ADCbyteArray