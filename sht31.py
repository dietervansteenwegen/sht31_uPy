from micropython import const  # type:ignore  # use const to conserve memory
from utime import sleep_ms

SHT31_DEVICE_ADDRESS =  const(0x44)  # bus address: 0x44 (pin 2 to GND) or 0x45 (pin 2 to Vcc)
CMD_SOFT_RESET_ADDR =   const(0x30)  # register for soft reset
CMD_SOFT_RESET_VAL =    const(0xA2)  # value for soft reset
CMD_SSHIGHREP_ADDR =    const(0x2C)  # register to start single shot measurement
CMD_SSHIGHREP_VAL =     const(0x06)  # value for single shot measurement
CRC_POLYNOMIAL =        const(0x31)
CRC_INITIAL =           const(0xFF)  # initial value for CRC
# CMD_HEATER_ON =     bytearray(0x30, 0x6D)
# CMD_HEATER_OFF =    bytearray(0x30, 0x66)

class SHT31:
    """ Minimalistic implementation of the Sensirion SHT31 sensor.

    Supports basic functions:
    * Address set to 0x44 or 0x45
    * Setup (soft reset)
    * Single shot measurement
    * CRC verification 
    * Data conversion
    """

    def __init__(self, i2c) -> None:
        self.i2c = i2c
        self.addr = SHT31_DEVICE_ADDRESS
        sleep_ms(2)  # device needs 0.5 to 1ms to start up according to datasheet
        if not self._search_device() and self._initialize():
            return None

    def _search_device(self) -> bool:
        devices_found = self.i2c.scan()
        return SHT31_DEVICE_ADDRESS in devices_found  # returns True if the device is found
            
    def _initialize(self) -> None:
        self.i2c.mem_write(CMD_SOFT_RESET_VAL, SHT31_DEVICE_ADDRESS, CMD_SOFT_RESET_ADDR)  # reset
        sleep_ms(2)  # 0.5 to 1 ms according to datasheet
        # TODO: add check? Nothing is returned, maybe read? another scan?

    def measure(self) -> tuple:
        self.i2c.mem_write(CMD_SSHIGHREP_VAL, SHT31_DEVICE_ADDRESS, CMD_SSHIGHREP_ADDR)  # trigger (high repeatability, clock stretching en.)
        sleep_ms(20)  # 12.5 to 15 ms for high repeatability according to datasheet
        res = bytearray(6)
        self.i2c.mem_read(res, SHT31_DEVICE_ADDRESS, 0)  # read from device
        if not self._verify_CRC8(res[0:3]) and self._verify_CRC8(res[3:6]):
            return (None, None)
        return self._convert_raw(res)
    
    def _convert_raw(self,data) -> tuple:
        rh_raw = (data[3] << 8) + data [4]
        rh = 100 * (rh_raw / 65535)

        temp_raw = (data[0] << 8) + data [1]
        temp_C = -45 + 175*(temp_raw/65535)
        return temp_C, rh

    def _verify_CRC8(self, data:bytearray) -> bool:
        """ Calculate and verify CRC for 2 bytes of data.
        Expects a bytearray of 3 bytes: two data bytes and one CRC.

        From the datasheet:
        Name                    CRC-8 
        Width                   8 bit 
        Protected data          read and/or write data 
        Polynomial              0x31 (x8 + x5 + x4 + 1) 
        Initialization          0xFF 
        Reflect input/output    False 
        Final                   XOR 0x00 
        Example                 0xBEEF -> 0x92 

        Returns         True if correct
                        False if not correct
        """
        crc = CRC_INITIAL
        for byte in data[0:2]:  # go over the 2 bytes
            crc ^= byte
            for _ in range(8):   # go over all bits in each byte
                if (crc & 0x80):
                    crc = ((crc <<1) ^ CRC_POLYNOMIAL) & 0xFF
                else:
                    crc = (crc << 1) & 0xFF
                byte >>= 1  # shift to next bit

        return crc == data[2]