import car as car_module
from bus_manager import BusManager
from ecus.base_ecu import BaseECU

LOCKING = 0x401
UNLOCKING = 0x402


# TODO: fill comment
class RadioECU(BaseECU):
    def __init__(self, bus: BusManager):
        super().__init__(bus)

    def _start_operations(self):
        car = car_module.Car.get_instance()
        # When the remote input is received, transmit it to the bus
        car.subscribe_to_event(car_module.CarSensorsEvents.RADIO_LOCK, self.edit_locking)

    def edit_locking(self, new_val: bool):
        """
        Ask the BCM ECU to activate/deactivate the security system via the bus
        :param new_val: True if the car has to be locker, False if it has to be unlocked.
        """
        if new_val:
            self.send_msg(LOCKING, 'LOCKED')
        else:
            self.send_msg(UNLOCKING, 'UNLOCKED')
