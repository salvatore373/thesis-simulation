import codecs
import string
from abc import abstractmethod, ABC
from threading import Thread
from typing import Callable, Any, Union

import can
from can import Message

from bus_manager import BusManager


# The ECUs superclass that implements all the base functionalities
class BaseECU(ABC):
    def __init__(self, bus: BusManager):
        """
        Create a ECU in the given CAN bus.

        :param bus: The CAN Bus instance where this ECU has to be installed
        """
        self.bus = bus

    def send_msg(self, msg_id, data: Union[str, int]):
        """
        Send to the bus the message with the given ID and Data
        :param msg_id: The ID of the message to send
        :param data: The content of the Data field of the message to send
        """
        # Convert the given data in hexadecimal format
        if type(data) == int:
            data = str(data)
        if type(data) == str:
            data = codecs.encode(data.encode(), 'hex')

        msg = can.Message(arbitration_id=msg_id, data=data, is_extended_id=False)
        self.bus.send(msg)

    @abstractmethod
    def _start_operations(self):
        """
        This method is called when the ECU has to start working in the bus. All the functions of this
        ECU must be activated here.
        """
        pass

    def start(self):
        """ Activate this ECU. All of its functions will start. """
        ecu_thread = Thread(target=self._start_operations)
        ecu_thread.start()

    def listen_to_bus(self, callback: Callable):
        """
        Start listening to the bus. For each new message in the bus, the callback will be called with
        that message as input.
        :param callback: The function to call when a new message is trasmitted in the bus.
        """
        listener = BaseECUListener(callback)
        self.bus.listen(listener)


class BaseECUListener(can.Listener):
    def __init__(self, callback: Callable, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.callback = callback

    def on_message_received(self, msg: Message) -> None:
        self.callback(msg)
