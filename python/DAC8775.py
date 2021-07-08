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
        self.idx = idx  # DAC address
        self.io = io    # GPIO
        self.eeprom = eeprom
        self.tlm = tlm
        self.max_current = None
        self.power = None

        self.DAC_reg_dict = {
                            'RESET':        [0x01, int.from_bytes(self.eeprom.DACmem[self.idx][0:2], byteorder='big'), 2],
                            'RESET_CONFIG': [0x02, int.from_bytes(self.eeprom.DACmem[self.idx][2:4], byteorder='big'), 2],
                            'SEL_DAC':      [0x03, int.from_bytes(self.eeprom.DACmem[self.idx][4:6], byteorder='big'), 2], 
                            'CONF_DAC':     [0x04, int.from_bytes(self.eeprom.DACmem[self.idx][6:8], byteorder='big'), 2],
                            'DAC_DATA':     [0x05, int.from_bytes(self.eeprom.DACmem[self.idx][8:10], byteorder='big'), 2],
                            'SEL_BB':       [0x06, int.from_bytes(self.eeprom.DACmem[self.idx][10:12], byteorder='big'), 2],
                            'CONF_BB':      [0x07, int.from_bytes(self.eeprom.DACmem[self.idx][12:14], byteorder='big'), 2],
                            'CHAN_CAL':     [0x08, int.from_bytes(self.eeprom.DACmem[self.idx][14:16], byteorder='big'), 2],
                            'CHAN_GAIN':    [0x09, int.from_bytes(self.eeprom.DACmem[self.idx][16:18], byteorder='big'), 2],
                            'CHAN_OFFSET':  [0x0A, int.from_bytes(self.eeprom.DACmem[self.idx][18:20], byteorder='big'), 2],
                            'STATUS':       [0x0B, int.from_bytes(self.eeprom.DACmem[self.idx][20:22], byteorder='big'), 2],
                            'STATUS_MASK':  [0x0C, int.from_bytes(self.eeprom.DACmem[self.idx][22:24], byteorder='big'), 2],
                            'ALARM_ACT':    [0x0D, int.from_bytes(self.eeprom.DACmem[self.idx][24:26], byteorder='big'), 2],
                            'ALARM_CODE':   [0x0E, int.from_bytes(self.eeprom.DACmem[self.idx][26:28], byteorder='big'), 2],
                            'WATCHDOG':     [0x10, int.from_bytes(self.eeprom.DACmem[self.idx][28:30], byteorder='big'), 2],
                            'ID':           [0x11, int.from_bytes(self.eeprom.DACmem[self.idx][30:32], byteorder='big'), 2],
                            'MODE':         [0x00, int.from_bytes(self.eeprom.DACmem[self.idx][32:34], byteorder='big'), 2],
                            'SNS_NUM':      [0x00, int.from_bytes(self.eeprom.DACmem[self.idx][34:36], byteorder='big'), 2],
                            'SETPOINT':     [0x00, int.from_bytes(self.eeprom.DACmem[self.idx][36:40], byteorder='big'), 4],
                            'KP':           [0x00, int.from_bytes(self.eeprom.DACmem[self.idx][40:44], byteorder='big'), 4],
                            'KI':           [0x00, int.from_bytes(self.eeprom.DACmem[self.idx][44:48], byteorder='big'), 4],
                            'KD':           [0x00, int.from_bytes(self.eeprom.DACmem[self.idx][48:52], byteorder='big'), 4],
                            'HTR_RES':      [0x00, int.from_bytes(self.eeprom.DACmem[self.idx][52:56], byteorder='big'), 4],
                            'HYSTERESIS':   [0x00, int.from_bytes(self.eeprom.DACmem[self.idx][60:64], byteorder='big'), 4]
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
        self.__set_mode(self.DAC_reg_dict['MODE'][1])                                   # 0=DISABLED, 1=Fixed%, 2=PID, or 3=HIPWR
        self.__set_sns_num(self.DAC_reg_dict['SNS_NUM'][1])                             # Sensor (AD7124) number (1-12)
        self.__set_kp(self.int_to_float(self.DAC_reg_dict['KP'][1]))                    # proportional term
        self.__set_ki(self.int_to_float(self.DAC_reg_dict['KI'][1]))                    # integral term
        self.__set_kd(self.int_to_float(self.DAC_reg_dict['KD'][1]))                    # derivative term
        self.__set_it(0)                                                                # total integral term
        self.__set_etPrev(0)                                                            # the previous error value
        self.__set_setPoint(self.int_to_float(self.DAC_reg_dict['SETPOINT'][1]))        # setpoint
        self.__set_htr_res(self.int_to_float(self.DAC_reg_dict['HTR_RES'][1]))          # Heater resistance
        self.__set_hysteresis(self.int_to_float(self.DAC_reg_dict['HYSTERESIS'][1]))    # Allowable range for HIPWR
        self.__set_controlVar(0)                                                        # control variable
        self.__set_rebootMode(False)                                                    # False: Reset PID values on reboot

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
        elif self.__mode == 3:
            self.hipwr_update(temp, units)
        elif self.__mode == 1:
            self.fp_update(temp, units)
        else:
            raise DACError("Invalid mode set. Cannot update DAC.")

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
        elif units == 1:
            setPointK = self.setPoint + 273.15
        elif units == 2:
            setPointK = ((self.setPoint - 32) * (5 / 9)) + 273.15
        else:
            raise AD7124Error("Invalid units. Cannot update DAC.")

        et = setPointK - pv # calculate e(t)
        d_et = ( et - self.etPrev ) / dt  # calculate de(t)/dt
        self.it += ( et * dt )  # add to the integral term
        self.etPrev = et  # set the previous error term (for next time)

        # calculate the new control variable
        p_term = self.kp * et
        i_term = self.ki * self.it
        d_term = self.kd * d_et

        # Maximum current is set by the maximum voltage and the heater's resistance
        self.max_current = MAX_VOLTAGE / self.htr_res
        if self.max_current > MAX_CURRENT:
            self.max_current = MAX_CURRENT

        max_i_term = self.max_current**2 * self.htr_res * 1000

        if i_term > max_i_term:
            i_term = max_i_term
        elif i_term < 0:
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

        controlVar_t = int((cv / self.max_current) * 2**18) # Current in the range of 0 - 2**18
        #print(f'current={cv}, max_cur={self.max_current}, cv={controlVar_t}')

        # 4 channels: A, B, C, D
        # We load each to max, then spill over into the next channel.
        channelList = [0, 0, 0, 0]  
        for i in range(len(channelList)):
            if controlVar_t >= 2**16:
                channelList[i] = 2**16 - 1
                controlVar_t = controlVar_t - 2**16 - 1
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

    def float_to_int(self, f):
        i = int.from_bytes(bytearray(struct.pack(">f", f)), byteorder='big')
        return i

    def int_to_float(self, i):
        fTmp = struct.unpack(">f", i.to_bytes(4, byteorder='big'))
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
        else:
            raise DACError("Failed to initialize DAC. Improper Mode.")

    def __get_sns_num(self):
        return self.__sns_num

    def __set_sns_num(self, var):
        if var >= 1 and var <= 12:
            self.DAC_reg_dict['SNS_NUM'][1] = var
            self.__sns_num = var
        elif var == 0:
            #self.logger.warning('No sensor set')
            self.__sns_num = var
        else:
            raise DACError("Failed to set temperature sensor. Must be 1-12.")

    def __get_hysteresis(self):
        return self.__hysteresis

    def __set_hysteresis(self, var):
        self.DAC_reg_dict['HYSTERESIS'][1] = self.float_to_int(var)
        self.__hysteresis = var

    def __get_kp(self):
        return self.__kp

    def __set_kp(self, var):
        self.DAC_reg_dict['KP'][1] = self.float_to_int(var)
        self.__kp = var

    def __get_ki(self):
        return self.__ki

    def __set_ki(self, var):
        self.DAC_reg_dict['KI'][1] = self.float_to_int(var)
        self.__ki = var

    def __get_kd(self):
        return self.__kd

    def __set_kd(self, var):
        self.DAC_reg_dict['KD'][1] = self.float_to_int(var)
        self.__kd = var

    def __get_it(self):
        return self.__it

    def __set_it(self, var):
        self.__it = var        

    def __get_setPoint(self):
        return self.__setPoint

    def __set_setPoint(self, var):
        # if var < 0:
        #     raise ValueError("Invalid setpoint.")
        self.DAC_reg_dict['SETPOINT'][1] = self.float_to_int(var)
        self.__setPoint = var

    def __get_etPrev(self):
        return self.__etPrev

    def __set_etPrev(self, var):
        self.__etPrev = var

    def __get_htr_res(self):
        return self.__htr_res

    def __set_htr_res(self, var):
        if var >= 1 and var <= 2**16:
            self.DAC_reg_dict['HTR_RES'][1] = self.float_to_int(var)
            self.__htr_res = var
        elif var == 0:
            #self.logger.warning('No heater resistance set')
            self.__htr_res = var
        else:
            raise DACError("Failed to set heater resistance. Must be 1-65536.")

    def __get_controlVar(self):
        return self.__controlVar

    def __set_controlVar(self, var):
        self.__controlVar = var

    def __get_rebootMode(self):
        return self.__rebootMode
    
    def __set_rebootMode(self, var):
        self.__rebootMode = var

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

    def update_eeprom_mem(self):
        DACbyteArray = bytearray()

        for reg in self.DAC_reg_dict:
            register = self.DAC_reg_dict[reg]
            regByteArray = register[1].to_bytes(register[2], byteorder='big')
            DACbyteArray.extend(regByteArray)

        self.eeprom.DACmem[self.idx] = DACbyteArray