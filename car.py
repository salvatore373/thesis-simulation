import time
from datetime import datetime
from enum import Enum

from pyee.base import EventEmitter


class CarSensorsEvents(str, Enum):
    # The event fired when the car's remote sends the msg to the Radio Receiver ECU to lock/unlock the car
    RADIO_LOCK = 'RADIO_LOCK'
    # The event fired from the sensors that read the car's speed
    SPEED = 'SPEED'
    # The event fired from the sensors that read the engine's RPM
    RPM = 'RPM'
    # The event fired when the car is started
    STARTUP = 'STARTUP'
    # The event fired when the driver makes a hard brake
    HARD_BRAKE = 'HARD_BRAKE'
    # The event fired when the car impacts against an obstacle
    IMPACT = 'IMPACT'


# A singleton class that simulates the vehicle that the CAN bus is installed on.
# This should perform the main functionalities of a car, in order to
# show a realistic CAN traffic.
# The methods of this class act as components, that perform actions on the car, and sensors,
# that warn all the interested ECUs of a specific event that has just happened.
class Car:
    class_instance = None

    @staticmethod
    def get_instance():
        if Car.class_instance is None:
            Car.class_instance = Car()
        return Car.class_instance

    def __init__(self):
        self.ev_emitter = EventEmitter()

        # The default status of the car's sensors
        self.gear = 0  # -1=R 0=N
        self.speed = 0
        self.rpm = 0

    def subscribe_to_event(self, event_id, callback):
        self.ev_emitter.add_listener(event_id, callback)

    def remote_locking(self, new_val: bool):
        """
        Lock or unlock the car from the remote passing a boolean
        :param new_val: True if the car has to be locker, False if it has to be unlocked.
        """
        self.ev_emitter.emit(CarSensorsEvents.RADIO_LOCK, new_val)

    def change_gear(self, delta: int):
        """
        When triggered by the TCM, change the gear
        :param delta: An integer to increase or decrease the gear (e.g. delta=-1 -> downshift)
        """
        self.gear += delta

    def reach_speed(self):
        """
        The car started moving, then get through the sensors all the information about the car.
        """
        # Startup the car
        self.ev_emitter.emit(CarSensorsEvents.STARTUP)

        # Go from 0km/h to 100km/h (linear speed based on gear)
        t = 1
        last_gear = 0
        while self.speed < 100:
            # Update speed
            if self.gear == 1:
                if self.speed < 15:
                    self.speed += 1
            elif self.gear == 2:
                if self.speed < 30:
                    self.speed += 1
            elif self.gear == 3:
                if self.speed < 55:
                    self.speed += 1
            elif self.gear == 4:
                if self.speed < 70:
                    self.speed += 1
            elif self.gear == 5:
                if self.speed < 100:
                    self.speed += 1
            elif self.gear == 6:
                if self.speed < 120:
                    self.speed += 1
            elif self.gear == 7:
                if self.speed < 150:
                    self.speed += 1

            # The sensor sends the current speed to the interested ECUs
            self.ev_emitter.emit(CarSensorsEvents.SPEED, self.speed)

            # Update the RPM
            if self.gear > last_gear:
                t = 1
                last_gear = self.gear
            self.rpm = min(((3 - (0.5 * (self.gear - 1))) * t + 7) * 100, 3500)
            t += 1

            # The sensor sends the current speed to the interested ECUs
            self.ev_emitter.emit(CarSensorsEvents.RPM, self.rpm)

            print('\nspeed: ', self.speed, ' RPM: ', self.rpm, ' gear: ', self.gear, '\n')

            # Slow up the process to make it visible
            time.sleep(0.1)

    def impact(self):
        """
        While the car is moving at max speed impacts an obstacle
        """

        self.reach_speed()

        # The driver makes a hard brake (the brake pedal sensor detects a 100% press)
        brake_time = datetime.now().timestamp()
        self.ev_emitter.emit(CarSensorsEvents.HARD_BRAKE, 100)

        # The car impacts against an obstacle (impact sensors detect a 65G impact force)
        impact_time = datetime.now().timestamp()
        self.ev_emitter.emit(CarSensorsEvents.IMPACT, '65G')

        print('brake time: ', brake_time)
        print('impact time: ', impact_time)
