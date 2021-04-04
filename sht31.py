from micropython import const  # type:ignore  # use const to conserve memory

DEVICE_ADDRESS =    const(0x44)  # Either 0x44 (default, pin 2 to GND) or 0x45 (pin 2 to Vcc)
CMD_SOFT_RESET =    const(bytearray(0x30, 0xA2))
CMD_HEATER_ON =     const(bytearray(0x30, 0x6D))
CMD_HEATER_OFF =    const(bytearray(0x30, 0x66))
# CMD_SSHIGHREP =     const(bytearray(0x2C, 0x06))
# CMD_SSMIDREP =      const(bytearray(0x2C, 0x0D))
# CMD_SSLOWREP =      const(bytearray(0x2C, 0x10))

class SHT31:
    """ Minimalistic implementation of the Sensirion SHT31 sensor.

    Supports basic functions:
    * Address set to 0x44 or 0x45
    * Setup
    * Single shot measurement
    * CRC verification
    * Data conversion
    """

    def __init__(self, i2c):
        self.i2c = i2c
        self.addr = DEVICE_ADDRESS
        if not self._search_device() and self._initialize():
            return None

    def _search_device(self):
        devices_found = self.i2c.scan()
        return DEVICE_ADDRESS in devices_found  # returns True if the device is found
            
    def _initialize(self):
        self.i2c.write_to


