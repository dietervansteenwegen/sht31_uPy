from micropython import const  # type:ignore  # use const to conserve memory
from utime import sleep_ms

DEVICE_ADDRESS =    const(0x44)  # Either 0x44 (default, pin 2 to GND) or 0x45 (pin 2 to Vcc)
# CMD_SOFT_RESET =    bytearray(0x30, 0xA2)
CMD_SOFT_RESET_ADDR =    const(0x30)
CMD_SOFT_RESET_VAL =    const(0xA2)
# CMD_HEATER_ON =     bytearray(0x30, 0x6D)
# CMD_HEATER_OFF =    bytearray(0x30, 0x66)
# CMD_SSHIGHREP =     bytearray(0x2C, 0x06)
CMD_SSHIGHREP_ADDR =     const(0x2C)
CMD_SSHIGHREP_VAL =     const(0x06)

class SHT31:
    """ Minimalistic implementation of the Sensirion SHT31 sensor.

    Supports basic functions:
    * Address set to 0x44 or 0x45
    * Setup
    * Single shot measurement
    * (TODO)CRC verification 
    * Data conversion
    """

    def __init__(self, i2c) -> None:
        self.i2c = i2c
        self.addr = DEVICE_ADDRESS
        sleep_ms(2)  # device needs 0.5 to 1ms to start up according to datasheet
        if not self._search_device() and self._initialize():
            return None

    def _search_device(self) -> bool:
        devices_found = self.i2c.scan()
        return DEVICE_ADDRESS in devices_found  # returns True if the device is found
            
    def _initialize(self) -> None:
        self.i2c.mem_write(CMD_SOFT_RESET_VAL, DEVICE_ADDRESS, CMD_SOFT_RESET_ADDR)  # reset
        sleep_ms(2)  # 0.5 to 1 ms according to datasheet
        # TODO: add check? Nothing is returned, maybe read? another scan?

    def measure(self) -> tuple:
        self.i2c.mem_write(CMD_SSHIGHREP_VAL, DEVICE_ADDRESS, CMD_SSHIGHREP_ADDR)  # trigger (high repeatability, clock stretching en.)
        sleep_ms(20)  # 12.5 to 15 ms for high repeatability according to datasheet
        res = bytearray(6)
        self.i2c.mem_read(res, DEVICE_ADDRESS, 0)  # read from device
        # TODO: CRC check
        # if not self._checkCRC[res[0:3] and self._checkCRC[3:6]:
        #     return None
        return self._convert_raw(res)
    
    def _convert_raw(self,data) -> tuple:
        rh_raw = (data[3] << 8) + data [4]
        rh = 100 * (rh_raw / 65535)

        temp_raw = (data[0] << 8) + data [1]
        temp_C = -45 + 175*(temp_raw/65535)
        return temp_C, rh

    def _calc_twos_complement(self, value, bits:int):
        if (value & (1 << (bits-1))):  # if bit 16 is 1, convert
            value -= (1 << bits)  # convert by substracting the maximum value
        return value



