# ADS1015.py
# 5/24/2021
# Aidan Gray
# aidan.gray@idg.jhu.edu
#
# The ADS1015 is a precision, low-power, 12-bit, I2C compatible
# analog-to-digital converter.

from smbus2 import SMBus, i2c_msg
import time
import logging

BUS_ID = 1
DEV_ID = 0x48

class ADS1015Error(IOError):
    pass

class ADS1015:
    def __init__(self, eeprom):
        self.eeprom = eeprom

        self.ADS1015_reg_dict = {
                                'confAIN_0':    [0x01, int.from_bytes(self.eeprom.ADS1015mem[0:2], byteorder='big'), 2], 
                                'confAIN_3':    [0x01, int.from_bytes(self.eeprom.ADS1015mem[2:4], byteorder='big'), 2]
                                }

        self.logger = logging.getLogger('smb')
        self.i2cBus = SMBus(BUS_ID)
        self.i2cAddr = DEV_ID
        self.convAddr = 0x00
        self.confAddr = self.ADS1015_reg_dict['confAIN_0'][0]
        self.confAIN_0 = self.ADS1015_reg_dict['confAIN_0'][1]  # AIN0 & AIN1 = 000
        self.confAIN_3 = self.ADS1015_reg_dict['confAIN_3'][1]  # AIN2 & AIN3 = 011
        self.conversionGain = 0.02647     
        self.conversionOffset = 39.915

    def _write(self, regAddr, data):
        """ 
        Input:
         - regAddr: int
         - data:    byte Array 
        """

        if len(data) > 2:
            raise ADS1015Error(f"Cannot write {len(data)} bytes. Max write size is 2 bytes.")

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
    
    # Perform a read of the configuration register
    def _config_read(self):
        confData = self._read(self.confAddr, 2)
        confData = int.from_bytes(confData, byteorder='big')
        return confData

    # Perform a write of the configuration register
    def _config_write(self, data):
        self._write(self.confAddr, data)

    # Perform a read of the conversion register
    def conversion_read(self):
        convData = self._read(self.convAddr, 2)
        convData = int.from_bytes(convData, byteorder='big')
        if convData == 0:
            adjData = 0
        else:
            adjData = (convData * self.conversionGain) + self.conversionOffset
        return adjData

    # Check if a conversion is occurring
    def conversion_status(self):
        status = self._config_read()
        statusBit = status >> 15
        return statusBit

    # Return the last conversion input multiplexer config (0 or 3)
    def last_convert(self):
        status = self._config_read()
        statusBit = (status >> 12) & 7
        return statusBit

    # Begin a conversion on the 000 multiplexer config
    def convert_0(self):
        self._config_write(self.confAIN_0.to_bytes(2, byteorder='big'))

    # Begin a conversion on the 011 multiplexer config
    def convert_3(self):
        self._config_write(self.confAIN_3.to_bytes(2, byteorder='big'))

    def update_eeprom_mem(self):
        ADSbyteArray = bytearray()

        for reg in self.ADS1015_reg_dict:
            register = self.ADS1015_reg_dict[reg]
            regByteArray = register[1].to_bytes(register[2], byteorder='big')
            ADSbyteArray.extend(regByteArray)

        self.eeprom.ADS1015mem = ADSbyteArray
        