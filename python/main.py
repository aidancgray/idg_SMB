#!/usr/local/bin/python3.8

from EEPROM import EEPROM
import time

def main():
    eeprom = EEPROM(0x50)

    read1 = eeprom.read(0, 0, 8)
    eeprom.write(0, 0, [0x00, 0x00, 0x00])
    read2 = eeprom.read(0, 0, 8)

    print(read1)
    print(read2)

if __name__ == "__main__":
    main()