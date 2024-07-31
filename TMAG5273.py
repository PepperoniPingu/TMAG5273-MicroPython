# TMAG5273 Magnetometer MicroPython Library
# ver: 1.0
# License: MIT
# Author: Jacob Williams (jrw4561@gmail.com)

try:
    from uctypes import struct, addressof, BFUINT8, BF_POS, BF_LEN
    from micropython import const
except (TypeError, ModuleNotFoundError):
    # Import wrapped in a try/except so that autodoc generation can process properly
    pass
from machine import I2C, Pin, Timer, disable_irq, enable_irq
import time, math

"""
	I2C address
"""
TMAG_ADDR_PRIMARY   = const(0x22)

"""
	Register addresses
"""

TMAG_REG_DEVICE_CONFIG_1      = const(0x00)
TMAG_REG_DEVICE_CONFIG_2      = const(0x01)
TMAG_REG_SENSOR_CONFIG_1      = const(0x02)
TMAG_REG_SENSOR_CONFIG_2      = const(0x03)
TMAG_REG_X_THR_CONFIG         = const(0x04)
TMAG_REG_Y_THR_CONFIG         = const(0x05)
TMAG_REG_Z_THR_CONFIG         = const(0x06)
TMAG_REG_T_CONFIG             = const(0x07)
TMAG_REG_INT_CONFIG_1         = const(0x08)
TMAG_REG_MAG_GAIN_CONFIG      = const(0x09)
TMAG_REG_MAG_OFFSET_CONFIG_1  = const(0x0A)
TMAG_REG_MAG_OFFSET_CONFIG_2  = const(0x0B)
TMAG_REG_I2C_ADDRESS          = const(0x0C)
TMAG_REG_DEVICE_ID            = const(0x0D)
TMAG_REG_MANUFACTURER_ID_LSB  = const(0x0E)
TMAG_REG_MANUFACTURER_ID_MSB  = const(0x0F)
TMAG_REG_T_MSB_RESULT         = const(0x10)
TMAG_REG_T_LSB_RESULT         = const(0x11)
TMAG_REG_X_MSB_RESULT         = const(0x12)
TMAG_REG_X_LSB_RESULT         = const(0x13)
TMAG_REG_Y_MSB_RESULT         = const(0x14)
TMAG_REG_Y_LSB_RESULT         = const(0x15)
TMAG_REG_Z_MSB_RESULT         = const(0x16)
TMAG_REG_Z_LSB_RESULT         = const(0x17)
TMAG_REG_CONV_STATUS          = const(0x18)
TMAG_REG_ANGLE_RESULT_MSB     = const(0x19)
TMAG_REG_ANGLE_RESULT_LSB     = const(0x1A)
TMAG_REG_MAGNITUDE_RESULT     = const(0x1B)
TMAG_REG_DEVICE_STATUS        = const(0x1C)

"""
	Bit field struct definitions of registers
"""

TMAG_REG_LAYOUT_DEVICE_CONFIG_1 = {
    "CRC_EN"     : BFUINT8 | 7 << BF_POS | 1 << BF_LEN,
    "MAG_TEMPCO" : BFUINT8 | 5 << BF_POS | 2 << BF_LEN,
    "CONV_AVG"   : BFUINT8 | 2 << BF_POS | 3 << BF_LEN,
    "I2C_RD"     : BFUINT8 | 0 << BF_POS | 2 << BF_LEN,
}
TMAG_REG_LAYOUT_DEVICE_CONFIG_2 = {
    "THR_HYST"             : BFUINT8 | 5 << BF_POS | 3 << BF_LEN,
    "LP_LN"                : BFUINT8 | 4 << BF_POS | 1 << BF_LEN,
    "I2C_GLITCH_FILTER"    : BFUINT8 | 3 << BF_POS | 1 << BF_LEN,
    "TRIGGER_MODE"         : BFUINT8 | 2 << BF_POS | 1 << BF_LEN,
    "OPERATING_MODE"       : BFUINT8 | 0 << BF_POS | 2 << BF_LEN,
}
TMAG_REG_LAYOUT_SENSOR_CONFIG_1 = {
    "MAG_CH_EN"    : BFUINT8 | 4 << BF_POS | 4 << BF_LEN,
    "SLEEPTIME"    : BFUINT8 | 0 << BF_POS | 4 << BF_LEN,
}
TMAG_REG_LAYOUT_SENSOR_CONFIG_2 = {
    "RESERVED"       : BFUINT8 | 7 << BF_POS | 1 << BF_LEN,
    "THRX_COUNT"     : BFUINT8 | 6 << BF_POS | 1 << BF_LEN,
    "MAG_THR_DIR"    : BFUINT8 | 5 << BF_POS | 1 << BF_LEN,
    "MAG_GAIN_CH"    : BFUINT8 | 4 << BF_POS | 1 << BF_LEN,
    "ANGLE_EN"       : BFUINT8 | 2 << BF_POS | 2 << BF_LEN,
    "X_Y_RANGE"      : BFUINT8 | 1 << BF_POS | 1 << BF_LEN,
    "Z_RANGE"        : BFUINT8 | 0 << BF_POS | 1 << BF_LEN,
}
TMAG_REG_LAYOUT_T_CONFIG = {
    "T_THR_CONFIG"  : BFUINT8 | 1 << BF_POS | 7 << BF_LEN,
    "T_CH_EN"       : BFUINT8 | 0 << BF_POS | 1 << BF_LEN,
}
TMAG_REG_LAYOUT_DEVICE_ID = {
    "RESERVED"  : BFUINT8 | 2 << BF_POS | 6 << BF_LEN,
    "VER"       : BFUINT8 | 0 << BF_POS | 2 << BF_LEN,
}


"""
	Dictionaries for possible register settings
"""

OPERATING_MODE = {
    "STANDBY_MODE": 0x0,                # Stand-by mode
    "SLEEP_MODE": 0x1,                  # Sleep mode
    "CONTINUOUS_MEASURE_MODE": 0x2,     # Continuous measure mode
    "WAKE_UP_AND_SLEEP_MODE": 0x3,      # Wake-up and sleep mode
}

MAG_CH_EN = {
    "CHANNELS_OFF": 0x0,     # Turn all the magnetic channels off
    "X_ENABLE": 0x1,         # X Channel enabled
    "Y_ENABLE": 0x2,         # Y Channel enabled
    "X_Y_ENABLE": 0x3,       # X, Y Channel enabled
    "Z_ENABLE": 0x4,         # Z Channel enabled
    "Z_X_ENABLE": 0x5,       # Z, X Channel enabled
    "Y_Z_ENABLE": 0x6,       # Y, Z Channel enabled
    "X_Y_Z_ENABLE": 0x7,     # X, Y, Z Channel enabled
    "XYX_ENABLE": 0x8,       # XYX Channel enabled
    "YXY_ENABLE": 0x9,       # YXY Channel enabled
    "YZY_ENABLE": 0xA,       # YZY Channel enabled
    "XZX_ENABLE": 0xB,       # XZX Channel enabled
}

X_Y_Z_RANGES = {
    "RANGE_40MT": 0x0,   # +/-40mT, DEFAULT
    "RANGE_80MT": 0x1,   # +/-80mT, DEFAULT
}

class HallSensor():

    _DEFAULT_TMAG_INSTANCE = None

    @classmethod
    def get_default_tmag(cls):
        """
        Get the default TMAG instance.
        """

        if cls._DEFAULT_TMAG_INSTANCE is None:
            cls._DEFAULT_TMAG_INSTANCE = cls(
                scl_pin=19,
                sda_pin=18,
                addr=TMAG_ADDR_PRIMARY
            )  
        return cls._DEFAULT_TMAG_INSTANCE

    def __init__(self, scl_pin: int, sda_pin: int, addr):
        # I2C values
        self.i2c = I2C(id=1, scl=Pin(scl_pin), sda=Pin(sda_pin), freq=400000)
        self.addr = addr

        # Initialize member variables
        self._reset_member_variables()

        # Transmit and recieve buffers
        self.tb = bytearray(1)
        self.rb = bytearray(1)

        # Copies of registers. Bytes and structs share the same memory
        # addresses, so changing one changes the other
        self.reg_byte_device_config_1  = bytearray(1)
        self.reg_byte_device_config_2  = bytearray(1)
        self.reg_byte_sensor_config_1  = bytearray(1)
        self.reg_byte_sensor_config_2  = bytearray(1)
        self.reg_byte_t_config         = bytearray(1)
        self.reg_byte_device_id        = bytearray(1)
        self.reg_bits_device_config_1  = struct(addressof(self.reg_byte_device_config_1), TMAG_REG_LAYOUT_DEVICE_CONFIG_1)
        self.reg_bits_device_config_2  = struct(addressof(self.reg_byte_device_config_2), TMAG_REG_LAYOUT_DEVICE_CONFIG_2)
        self.reg_bits_sensor_config_1  = struct(addressof(self.reg_byte_sensor_config_1), TMAG_REG_LAYOUT_SENSOR_CONFIG_1)
        self.reg_bits_sensor_config_2  = struct(addressof(self.reg_byte_sensor_config_2), TMAG_REG_LAYOUT_SENSOR_CONFIG_2)
        self.reg_bits_t_config         = struct(addressof(self.reg_byte_t_config), TMAG_REG_LAYOUT_T_CONFIG)
        self.reg_bits_device_id        = struct(addressof(self.reg_byte_device_id), TMAG_REG_LAYOUT_DEVICE_ID)

        # Check if the MAG is connected
        if not self.is_connected():
            # TODO - do something intelligent here
            pass
        
        self.set_magnetic_channel('X_Y_Z_ENABLE')
        self.set_temperature_enabled(True)
        self.set_operating_mode('CONTINUOUS_MEASURE_MODE')

        #Set the axis ranges for the device to be the largest
        self.set_xy_axis_range('RANGE_80MT')
        self.set_z_axis_range('RANGE_80MT')

    """
        The following are private helper methods to read and write registers, as well as to convert the read values to the correct unit.
    """

    def _reset_member_variables(self):
        self.range_val_xy = 0
        self.range_val_z = 0

    def _uint16_to_int16(self, d):
        if d < 0x8000:
            return d
        else:
            return d - 0x10000

    def _setreg(self, reg, dat):
        self.tb[0] = dat
        self.i2c.writeto_mem(self.addr, reg, self.tb)

    def _getreg(self, reg):
        self.i2c.readfrom_mem_into(self.addr, reg, self.rb)
        return self.rb[0]

    def _getregs(self, reg, num_bytes):
        rx_buf = bytearray(num_bytes)
        self.i2c.readfrom_mem_into(self.addr, reg, rx_buf)
        return rx_buf

    def _get2reg(self, reg):
        return self._getreg(reg) + self._getreg(reg+1) * 256

    def _r_w_reg(self, reg, dat, mask):
        self._getreg(reg)
        self.rb[0] = (self.rb[0] & mask) | dat
        self._setreg(reg, self.rb[0])

    """
        Public facing API Methods
    """

    def is_connected(self):
        """
        Checks whether the IMU is connected

        :return: True if DEVICE_ID value is correct, otherwise False
        :rtype: bool
        """
        self.reg_byte_device_id = self._getreg(TMAG_REG_DEVICE_ID)

        return (self.reg_bits_device_id.VER == 1 or self.reg_bits_device_id.VER == 2)

    def set_magnetic_channel(self, value):
        """
        Set which magnetometer channels are enabled
        """
        # Get register value
        self.reg_byte_sensor_config_1[0] = self._getreg(TMAG_REG_SENSOR_CONFIG_1)

        # Set value as requested
        self.reg_bits_sensor_config_1.MAG_CH_EN = MAG_CH_EN[value]
        self._setreg(TMAG_REG_SENSOR_CONFIG_1, self.reg_byte_sensor_config_1[0])

    def set_temperature_enabled(self, value):
        """
        Set which magnetometer channels are enabled
        """
        # Get register value
        self.reg_byte_t_config[0] = self._getreg(TMAG_REG_T_CONFIG)

        # Set value as requested
        if(value):
            self.reg_bits_t_config.T_CH_EN = 0x01
        else:
            self.reg_bits_t_config.T_CH_EN = 0x00

        self._setreg(TMAG_REG_T_CONFIG, self.reg_byte_t_config[0])

    def set_operating_mode(self, value):
        """
        Sets the operating mode
        """
        # Get register value
        self.reg_byte_device_config_2[0] = self._getreg(TMAG_REG_DEVICE_CONFIG_2)

        # Set value as requested
        self.reg_bits_device_config_2.OPERATING_MODE = OPERATING_MODE[value]
        self._setreg(TMAG_REG_DEVICE_CONFIG_2, self.reg_byte_device_config_2[0])

    def set_xy_axis_range(self, value):
        """
        Set which X axis and Y axis range to use
        """
        # Get register value
        self.reg_byte_sensor_config_2[0] = self._getreg(TMAG_REG_SENSOR_CONFIG_2)

        # Set value as requested
        self.reg_bits_sensor_config_2.X_Y_RANGE = X_Y_Z_RANGES[value]
        self._setreg(TMAG_REG_SENSOR_CONFIG_2, self.reg_byte_sensor_config_2[0])
        self.range_val_xy = self.reg_bits_sensor_config_2.X_Y_RANGE

    def set_z_axis_range(self, value):
        """
        Set which Z axis range to use
        """
        # Get register value
        self.reg_byte_sensor_config_2[0] = self._getreg(TMAG_REG_SENSOR_CONFIG_2)

        # Set value as requested
        self.reg_bits_sensor_config_2.Z_RANGE = X_Y_Z_RANGES[value]
        self._setreg(TMAG_REG_SENSOR_CONFIG_2, self.reg_byte_sensor_config_2[0])
        self.range_val_z = self.reg_bits_sensor_config_2.Z_RANGE


    def get_temp(self):
        """
        :return: The current reading for the magnetometer's temperature sensor in Celcius
        :rtype: floa
        """
        raw_LSB = self._getreg(TMAG_REG_T_LSB_RESULT)
        raw_MSB = self._getreg(TMAG_REG_T_MSB_RESULT)
        
        raw_t = self._uint16_to_int16((raw_MSB << 8) + raw_LSB)

        T_SNS_T0 = 25
        T_ADC_T0 = 17508
        T_ADC_RES = 60.1
        
        temp_celcius = T_SNS_T0 + ((raw_t - T_ADC_T0) / T_ADC_RES)
        
        print(f"rawmsb: {raw_MSB:>8.3f}     rawlsb: {raw_LSB:>8.3f}   celcius: {temp_celcius:>8.3f}")


    def get_mag_x(self):
        """
        :return: The current reading for the magnetometer's X-axis, in mT
        :rtype: float
        """
        raw_LSB = self._getreg(TMAG_REG_X_LSB_RESULT)
        raw_MSB = self._getreg(TMAG_REG_X_MSB_RESULT)
        
        raw_x = self._uint16_to_int16((raw_MSB << 8) + raw_LSB)
        
        if (self.range_val_xy == 0):
            return (40/32768 * raw_x)
        elif (self.range_val_xy == 1):
            return (80/32768 * raw_x)
        else:
            return 0
            

    def get_mag_y(self):
        """
        :return: The current reading for the magnetometer's Y-axis, in mT
        :rtype: float
        """
        raw_LSB = self._getreg(TMAG_REG_Y_LSB_RESULT)
        raw_MSB = self._getreg(TMAG_REG_Y_MSB_RESULT)
        
        raw_y = self._uint16_to_int16((raw_MSB << 8) + raw_LSB)
        
        if (self.range_val_xy == 0):
            return (40/32768 * raw_y)
        elif (self.range_val_xy == 1):
            return (80/32768 * raw_y)
        else:
            return 0
            
    def get_mag_z(self):
        """
        :return: The current reading for the magnetometer's Z-axis, in mT
        :rtype: float
        """
        raw_LSB = self._getreg(TMAG_REG_Z_LSB_RESULT)
        raw_MSB = self._getreg(TMAG_REG_Z_MSB_RESULT)
        
        raw_z = self._uint16_to_int16((raw_MSB << 8) + raw_LSB)
        
        if (self.range_val_xy == 0):
            return (40/32768 * raw_z)
        elif (self.range_val_xy == 1):
            return (80/32768 * raw_z)
        else:
            return 0