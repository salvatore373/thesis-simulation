import time
from datetime import datetime, timedelta
from enum import Enum

from car import Car, CarSensorsEvents
from ecus.base_ecu import BaseECU


# The type of attacks that this ECU can perform
class AttackTypes(Enum):
    DoSOnImpact = 1,  # When the car detects and impact performs a DoS attack against the bus
    Replay = 2,
    FreezeDoomLoop = 3


# An ECU designed to perform attacks against the bus where it is installed
class AttackerECU(BaseECU):
    def _start_operations(self):
        car = Car.get_instance()
        if self.attack_type == AttackTypes.DoSOnImpact:
            car.subscribe_to_event(CarSensorsEvents.IMPACT, lambda x: self._perform_dos())
        elif self.attack_type == AttackTypes.Replay:
            pass
        elif self.attack_type == AttackTypes.FreezeDoomLoop:
            self._perform_freeze_doom_loop()

    def __init__(self, bus, attack_type: AttackTypes):
        super().__init__(bus)
        self.attack_type = attack_type

    def _perform_dos(self):
        """
        Performs a DoS attack against the bus sending many messages of maximum priority.
        The bus will stay blocked for 5 seconds.
        """
        start = datetime.now()
        while datetime.now() - start <= timedelta(seconds=5):
            self.send_msg(0x0, 'DoS')

    def _perform_replay(self):
        pass

    def _perform_freeze_doom_loop(self):
        """
        Performs a Freeze Doom Loop attack on the bus sending many Overload frames.
        The bus is frozen for 5 seconds.
        """
        # Wait 5 seconds before starting the attack
        time.sleep(5)

        start = datetime.now()
        while datetime.now() - start <= timedelta(seconds=5):
            self.send_overload()
        print("end")
