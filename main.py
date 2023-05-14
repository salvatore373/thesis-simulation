import sys
import time
from contextlib import redirect_stdout

from bus_manager import BusManager
from car import Car
from ecus.abs import AntiLockBrakingSystem
from ecus.acm import AirbagControlModule
from ecus.attcker import AttackerECU, AttackTypes
from ecus.bcm import BodyControlModule
from ecus.ecm import EngineControlModule
from ecus.fake import FakeECU
from ecus.radio_ecu import RadioECU
from ecus.tcm import TransmissionControlModule


def start_all_ecus(bus):
    """
    Starts and attaches to the bus all the available ECUs
    :param bus: The bus where the ECUs should be attached
    """
    bcm = BodyControlModule(bus)
    bcm.start()
    radio_ecu = RadioECU(bus)
    radio_ecu.start()
    tcm_ecu = TransmissionControlModule(bus)
    tcm_ecu.start()
    ecm_ecu = EngineControlModule(bus)
    ecm_ecu.start()
    acm_ecu = AirbagControlModule(bus)
    acm_ecu.start()
    abs_ecu = AntiLockBrakingSystem(bus)
    abs_ecu.start()


def simulate_fdm_during_progression(bus, car):
    """
    Simulates a Freeze Doom Loop attack during the car's progression from 0km to a high speed.
    :param bus: The bus where the attack has to be performed
    :param car: The car where the attack has to be performed
    """
    sys.stdout = open('fdm-log.txt', 'w')
    bus.show_bus()

    # Start all the ECUs
    start_all_ecus(bus)

    # Attach the attacker ECU to the bus (when the car is already started)
    att_ecu = AttackerECU(bus, AttackTypes.FreezeDoomLoop)
    att_ecu.start()

    # Simulate a car speed progression
    car.reach_speed()


def simulate_dos_on_impact(bus, car):
    """
    Simulates a DoS attack during a car's impact.
    :param bus: The bus where the attack has to be performed
    :param car: The car where the attack has to be performed
    """
    sys.stdout = open('dos-log.txt', 'w')
    bus.show_bus()

    # Attach the attacker ECU to the bus
    att_ecu = AttackerECU(bus, AttackTypes.DoSOnImpact)
    att_ecu.start()

    # Start all the ECUs
    start_all_ecus(bus)

    # Simulate a car impact
    car.impact()


def simulate_unlocking_replay(bus, car):
    """
    Simulates a Replay attack to unlock the car after it has been locked
    :param bus: The bus where the attack has to be performed
    :param car: The car where the attack has to be performed
    """
    sys.stdout = open('rep-log.txt', 'w')
    bus.show_bus()

    # Attach the attacker ECU to the bus
    att_ecu = AttackerECU(bus, AttackTypes.ReplayToUnlock)
    att_ecu.start()

    # Start all the ECUs
    start_all_ecus(bus)

    # Simulate car locking and unlocking
    car.remote_locking(False)
    car.remote_locking(True)


def main():
    # Initialize the Bus and Car objects
    car = Car.get_instance()
    bus = BusManager()

    # simulate_dos_on_impact(bus, car) # stop after 7 sec
    # simulate_fdm_during_progression(bus, car) # stop after 20 sec
    simulate_unlocking_replay(bus, car)  # stop after 10 sec

    time.sleep(15)  # DEBUG
    bus.shutdown()


if __name__ == '__main__':
    main()
