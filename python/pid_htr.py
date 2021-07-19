# pid_htr.py
# 6/28/2021
# Aidan Gray
# aidan.gray@idg.jhu.edu
#
# PID Heater Class.

import RPi.GPIO as GPIO

class PIDError(ValueError):
    pass

class pid_htr():
    def __init__(self, idx, io, eeprom, dacList):
        self.idx = idx
        self.io = io
        self.eeprom = eeprom
        self.dacList = dacList
        self.dac = self.dacList[idx]

        self.pid_htr_reg_dict = {
                                'SNS_NUM':  [int.from_bytes(self.eeprom.PIDmem[self.idx][0:2], byteorder='big'), 2], 
                                'SETPOINT': [int.from_bytes(self.eeprom.PIDmem[self.idx][2:4], byteorder='big'), 2],
                                'KP':       [int.from_bytes(self.eeprom.PIDmem[self.idx][4:6], byteorder='big'), 2],
                                'KI':       [int.from_bytes(self.eeprom.PIDmem[self.idx][6:8], byteorder='big'), 2],
                                'KD':       [int.from_bytes(self.eeprom.PIDmem[self.idx][8:10], byteorder='big'), 2],
                                'IT':       [int.from_bytes(self.eeprom.PIDmem[self.idx][10:12], byteorder='big'), 2],
                                'ETPREV':   [int.from_bytes(self.eeprom.PIDmem[self.idx][12:14], byteorder='big'), 2]
                                }

        self.sns_num = self.pid_htr_reg_dict['SNS_NUM'][0]
        self.setPoint = self.pid_htr_reg_dict['SETPOINT'][0]
        self.kp = self.pid_htr_reg_dict['KP'][0]
        self.ki = self.pid_htr_reg_dict['KI'][0]
        self.kd = self.pid_htr_reg_dict['KD'][0]
        self.it = self.pid_htr_reg_dict['IT'][0]
        self.etPrev = self.pid_htr_reg_dict['ETPREV'][0]

    def set_dac(self, dacNum):
        if dacNum >= 1 and dacNum <= 4:
            self.dac = self.dacList[dacNum-1]
        else:
            raise PIDError("Invalid DAC selected. Must be 1-4.")

    def set_sns(self, snsNum):
        if snsNum >= 1 and snsNum <= 12:
            self.sns_num = snsNum
        else:
            raise PIDError("Invalid sensor selected. Must be 1-12.")
