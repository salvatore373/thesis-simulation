import codecs

import can

from ecus.base_ecu import BaseECU
from ecus.ecm import BRAKE_PERCENTAGE

ABS_SYSTEM_STATUS = 0x11


# Anti-lock Breaking System Module
class AntiLockBrakingSystem(BaseECU):
    def __init__(self, bus):
        super().__init__(bus)
        self.gear = 0

    def _start_operations(self):
        self.listen_to_bus(self.__read_brake_percentage)

    def __read_brake_percentage(self, msg: can.Message):
        """
        Listen to the bus and activate the ABS System when the read brake percentage is too high.
        :param msg: The message read from the bus.
        :return:
        """
        if msg.arbitration_id == BRAKE_PERCENTAGE:
            brake_percentage = int(codecs.decode(msg.data, 'hex'))
            if brake_percentage > 90:
                self.send_msg(ABS_SYSTEM_STATUS, 'ACTIVE')
