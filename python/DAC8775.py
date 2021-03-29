import RPi.GPIO as GPIO
import time
import logging

class DACError(ValueError):
    pass

class DAC():

    def __init__(self, idx, io, mode):
        if idx < 0 or idx > 3:
            raise DACError("Failed to initialize DAC. Index out of range.")

        self.idx = idx  # DAC address
        self.io = io  # GPIO
        self.logger = logging.getLogger('DAC-'+str(idx))
        self.logger.setLevel(logging.INFO)

        # GPIO Pins
        self.mosi = self.io.pin_map['SPI1_MOSI']
        self.miso = self.io.pin_map['SPI1_MISO']
        self.sclk = self.io.pin_map['SPI1_SCLK']
        self.ssa0 = self.io.pin_map['nDAC_SSA0']
        self.ssa1 = self.io.pin_map['nDAC_SSA1']
        self.mss = self.io.pin_map['nDAC_MSS']

        # Heater Parameters
        self.__set_mode(mode)  # PID, BB, or FIXED
        self.__set_hysteresis(0)  # Allowable range for BB
        self.__set_kp(0)  # proportional term
        self.__set_ki(0)  # integral term
        self.__set_kd(0)  # derivative term
        self.__set_it(0)  # total integral term
        self.__set_setPoint(0)  # setpoint
        self.__set_etPrev(0) # the previous error value
        self.__set_controlVar(0)  # control variable
        self.__set_rebootMode(False)  # False: Reset PID values on reboot

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
            GPIO.output(self.ssa0, 0)  # set SSA0 to DAC1
        elif self.idx == 3:
            GPIO.output(self.ssa1, 1)  # set SSA1
            GPIO.output(self.ssa0, 1)  # set SSA0 to DAC1
        else:
            GPIO.output(self.ssa1, 1)  # set SSA1
            GPIO.output(self.ssa0, 1)  # set SSA0 to DAC1

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
        returnData = int.from_bytes(returnBytes, byteorder = 'big')

        return returnData

    def pid_update(self, pv, dt=1):
        """
        Update the PID values. The default functionality assumes PID updates
        are occurring at 1Hz. If this frequency is changed, you must pass the 
        delta-time into the pid_update() function after the process variable,
        which is the measured temperature.

        Input:
        - pv: float
        - dt: change in time (default 1s)
        """

        et = self.setPoint - pv # calculate e(t)
        d_et = ( et - self.etPrev ) / dt  # calculate de(t)/dt
        self.it += ( et * dt )  # add to the integral term
        self.etPrev = et  # set the previous error term (for next time)

        # calculate the new control variable
        self.controlVar = ( self.kp * et ) + ( self.ki * self.it ) + ( self.kd * d_et )
        self.write_control_var(self.controlVar)

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

        controlVar_t = cv  # temporary variable
        DSDO_bit = 2**4  # set Disable SDO bit

        # 4 channels: A, B, C, D
        # We load each to max, then spill over into the next channel.
        channelList = [0, 0, 0, 0]  
        for i in range(len(channelList)):
            if controlVar_t > 2**16:
                channelList[i] = 2**16
                controlVar_t -= 2**16
            else:
                channelList[i] = controlVar_t
                controlVar_t = 0

            channelSelect = DSDO_bit | 2**(5+i)
            self.dac_write_data(0x03, channelSelect)  # Select each channel
            self.dac_write_data(0x05, channelList[i])  # Write to the channel

        # Load the DAC
        self.io.dac_ldac(1)
        self.io.dac_ldac(0)
        self.io.dac_ldac(1)

    """
    Getters and Setters for a bunch of properties.
    """

    def __get_mode(self):
        return self.__mode

    def __set_mode(self, var):
        if var == 'PID' or var == 'BB' or var == 'FIXED':
            self.__mode = var
        else:
            raise DACError("Failed to initialize DAC. Improper Mode.")

    def __get_hysteresis(self):
        return self.__hysteresis

    def __set_hysteresis(self, var):
        self.__hysteresis = var

    def __get_kp(self):
        return self.__kp

    def __set_kp(self, var):
        self.__kp = var

    def __get_ki(self):
        return self.__ki

    def __set_ki(self, var):
        self.__ki = var

    def __get_kd(self):
        return self.__kd

    def __set_kd(self, var):
        self.__kd = var

    def __get_it(self):
        return self.__it

    def __set_it(self, var):
        self.__it = var        

    def __get_setPoint(self):
        return self.__setPoint

    def __set_setPoint(self, var):
        if var < 0:
            raise ValueError("Invalid setpoint.")
        self.__setPoint = var

    def __get_etPrev(self):
        return self.__etPrev

    def __set_etPrev(self, var):
        self.__etPrev = var

    def __get_controlVar(self):
        return self.__controlVar

    def __set_controlVar(self, var):
        self.__controlVar = var

    def __get_rebootMode(self):
        return self.__rebootMode
    
    def __set_rebootMode(self, var):
        self.__rebootMode = var

    mode = property(__get_mode, __set_mode)
    hysteresis = property(__get_hysteresis, __set_hysteresis)
    kp = property(__get_kp, __set_kp)
    ki = property(__get_ki, __set_ki)
    kd = property(__get_kd, __set_kd)
    it = property(__get_it, __set_it)
    setPoint = property(__get_setPoint, __set_setPoint)
    etPrev = property(__get_etPrev, __set_etPrev)
    controlVar = property(__get_controlVar, __set_controlVar)
    rebootMode = property(__get_rebootMode, __set_rebootMode)