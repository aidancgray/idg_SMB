# BME280.py
# 5/24/2021
# Aidan Gray
# aidan.gray@idg.jhu.edu
#
# The BME280 is a combined digital humidity, pressure, and temperature
# sensor based on proven sensing principles. It uses the I2C interface.
# 
# This module allows for reading and writing to an I2C device given its
# address.

from smbus2 import SMBus, i2c_msg
import time
import logging

BUS_ID = 1
DEV_ID = 0x76

class BME280Error(IOError):
    pass

class BME280:
    def __init__(self):
        self.logger = logging.getLogger('smb')
        self.i2cBus = SMBus(BUS_ID)
        self.i2cAddr = DEV_ID
        self.ctrlHumAddr = 0xF2
        self.ctrlMeasAddr = 0xF4
        self.configAddr = 0xF5
        self.resetAddr = 0xE0  # Write 0xB6 to reset
        self.pAddr = [0xF7, 0xF8, 0xF9]
        self.tAddr = [0xFA, 0xFB, 0xFC]
        self.hAddr = [0xFD, 0xFE]
    
        self._write(self.ctrlHumAddr, b'\x01')  # Humidity: Oversampling rate x1
        self._write(self.ctrlMeasAddr, b'\x27')   # Press&Temp: Oversampling rate x1 & Normal Mode
        self._write(self.configAddr, b'\x00')  # Configure the standby mode and IIR Filter

        self.t_fine = 0  # Holds fine resolution temperature value for pressure compensation formula

        self.trimT, self.trimP, self.trimH = self._get_compensation_params()

    def _write(self, regAddr, data):
        """ 
        Input:
         - regAddr: int
         - data:    byte Array 
        """

        if len(data) > 1:
            raise BME280Error(f"Cannot write {len(data)} bytes. Max write size is 1 byte.")

        writeData = regAddr.to_bytes(1, byteorder = 'big') + data
        write = i2c_msg.write(self.i2cAddr, writeData)

        with SMBus(BUS_ID) as bus:
            bus.i2c_rdwr(write)    

        time.sleep(0.005)  
        
    def _read(self, regAddr, numBytes):
        """
        Input:
         - regAddr:     int
         - numBytes:    int

        Output:
         - returnBytes: byte array
        """

        write = i2c_msg.write(self.i2cAddr, regAddr.to_bytes(1, byteorder='big'))
        read = i2c_msg.read(self.i2cAddr, numBytes)
        
        with SMBus(BUS_ID) as bus:
            bus.i2c_rdwr(write,read)

        time.sleep(0.0005)

        returnBytes = bytearray()
        
        for value in read:
            returnBytes.append(value)

        return returnBytes
    
    def _get_compensation_params(self):
        trimT = self._read(0x88, 6)
        trimP = self._read(0x8E, 18)
        trimHa = self._read(0xA1, 1)
        trimHb = self._read(0xE1, 7)

        # Create a list of temperature trim values
        trimTlst = []
        t1a = "{0:b}".format(int.from_bytes(trimT[0:1], byteorder='little', signed=False))
        t1b = "{0:b}".format(int.from_bytes(trimT[1:2], byteorder='little', signed=True))
        t2a = "{0:b}".format(int.from_bytes(trimT[2:3], byteorder='little', signed=False))
        t2b = "{0:b}".format(int.from_bytes(trimT[3:4], byteorder='little', signed=False))
        t3a = "{0:b}".format(int.from_bytes(trimT[4:5], byteorder='little', signed=False))
        t3b = "{0:b}".format(int.from_bytes(trimT[5:6], byteorder='little', signed=False))

        t1 = int.from_bytes(trimT[0:2], byteorder='little', signed=False)
        t2 = int.from_bytes(trimT[2:4], byteorder='little', signed=True)
        t3 = int.from_bytes(trimT[4:6], byteorder='little', signed=True)
        
        trimTlst.append(t1)
        trimTlst.append(t2)
        trimTlst.append(t3)
        
        # Create a list of pressure trim values
        trimPlst = []

        p1 = int.from_bytes(trimP[0:2], byteorder='little', signed=False)
        p2 = int.from_bytes(trimP[2:4], byteorder='little', signed=True)
        p3 = int.from_bytes(trimP[4:6], byteorder='little', signed=True)
        p4 = int.from_bytes(trimP[6:8], byteorder='little', signed=True)
        p5 = int.from_bytes(trimP[8:10], byteorder='little', signed=True)
        p6 = int.from_bytes(trimP[10:12], byteorder='little', signed=True)
        p7 = int.from_bytes(trimP[12:14], byteorder='little', signed=True)
        p8 = int.from_bytes(trimP[14:16], byteorder='little', signed=True)
        p9 = int.from_bytes(trimP[16:18], byteorder='little', signed=True)

        trimPlst.append(p1)
        trimPlst.append(p2)
        trimPlst.append(p3)
        trimPlst.append(p4)
        trimPlst.append(p5)
        trimPlst.append(p6)
        trimPlst.append(p7)
        trimPlst.append(p8)
        trimPlst.append(p9)

        # Create a list of humidity trim values
        trimHlst = []
        tmpH1 = int.from_bytes(trimHa[0:1], byteorder='little', signed=False)
        trimHlst.append(tmpH1)

        tmpH2 = int.from_bytes(trimHb[0:2], byteorder='little', signed=True)
        trimHlst.append(tmpH2)

        tmpH3 = int.from_bytes(trimHb[2:3], byteorder='little', signed=False)
        trimHlst.append(tmpH3)

        tmpH4a = int.from_bytes(trimHb[3:4], byteorder='little', signed=True)
        tmpH45 = int.from_bytes(trimHb[4:5], byteorder='little', signed=False)
        tmpH4b = tmpH45 & 15  # get only 4 lsb
        tmpH4a = tmpH4a << 4  # shift right by 4 bits
        tmpH4 = tmpH4a + tmpH4b 
        trimHlst.append(tmpH4)

        tmpH5a = tmpH45 & 240  # get only 4 msb
        tmpH5b = int.from_bytes(trimHb[5:6], byteorder='little', signed=True)
        tmpH5b = tmpH5b << 4  # shift right by 4 bits
        tmpH5 = tmpH5a + tmpH5b
        trimHlst.append(tmpH5)

        tmpH6 = int.from_bytes(trimHb[6:7], byteorder='little', signed=True)
        trimHlst.append(tmpH6)

        return trimTlst, trimPlst, trimHlst

    def _compensate_T(self, adc_T):
        dig_T1 = self.trimT[0]
        dig_T2 = self.trimT[1]
        dig_T3 = self.trimT[2]

        var1 = (float(adc_T)/16384.0 - float(dig_T1)/1024.0) * float(dig_T2)
        var2 = ((float(adc_T)/131072.0 - float(dig_T1)/8192.0) * (float(adc_T)/131072.0 - float(dig_T1)/8192.0)) * float(dig_T3)
        self.t_fine = float(var1 + var2)
        cT = self.t_fine / 5120.0
        return cT

    def _compensate_P(self, adc_P):
        dig_P1 = self.trimP[0]
        dig_P2 = self.trimP[1]
        dig_P3 = self.trimP[2]
        dig_P4 = self.trimP[3]
        dig_P5 = self.trimP[4]
        dig_P6 = self.trimP[5]
        dig_P7 = self.trimP[6]
        dig_P8 = self.trimP[7]
        dig_P9 = self.trimP[8]

        var1 = (float(self.t_fine)/2.0) - 64000.0
        var2 = var1 * var1 * (float(dig_P6)) / 32768.0
        var2 = var2 + var1 * (float(dig_P5)) * 2.0
        var2 = (var2 / 4.0) + (float(dig_P4)) * 65536.0
        var1 = ((float(dig_P3)) * var1 * var1 / 524288.0 + (float(dig_P2)) * var1) / 524288.0 
        var1 = (1.0 + var1 / 32768.0) * (float(dig_P1))
        
        if var1 == 0.0:
            return -1
        
        cP = 1048576.0 - float(adc_P)
        cP = (cP - (var2 / 4096.0)) * 6250.0 / var1
        var1 = (float(dig_P9)) * cP * cP / 2147483648.0
        var2 = cP * (float(dig_P8)) / 32768.0
        cP = cP + (var1 + var2 + (float(dig_P7))) / 16.0
        
        return cP

    def _compensate_H(self, uH):
        dig_H1 = self.trimH[0]
        dig_H2 = self.trimH[1]
        dig_H3 = self.trimH[2]
        dig_H4 = self.trimH[3]
        dig_H5 = self.trimH[4]
        dig_H6 = self.trimH[5]

        var_H = (float(self.t_fine) - 76800.0)
        var_H = (uH - (float(dig_H4) * 64.0 + float(dig_H5) / 16384.0 * var_H)) * (float(dig_H2) / 65536.0 * (1.0 + float(dig_H6) / 67108864.0 * var_H * (1.0 + float(dig_H3) / 67108864.0 * var_H)))
        var_H = var_H * (1.0 - float(dig_H1) * var_H / 524288.0)

        if var_H > 100.0:
            var_H = 100.0
        elif var_H < 0.0:
            var_H = 0.0
        
        cH = var_H
        return cH

    def _get_raw_data(self):
        uPtmp = self._read(self.pAddr[0], len(self.pAddr))
        uTtmp = self._read(self.tAddr[0], len(self.tAddr))
        uHtmp = self._read(self.hAddr[0], len(self.hAddr))

        # convert from bytearray to int
        uPtmp = int.from_bytes(uPtmp, byteorder='big', signed=False)
        uP = int(uPtmp / 2**4)  # bitshift right by 4

        uTtmp = int.from_bytes(uTtmp, byteorder='big', signed=False)
        uT = int(uTtmp / 2**4)  # bitshift right by 4

        uH = int.from_bytes(uHtmp, byteorder='big', signed=False)

        return uP, uT, uH
    
    def _get_data(self):
        uP, uT, uH = self._get_raw_data()

        # T must be compensated first to get t_fine for P compensation
        cT = self._compensate_T(uT)
        cP = self._compensate_P(uP)
        cH = self._compensate_H(uH)

        return cP, cT, cH

    def get_temperature(self):
        cP, cT, cH = self._get_data()
        return float("{:.2f}".format(cT))

    def get_pressure(self):
        cP, cT, cH = self._get_data()
        return float("{:.2f}".format(cP))

    def get_humidity(self):
        cP, cT, cH = self._get_data()
        return float("{:.2f}".format(cH))