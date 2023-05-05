import codecs
import re

import car as car_module
from ecus.base_ecu import BaseECU

AIRBAG_STATUS = 0x8
SEATBELT_STATUS = 0x9
IMPACT_SENSOR_READ = 0x10


# TODO: fill comment
class AirbagControlModule(BaseECU):
    def __init__(self, bus):
        super().__init__(bus)
        self.gear = 0

    def _start_operations(self):
        car = car_module.Car.get_instance()
        # Read from the car sensors the impact force
        car.subscribe_to_event(car_module.CarSensorsEvents.IMPACT, self.__get_impact_force)

    def __get_impact_force(self, impact_force):
        """
        Read from the sensors the impact force and send it to the bus.
        :param impact_force: The impact force read by the sensors.
        """
        g_force = re.search('[0-9]+(?=G)', impact_force).group(0)
        self.send_msg(IMPACT_SENSOR_READ, g_force)
        if int(g_force) > 60:
            self.__activate_safety_procedure()

    def __activate_safety_procedure(self):
        """
        Interact with the other ECUs to protect the car's passengers from the impact.
        :return:
        """
        # Alert the other ECUs that the Airbag system has been deployed
        self.send_msg(AIRBAG_STATUS, 'DEPLOYED')

        # Block the seatbelts
        self.send_msg(SEATBELT_STATUS, 'BLOCK')
