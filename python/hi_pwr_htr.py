# hi_pwr_htr.py
# 5/24/2021
# Aidan Gray
# aidan.gray@idg.jhu.edu
#
# High Power Heater class (Bang-Bang). 
# Simple functionality: on/off/status

import RPi.GPIO as GPIO

class hi_pwr_htr():
    def __init__(self, idx, io, eeprom):
        self.idx = idx
        self.io = io
        self.eeprom = eeprom
        self.hi_pwr_en_pin = 0

        self.hi_pwr_htr_reg_dict = {
                                    'SNS_NUM':  [int.from_bytes(self.eeprom.HIPWRmem[self.idx][0:2], byteorder='big'), 2],
                                    'SETPOINT': [int.from_bytes(self.eeprom.HIPWRmem[self.idx][2:4], byteorder='big'), 2] 
                                    }

        self.sns_num = self.hi_pwr_htr_reg_dict['SNS_NUM'][0]
        self.setPoint = self.hi_pwr_htr_reg_dict['SETPOINT'][0]

        if self.idx == 0:
            self.hi_pwr_en_pin = self.io.pin_map['HI_PWR_EN1']
        elif self.idx == 1:
            self.hi_pwr_en_pin = self.io.pin_map['HI_PWR_EN2']
        
        GPIO.setup(self.hi_pwr_en_pin, GPIO.OUT)
        GPIO.output(self.hi_pwr_en_pin, 0)

    def power_on(self):
        GPIO.output(self.hi_pwr_en_pin, 1)

    def power_off(self):
        GPIO.output(self.hi_pwr_en_pin, 0)

    def status(self):
        status = GPIO.input(self.hi_pwr_en_pin)
        return status

    def update_eeprom_mem(self):
        HIPWRbyteArray = bytearray()

        for reg in self.hi_pwr_htr_reg_dict:
            register = self.hi_pwr_htr_reg_dict[reg]
            regByteArray = register[0].to_bytes(register[1], byteorder='big')
            HIPWRbyteArray.extend(regByteArray)

        self.eeprom.HIPWRmem[self.idx] = HIPWRbyteArray
