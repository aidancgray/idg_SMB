import atexit
import logging
import signal

import RPi.GPIO as GPIO

import Gbl

def sigCleanup(signum, frame):
    logging.warn("caught signal %s", signum)
    raise SystemExit()


def cleanup():
    try:
        GPIO.cleanup()
    except RuntimeWarning:
        return
    
    #logging.warn('reset GPIO configuration on exit.')


class io():

    def __init__(self, ):
        """
        @dictionary GPIO Pin Numbers
        @Maps DAC singals to GPIO PINS.
        """
        self.pin_map = {
            "SDA_0": 2,
            "SCL_0": 3,
            "nDAC_ALARM": 4,
            "HI_PWR_EN1": 5,
            "HI_PWR_EN2": 6,
            "nADC_CS1": 7,
            "nADC_CS0": 24,
            "SPI0_MISO": 9,
            "SPI0_MOSI": 10,
            "SPI0_SCLK": 11,
            "nDAC_RESET": 12,
            "nLDAC": 13,
            "nADC_BANK1_SEL": 16,
            "nDAC_SSA1": 17,        # DAC Slave Select Address 1
            "nDAC_SSA0": 18,        # DAC Slave Select Address 0
            "SPI1_MISO": 19,
            "SPI1_MOSI": 20,
            "SPI1_SCLK": 21,
            "nADC_BANK3_SEL": 22,
            "DAC_CLR": 23,
            "GPIO24": 24,
            "nDAC_MSS": 25,         # DAC Master Slave Select
            "nADC_SYNC": 26,
            "nADC_BANK2_SEL": 27,
        }

        atexit.register(cleanup)
        signal.signal(signal.SIGTERM, sigCleanup)
        
        """ SET GPIO numbering mode to use GPIO designation, NOT pin numbers """
        GPIO.setmode(GPIO.BCM)

        # Set HI_PWR_EN1 to output.
        pin = self.pin_map['HI_PWR_EN1']
        GPIO.setup(pin, GPIO.OUT)

        # Set HI_PWR_EN2 to output.
        pin = self.pin_map['HI_PWR_EN2']
        GPIO.setup(pin, GPIO.OUT)

        # Set /ADC_SC0 to output.
        pin = self.pin_map['nADC_CS0']
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, 1)

        # Set /ADC SC1 to output.
        pin = self.pin_map['nADC_CS1']
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, 1)

        # Set nADC_BANK1_SEL to output
        pin = self.pin_map['nADC_BANK1_SEL']
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, 1)  # disable

        # Set nADC_BANK2_SEL to output
        pin = self.pin_map['nADC_BANK2_SEL']
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, 1)  # disable

        # Set nADC_BANK3_SEL to output
        pin = self.pin_map['nADC_BANK3_SEL']
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, 1)  # disable

        # Set SPI1_SCLK to output.
        pin = self.pin_map['SPI1_SCLK']
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, 1)  # idle high

        # Set SPI1_MOSI to output.
        pin = self.pin_map['SPI1_MOSI']
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, 0)  # normally low

        # Set SPI1_MISO to input.
        pin = self.pin_map['SPI1_MISO']
        # GPIO.setup(pin, GPIO.IN)
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        # Set /DAC_MSS to output.
        pin = self.pin_map['nDAC_MSS']
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, 1)  # enable master slave select

        # Set /DAC_SSA0 to output.
        pin = self.pin_map['nDAC_SSA0']
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, 0)

        # Set /DAC_SSA1 to output.
        pin = self.pin_map['nDAC_SSA1']
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, 0)

        # Set ADC /SYNC to output.
        pin = self.pin_map['nADC_SYNC']
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, 0)

        # Set DAC /RESET to output.
        pin = self.pin_map['nDAC_RESET']
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, 1)  # put DAC in run mode

        # Set DAC /LDAC to output and low level for Asynchronous Mode
        pin = self.pin_map['nLDAC']
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, 1)

        # Set DAC CLR to output.
        pin = self.pin_map['DAC_CLR']
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, 0)

        # Set DAC /Alarm to input.
        pin = self.pin_map['nDAC_ALARM']
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def dac_reset(self, state):
        pin = self.pin_map['nDAC_RESET']
        GPIO.output(pin, state)

    def dac_ldac(self, state):
        pin = self.pin_map['nLDAC']
        GPIO.output(pin, state)

    def dac_clr(self, state):
        pin = self.pin_map['DAC_CLR']
        GPIO.output(pin, state)

    def dac_mss_sel(self, state):
        pin = self.pin_map['nDAC_MSS']
        GPIO.output(pin, state)

    def dac_sel(self, dac_id):
        ssa0 = self.pin_map['nDAC_SSA0']
        ssa1 = self.pin_map['nDAC_SSA1']

        self.dac_bank_sel(False)

        if dac_id == 0:
            GPIO.output(ssa1, 0)
            GPIO.output(ssa0, 0)
        elif dac_id == 1:
            GPIO.output(ssa1, 0)
            GPIO.output(ssa0, 1)
        elif dac_id == 2:
            GPIO.output(ssa1, 1)
            GPIO.output(ssa0, 0)
        elif dac_id == 3:
            GPIO.output(ssa1, 1)
            GPIO.output(ssa0, 1)
        else:
            GPIO.output(ssa1, 1)
            GPIO.output(ssa0, 1)

    # There are 12 ADCs divided into three banks of 4. To enable an
    # ADC select the bank using the bank_sel lines and then the chip
    # using the chip_sel lines.

    def adc_sel(self, adc_id):
        cs0 = self.pin_map['nADC_CS0']
        cs1 = self.pin_map['nADC_CS1']
        bs1 = self.pin_map['nADC_BANK1_SEL']
        bs2 = self.pin_map['nADC_BANK2_SEL']
        bs3 = self.pin_map['nADC_BANK3_SEL']
        adc_mux_id = adc_id % 4

        # deselect all chips first
        # GPIO.output(bs1, 1)
        # GPIO.output(bs2, 1)
        # GPIO.output(bs3, 1)

        if adc_id in range(0, 4):
            GPIO.output(bs1, 0)
            GPIO.output(bs2, 1)
            GPIO.output(bs3, 1)

        elif adc_id in range(4, 8):
            GPIO.output(bs1, 1)
            GPIO.output(bs2, 0)
            GPIO.output(bs3, 1)

        elif adc_id in range(8, 12):
            GPIO.output(bs1, 1)
            GPIO.output(bs2, 1)
            GPIO.output(bs3, 0)
        else:
            GPIO.output(bs1, 1)
            GPIO.output(bs2, 1)
            GPIO.output(bs3, 1)

        # deselect chip first
        if adc_mux_id >= 0 and adc_mux_id < 3:
            GPIO.output(cs1, 1)
            GPIO.output(cs0, 1)
        else:
            GPIO.output(cs1, 0)
            GPIO.output(cs0, 0)

        # now select the one you want
        if adc_mux_id == 0:
            GPIO.output(cs1, 0)
            GPIO.output(cs0, 0)

        elif adc_mux_id == 1:
            GPIO.output(cs1, 0)
            GPIO.output(cs0, 1)

        elif adc_mux_id == 2:
            GPIO.output(cs1, 1)
            GPIO.output(cs0, 0)

        elif adc_mux_id == 3:
            GPIO.output(cs1, 1)
            GPIO.output(cs0, 1)

        else:
            GPIO.output(cs1, 1)
            GPIO.output(cs0, 1)
