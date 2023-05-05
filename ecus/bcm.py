from bus_manager import BusManager
from ecus.base_ecu import BaseECU
from ecus.radio_ecu import LOCKING, UNLOCKING

CAR_LOCKED = 0X501
CAR_UNLOCKED = 0X502


# TODO: fill comment
class BodyControlModule(BaseECU):
    def __init__(self, bus: BusManager):
        super().__init__(bus)
        # Whether the security system is active or not
        self.locked = False

    def _start_operations(self):
        # Listen to RadioECU's frame to lock/unlock
        self.listen_to_bus(self.__radio_ecu_listener)
        pass

    def __radio_ecu_listener(self, msg):
        """
        Listens for the Radio ECU's frames to respond to locking or unlocking events. This method has to
        be passed to BusManager.listen_to_bus() method.
        :param msg: The message read from the bus.
        """
        if msg.arbitration_id == LOCKING:
            self.edit_locking(True)
        elif msg.arbitration_id == UNLOCKING:
            self.edit_locking(False)

    def edit_locking(self, new_val: bool):
        """
        Activate/Deactivate the security system
        :param new_val: True if the car has to be locker, False if it has to be unlocked.
        :return:
        """
        self.locked = new_val

        if new_val:
            self.send_msg(CAR_LOCKED, 'LOCKED')
        else:
            self.send_msg(CAR_UNLOCKED, 'UNLOCKED')
