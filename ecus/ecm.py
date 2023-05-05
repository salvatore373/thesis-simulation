from bus_manager import BusManager
import car as car_module
from ecus.base_ecu import BaseECU
import codecs

RPM = 0x51
SPEED = 0x52
BRAKE_PERCENTAGE = 0x53


# TODO: fill comment
class EngineControlModule(BaseECU):
    def __init__(self, bus: BusManager):
        super().__init__(bus)

        self.speed = 0
        self.rpm = 0

    def _start_operations(self):
        car = car_module.Car.get_instance()
        # When the sensors read a new speed or RPM save them locally and send them on the bus
        car.subscribe_to_event(car_module.CarSensorsEvents.SPEED, self.__save_speed)
        car.subscribe_to_event(car_module.CarSensorsEvents.RPM, self.__save_rpm)
        # Send to the bus information about brake percentage gained from the sensors
        car.subscribe_to_event(car_module.CarSensorsEvents.HARD_BRAKE, self.__send_brake_percentage)
        pass

    def __save_speed(self, new_speed: int):
        self.speed = new_speed
        # Send a message on the base with the new speed in Hex as data
        self.send_msg(SPEED, new_speed)

    def __save_rpm(self, new_rpm: int):
        self.rpm = new_rpm
        # Send a message on the base with the new RPM in Hex as data
        self.send_msg(RPM, new_rpm)

    def __send_brake_percentage(self, brake_percentage: int):
        # Send a message on the base with the brake percentage in Hex as data
        self.send_msg(BRAKE_PERCENTAGE, brake_percentage)
