import time

from bus_manager import BusManager
from car import Car
from ecus.abs import AntiLockBrakingSystem
from ecus.acm import AirbagControlModule
from ecus.ecm import EngineControlModule
from ecus.tcm import TransmissionControlModule


def main():
    bus = BusManager()
    bus.show_bus()

    # Start all the ECUs
    # ecu = FakeECU(bus)
    # ecu.start()
    # bcm = BodyControlModule(bus)
    # bcm.start()
    # radio_ecu = RadioECU(bus)
    # radio_ecu.start()
    # tcm_ecu = TransmissionControlModule(bus)
    # tcm_ecu.start()
    ecm_ecu = EngineControlModule(bus)
    ecm_ecu.start()
    acm_ecu = AirbagControlModule(bus)
    acm_ecu.start()
    abs_ecu = AntiLockBrakingSystem(bus)
    abs_ecu.start()

    # Initialize a Car object
    car = Car.get_instance()
    # Unlock the car
    # car.remote_locking(False)
    # car.reach_speed()
    car.impact()

    time.sleep(2)  # DEBUG
    bus.shutdown()


if __name__ == '__main__':
    main()
