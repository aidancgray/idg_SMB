# DAC8775.py
# 5/24/2021
# Aidan Gray
# aidan.gray@idg.jhu.edu
#
# Class for a DAC module. This board consists of four (4) DACs. 

from AD7124 import AD7124Error
import RPi.GPIO as GPIO
import logging
import numpy as np
import struct

MAX_VOLTAGE = 28 # Volts
MAX_CURRENT = 0.096 # Amps (24mA per channel)
DSDO_BIT = 2**4

class DACError(ValueError):
    pass

class DAC():

    def __init__(self, idx, io, eeprom, tlm):
        if idx < 0 or idx > 3:
            raise DACError("Failed to initialize DAC. Index out of range.")

        self.logger = logging.getLogger('smb')
        self.idx = idx  # DAC number 0-3
        self.io = io    # GPIO
        self.eeprom = eeprom
        self.tlm = tlm
        self.max_current = 0
        self.power = 0

        self.DAC_reg_dict = {
                            'MODE':         [0x00, int.from_bytes(self.eeprom.DACmem[self.idx][0:2], byteorder='big', signed=False), 2],
                            'SNS_NUM':      [0x00, int.from_bytes(self.eeprom.DACmem[self.idx][2:4], byteorder='big', signed=False), 2],
                            'SETPOINT':     [0x00, int.from_bytes(self.eeprom.DACmem[self.idx][4:8], byteorder='big', signed=True), 4],
                            'KP':           [0x00, int.from_bytes(self.eeprom.DACmem[self.idx][8:12], byteorder='big', signed=False), 4],
                            'KI':           [0x00, int.from_bytes(self.eeprom.DACmem[self.idx][12:16], byteorder='big', signed=False), 4],
                            'KD':           [0x00, int.from_bytes(self.eeprom.DACmem[self.idx][16:20], byteorder='big', signed=False), 4],
                            'HTR_RES':      [0x00, int.from_bytes(self.eeprom.DACmem[self.idx][20:24], byteorder='big', signed=False), 4],
                            'HYSTERESIS':   [0x00, int.from_bytes(self.eeprom.DACmem[self.idx][24:28], byteorder='big', signed=False), 4],
                            'MAX_TEMP':     [0x00, int.from_bytes(self.eeprom.DACmem[self.idx][28:32], byteorder='big', signed=True), 4],
                            'MIN_TEMP':     [0x00, int.from_bytes(self.eeprom.DACmem[self.idx][32:36], byteorder='big', signed=True), 4],
                            'FIXED_PERCENT':[0x00, int.from_bytes(self.eeprom.DACmem[self.idx][36:40], byteorder='big', signed=False), 4],
                            'CONTROL_VAR':  [0x00, int.from_bytes(self.eeprom.DACmem[self.idx][40:44], byteorder='big', signed=False), 4]
                            }

        # GPIO Pins
        self.mosi = self.io.pin_map['SPI1_MOSI']
        self.miso = self.io.pin_map['SPI1_MISO']
        self.sclk = self.io.pin_map['SPI1_SCLK']
        self.ssa0 = self.io.pin_map['nDAC_SSA0']
        self.ssa1 = self.io.pin_map['nDAC_SSA1']
        self.mss = self.io.pin_map['nDAC_MSS']

        self.dac_write_data(0x06, 15)  # Select all Buck-Boost Converters
        for i in range(4):
            channelSelect = DSDO_BIT | 2**(5+i)
            self.dac_write_data(0x03, channelSelect)    # Select each channel           

            self.dac_write_data(0x04, 4102)  # Write the DAC Config Registers
            self.dac_write_data(0x07, 1601)  # Write the BB Config Registers

        # Heater Parameters
        self.__set_sns_num(self.DAC_reg_dict['SNS_NUM'][1])                                         # Sensor (AD7124) number (1-12)
        self.__set_kp(self.int_to_float(self.DAC_reg_dict['KP'][1], sign=False))                    # proportional term
        self.__set_ki(self.int_to_float(self.DAC_reg_dict['KI'][1], sign=False))                    # integral term
        self.__set_kd(self.int_to_float(self.DAC_reg_dict['KD'][1], sign=False))                    # derivative term
        self.__set_it(0)                                                                            # total integral term
        self.__set_etPrev(0)                                                                        # the previous error value
        self.__set_setPoint(self.int_to_float(self.DAC_reg_dict['SETPOINT'][1], sign=True))         # setpoint
        self.__set_htr_res(self.int_to_float(self.DAC_reg_dict['HTR_RES'][1], sign=False))          # Heater resistance
        self.__set_hysteresis(self.int_to_float(self.DAC_reg_dict['HYSTERESIS'][1], sign=False))    # Allowable range for HIPWR
        self.__set_rebootMode(False)                                                                # False: Reset PID values on reboot
        self.__set_max_temp(self.int_to_float(self.DAC_reg_dict['MAX_TEMP'][1], sign=True))         # Maximum temperature before heater shutoff
        self.__set_min_temp(self.int_to_float(self.DAC_reg_dict['MIN_TEMP'][1], sign=True))         # Minimum temperature before cooler shutoff
        self.__set_fixed_percent(self.int_to_float(self.DAC_reg_dict['FIXED_PERCENT'][1], sign=False))  # Fixed Percent value (0.0 -> 1.0)
        self.__set_mode(self.DAC_reg_dict['MODE'][1])                                               # 0=DISABLED, 1=Fixed%, 2=PID, or 3=Set Current
        self.__set_controlVar(self.int_to_float(self.DAC_reg_dict['CONTROL_VAR'][1], sign=False))   # control variable

    """
    DAC Functions: read/write/etc
    """

    def __slave_select(self):
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
            GPIO.output(self.ssa0, 0)  # set SSA0 to DAC2
        elif self.idx == 3:
            GPIO.output(self.ssa1, 1)  # set SSA1
            GPIO.output(self.ssa0, 1)  # set SSA0 to DAC3
        else:
            GPIO.output(self.ssa1, 1)  # set SSA1
            GPIO.output(self.ssa0, 1)  # set SSA0 to DAC3

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

        self.__slave_select()

        GPIO.output(self.mss, 0)  # MSS LOW
        GPIO.output(self.sclk, 1)  # set clock high

        for byte in writeByteArray:
            readByte = self.__dac_write_byte(byte) 

        GPIO.output(self.mss, 1)  # MSS HIGH

    def __dac_write_byte(self, writeByte):
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

        self.__slave_select()

        GPIO.output(self.sclk, 0)  # Clock low
        GPIO.output(self.mss, 0)  # MSS LOW
        GPIO.output(self.sclk, 1)  # Clock high

        nopComm = 0
        nopByteArray = nopComm.to_bytes(3, byteorder = 'big')

        returnBytes = bytearray(0)
        for byte in nopByteArray:
            readByte = self.__dac_write_byte(byte)
            returnBytes.append(readByte)
        
        GPIO.output(self.mss, 1)  # MSS HIGH

        # convert bytearray to int
        returnData = int.from_bytes(returnBytes[1:3], byteorder = 'big')

        return returnData

    def dac_update(self, temp, units):
        if self.__mode == 2:
            self.pid_update(temp, units)
        else:
            raise DACError("Invalid mode set. Cannot update DAC.")

    def fp_update(self):
        self.tlm[f'dac_fp_{self.idx+1}'] = self.fixed_percent
        self.max_power = (self.max_current ** 2) * self.htr_res
        self.power = self.max_power * self.fixed_percent
        self.controlVar = self.power_to_current(self.power)
        self.write_control_var(self.controlVar)

    def set_current_update(self):
        self.write_control_var(self.controlVar)

    def pid_update(self, pv, units, dt=1):
        """
        Update the PID values. The default functionality assumes PID updates
        are occurring at 1Hz. If this frequency is changed, you must pass the 
        delta-time into the pid_update() function after the process variable,
        which is the measured temperature.

        Input:
        - pv: float
        - dt: change in time (default 1s)
        """

        # Convert to Kelvin (0=K, 1=C, 2=F)
        if units == 0:
            pv = pv
        elif units == 1:
            pv += 273.15
        elif units == 2:
            pv = ((pv - 32) * (5 / 9)) + 273.15
        else:
            raise AD7124Error("Invalid units. Cannot update DAC.")

        # Convert Setpoint to Kelvin
        spUnits = self.tlm['sns_temp_'+str(self.sns_num)]
        if spUnits == 'K':
            setPointK = self.setPoint
        elif spUnits == 'C':
            setPointK = self.setPoint + 273.15
        elif spUnits == 'F':
            setPointK = ((self.setPoint - 32) * (5 / 9)) + 273.15
        else:
            raise AD7124Error("Invalid units. Cannot update DAC.")

        et = setPointK - pv # calculate e(t)
        d_et = ( et - self.etPrev ) / dt  # calculate de(t)/dt
        self.it = self.it + ( self.ki * et * dt )  # add to the integral term
        self.etPrev = et  # set the previous error term (for next time)

        # calculate the new control variable
        p_term = self.kp * et
        i_term = self.it
        d_term = self.kd * d_et

        # Maximum current is set by the maximum voltage and the heater's resistance
        self.max_current = MAX_VOLTAGE / self.htr_res
        if self.max_current > MAX_CURRENT:
            self.max_current = MAX_CURRENT

        max_i_term = self.max_current**2 * self.htr_res * 1000
        #print(f'p_term={p_term}')
        #print(f'i_term={i_term}')
        
        if i_term > max_i_term:
            self.it = max_i_term / self.ki
            i_term = max_i_term
        elif i_term < 0:
            self.it = 0
            i_term = 0

        controlVarTmp = p_term + i_term + d_term
        controlVarTmp = controlVarTmp / 1000.0  # Watts

        self.power = controlVarTmp

        # convert control variable (power) to current
        self.controlVar = self.power_to_current(controlVarTmp)

        self.write_control_var(self.controlVar)

    def power_to_current(self, power):
        if power <= 0:
            power = 0.0

        current = np.sqrt(power / self.htr_res)
        
        if current <= 0:
            current = 0.0
        elif current >= self.max_current:
            current = self.max_current
        
        return current

    def write_control_var(self, cv):
        """
        This method takes in a control variable value and writes it to the DAC.
        Each DAC channel can only hold 2^16 bits, so we first fill up channel A,
        then B, C, and D. Each channel is selected, then the data is loaded into the
        DAC set register address. After this is done for each channel, the "load DAC"
        GPIO pin is flipped, pushing the channel buffers into the DAC registers.

        Input:
        - cv: float
        """
        
        if self.htr_res == 0:
            self.power = 0
        else:
            self.power = cv**2 * self.htr_res
        self.tlm[f'dac_current_{self.idx+1}'] = cv
        self.tlm[f'dac_power_{self.idx+1}'] = self.power

        if self.max_current != 0:
            controlVar_t = int((cv / self.max_current) * 2**18) # Current in the range of 0 - 2**18
        else:
            controlVar_t = 0

        # 4 channels: A, B, C, D
        # We load each to max, then spill over into the next channel.
        channelList = [0, 0, 0, 0]  
        chanMax = 2**16 - 1
        for i in range(len(channelList)):
            if controlVar_t > chanMax:
                channelList[i] = chanMax
                controlVar_t = controlVar_t - chanMax
            elif controlVar_t < 0:
                channelList[i] = 0
                controlVar_t = 0
            else: 
                channelList[i] = controlVar_t
                controlVar_t = 0

            channelSelect = DSDO_BIT | 2**(5+i)
            self.dac_write_data(0x03, channelSelect)  # Select each channel
            self.dac_write_data(0x05, channelList[i])  # Write to the channel

        # Load the DAC
        self.io.dac_ldac(1)
        self.io.dac_ldac(0)
        self.io.dac_ldac(1)

    def float_to_int(self, f, sign=False):
        i = int.from_bytes(bytearray(struct.pack(">f", f)), byteorder='big', signed=sign)
        return i

    def int_to_float(self, i, sign=False):
        fTmp = struct.unpack(">f", i.to_bytes(4, byteorder='big', signed=sign))
        f= fTmp[0]
        return f

    """
    Getters and Setters for a bunch of properties.
    """

    def __get_mode(self):
        return self.__mode

    def __set_mode(self, var):
        if var == 1 or var == 2 or var == 3 or var == 0:
            self.DAC_reg_dict['MODE'][1] = var
            self.__mode = var
            if var == 0:
                self.write_control_var(0)
        else:
            raise DACError("Failed to initialize DAC. Improper Mode.")

    def __get_sns_num(self):
        return self.__sns_num

    def __set_sns_num(self, var):
        if var >= 1 and var <= 12:
            self.DAC_reg_dict['SNS_NUM'][1] = var
            self.__sns_num = var
        elif var == 0:
            self.__sns_num = var
        else:
            raise DACError("Failed to set temperature sensor. Must be 1-12.")

    def __get_hysteresis(self):
        return self.__hysteresis

    def __set_hysteresis(self, var):
        self.DAC_reg_dict['HYSTERESIS'][1] = self.float_to_int(var, sign=False)
        self.__hysteresis = var

    def __get_kp(self):
        return self.__kp

    def __set_kp(self, var):
        self.DAC_reg_dict['KP'][1] = self.float_to_int(var, sign=False)
        self.__kp = var

    def __get_ki(self):
        return self.__ki

    def __set_ki(self, var):
        self.DAC_reg_dict['KI'][1] = self.float_to_int(var, sign=False)
        self.__ki = var

    def __get_kd(self):
        return self.__kd

    def __set_kd(self, var):
        self.DAC_reg_dict['KD'][1] = self.float_to_int(var, sign=False)
        self.__kd = var

    def __get_it(self):
        return self.__it

    def __set_it(self, var):
        self.__it = var        

    def __get_setPoint(self):
        return self.__setPoint

    def __set_setPoint(self, var):
        self.DAC_reg_dict['SETPOINT'][1] = self.float_to_int(var, sign=True)
        self.__setPoint = var

    def __get_etPrev(self):
        return self.__etPrev

    def __set_etPrev(self, var):
        self.__etPrev = var

    def __get_htr_res(self):
        return self.__htr_res

    def __set_htr_res(self, var):
        if var >= 1 and var <= 2**16:
            self.DAC_reg_dict['HTR_RES'][1] = self.float_to_int(var, sign=False)
            self.__htr_res = var

            # Update max_current to reflect new heater resistance
            self.max_current = MAX_VOLTAGE / self.htr_res
            if self.max_current > MAX_CURRENT:
                self.max_current = MAX_CURRENT
        
        elif var == 0:
            self.DAC_reg_dict['HTR_RES'][1] = self.float_to_int(var, sign=False)
            self.__htr_res = var
            self.max_current = 0

        else:
            raise DACError("Failed to set heater resistance. Must be 1-65536.")

    def __get_controlVar(self):
        return self.__controlVar

    def __set_controlVar(self, var):
        self.DAC_reg_dict['CONTROL_VAR'][1] = self.float_to_int(var, sign=False)
        self.__controlVar = var

    def __get_rebootMode(self):
        return self.__rebootMode
    
    def __set_rebootMode(self, var):
        self.__rebootMode = var

    def __set_max_temp(self, var):
        self.DAC_reg_dict['MAX_TEMP'][1] = self.float_to_int(var, sign=True)
        self.__max_temp = var
    
    def __get_max_temp(self):
        return self.__max_temp

    def __set_min_temp(self, var):
        self.DAC_reg_dict['MIN_TEMP'][1] = self.float_to_int(var, sign=True)
        self.__min_temp = var
    
    def __get_min_temp(self):
        return self.__min_temp

    def __set_fixed_percent(self, var):
        self.DAC_reg_dict['FIXED_PERCENT'][1] = self.float_to_int(var, sign=False)
        self.__fixed_percent = var

    def __get_fixed_percent(self):
        return self.__fixed_percent

    mode = property(__get_mode, __set_mode)
    sns_num = property(__get_sns_num, __set_sns_num)
    hysteresis = property(__get_hysteresis, __set_hysteresis)
    kp = property(__get_kp, __set_kp)
    ki = property(__get_ki, __set_ki)
    kd = property(__get_kd, __set_kd)
    it = property(__get_it, __set_it)
    setPoint = property(__get_setPoint, __set_setPoint)
    etPrev = property(__get_etPrev, __set_etPrev)
    htr_res = property(__get_htr_res, __set_htr_res)
    controlVar = property(__get_controlVar, __set_controlVar)
    rebootMode = property(__get_rebootMode, __set_rebootMode)
    max_temp = property(__get_max_temp, __set_max_temp)
    min_temp = property(__get_min_temp, __set_min_temp)
    fixed_percent = property(__get_fixed_percent, __set_fixed_percent)

    def update_eeprom_mem(self):
        DACbyteArray = bytearray()

        for reg in self.DAC_reg_dict:
            register = self.DAC_reg_dict[reg]
            
            if reg == 'SETPOINT' or reg == 'MAX_TEMP' or reg == 'MIN_TEMP':
                regByteArray = register[1].to_bytes(register[2], byteorder='big', signed=True)
            else:
                regByteArray = register[1].to_bytes(register[2], byteorder='big', signed=False)
            
            DACbyteArray.extend(regByteArray)

        self.eeprom.DACmem[self.idx] = DACbyteArray