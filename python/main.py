#!/usr/local/bin/python3.8

from EEPROM import EEPROM
import time

def main():
    eeprom = EEPROM(0x50)

    eeprom.write(0x00,0x00,[0xA0])
    
    read1 = eeprom.readout()
    print(read1)

if __name__ == "__main__":
    main()