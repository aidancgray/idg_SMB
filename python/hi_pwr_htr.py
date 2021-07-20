# hi_pwr_htr.py
# 5/24/2021
# Aidan Gray
# aidan.gray@idg.jhu.edu
#
# High Power Heater class (Bang-Bang). 
# Simple functionality: on/off/status

import RPi.GPIO as GPIO
import struct

class HIPWRError(ValueError):
    pass

class hi_pwr_htr():
    def __init__(self, idx, io, eeprom, tlm):
        self.idx = idx
        self.io = io
        self.eeprom = eeprom
        self.tlm = tlm
        self.hi_pwr_en_pin = 0

        self.hi_pwr_htr_reg_dict = {
                                    'MODE':         [int.from_bytes(self.eeprom.HIPWRmem[self.idx][0:2], byteorder='big', signed=False), 2],
                                    'SNS_NUM':      [int.from_bytes(self.eeprom.HIPWRmem[self.idx][2:4], byteorder='big', signed=False), 2],
                                    'SETPOINT':     [int.from_bytes(self.eeprom.HIPWRmem[self.idx][4:8], byteorder='big', signed=True), 4],
                                    'HYSTERESIS':   [int.from_bytes(self.eeprom.HIPWRmem[self.idx][8:12], byteorder='big', signed=False), 4],
                                    'MAX_TEMP':     [int.from_bytes(self.eeprom.HIPWRmem[self.idx][12:16], byteorder='big', signed=True), 4],
                                    'MIN_TEMP':     [int.from_bytes(self.eeprom.HIPWRmem[self.idx][16:20], byteorder='big', signed=True), 4]
                                    }

        self.mode = self.hi_pwr_htr_reg_dict['MODE'][0]         # 0=Disabled, 1=Enabled, 2=HYSTERESIS
        self.sns_num = self.hi_pwr_htr_reg_dict['SNS_NUM'][0]
        self.setPoint = self.hi_pwr_htr_reg_dict['SETPOINT'][0]
        self.hysteresis = self.hi_pwr_htr_reg_dict['HYSTERESIS'][0]
        self.max_temp = self.hi_pwr_htr_reg_dict['MAX_TEMP'][0]
        self.min_temp = self.hi_pwr_htr_reg_dict['MIN_TEMP'][0]

        if self.idx == 0:
            self.hi_pwr_en_pin = self.io.pin_map['HI_PWR_EN1']
        elif self.idx == 1:
            self.hi_pwr_en_pin = self.io.pin_map['HI_PWR_EN2']
        
        GPIO.setup(self.hi_pwr_en_pin, GPIO.OUT)
        GPIO.output(self.hi_pwr_en_pin, 0)

    def float_to_int(self, f, sign=False):
        i = int.from_bytes(bytearray(struct.pack(">f", f)), byteorder='big', signed=sign)
        return i

    def int_to_float(self, i, sign=False):
        fTmp = struct.unpack(">f", i.to_bytes(4, byteorder='big', signed=sign))
        f= fTmp[0]
        return f

    def set_mode(self, mode):
        if mode == 0 or mode == 1 or mode == 2:
            self.mode = mode
        else:
            raise HIPWRError("Invalid Mode. Must be 0=Disabled, 1=USER_SET, 2=HYSTERESIS.")

    def power_on(self):
        GPIO.output(self.hi_pwr_en_pin, 1)

    def power_off(self):
        GPIO.output(self.hi_pwr_en_pin, 0)

    def status(self):
        status = GPIO.input(self.hi_pwr_en_pin)
        return status

    def update_htr(self, temp, units):
        # Convert to Kelvin (0=K, 1=C, 2=F)
        # if units == 0:
        #     temp = temp
        # elif units == 1:
        #     temp += 273.15
        # elif units == 2:
        #     temp = ((temp - 32) * (5 / 9)) + 273.15
        # else:
        #     raise HIPWRError("Invalid units. Cannot update HI_PWR_HTR.")

        hystUpper = self.setPoint + self.hysteresis
        hystLower = self.setPoint - self.hysteresis
        
        if temp >= hystUpper:
            self.power_off()
        elif temp <= hystLower:
            self.power_on()

    def update_eeprom_mem(self):
        HIPWRbyteArray = bytearray()

        for reg in self.hi_pwr_htr_reg_dict:
            register = self.hi_pwr_htr_reg_dict[reg]
            regByteArray = register[0].to_bytes(register[1], byteorder='big')
            HIPWRbyteArray.extend(regByteArray)

        self.eeprom.HIPWRmem[self.idx] = HIPWRbyteArray
