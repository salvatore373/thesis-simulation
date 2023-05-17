import codecs

import can

import car as car_module
from ecus.base_ecu import BaseECU
from ecus.ecm import RPM

# Define the IDs of the message types
GEAR_SHIFT = 0x201


# The Transmission Control Module ECU
class TransmissionControlModule(BaseECU):
    def __init__(self, bus):
        super().__init__(bus)
        self.gear = 0
        self.last_rpm = 0
        self.can_change = True

    def _start_operations(self):
        car = car_module.Car.get_instance()
        # Start moving the car on startup
        car.subscribe_to_event(car_module.CarSensorsEvents.STARTUP, self.__on_startup)

        # Listen to messages on the bus
        self.listen_to_bus(self.__listen_for_rpm)

    def shift_gear(self, delta: int):
        """
        Changes the gear of the car of a delta value.
        :param delta: An integer to increase or decrease the gear (e.g. delta=-1 -> downshift)
        """
        self.gear += delta

        car = car_module.Car.get_instance()
        car.change_gear(delta)

        self.send_msg(GEAR_SHIFT, delta)

    def __on_startup(self):
        """
        The function to call when the car is started.
        """
        self.shift_gear(1)

    def __listen_for_rpm(self, msg: can.Message):
        """
        Listen to the bus waiting for messages about the RPM
        :param msg: The message on the bus
        """
        if msg.arbitration_id == RPM:
            rpm = float(codecs.decode(msg.data, 'hex'))

            # Check whether the gear change took effect, and allow to change the gear again
            if not self.can_change and self.last_rpm > rpm:
                self.can_change = True

            # Change the gear when the RPM go over 2500 (and the gear has not just been shifted)
            if rpm > 2500 and self.can_change:
                self.shift_gear(1)
                self.can_change = False

            self.last_rpm = rpm
