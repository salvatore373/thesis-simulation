import codecs
import time
from abc import abstractmethod, ABC
from threading import Thread
from typing import Callable, Any, Union

import can
from can import Message

from bus_manager import BusManager

# The ID of the overload frame
OVERLOAD_ID = 0x3


# The ECUs superclass that implements all the base functionalities
class BaseECU(ABC):
    def __init__(self, bus: BusManager):
        """
        Create a ECU in the given CAN bus.

        :param bus: The CAN Bus instance where this ECU has to be installed
        """
        self.bus = bus

        # Whether the ECU is under the effect of an Overload frame received from the bus
        self.overloaded = False

    def send_msg(self, msg_id, data: Union[str, int]):
        """
        Send to the bus the message with the given ID and Data
        :param msg_id: The ID of the message to send
        :param data: The content of the Data field of the message to send
        """
        # Prevent the sending of messages if the ECU is overloaded
        if self.overloaded:
            return

        # Convert the given data in hexadecimal format
        if type(data) == int or type(data) == float:
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

    def _start_thread_exec(self):
        """
        The function to execute in a separate thread
        :return:
        """
        self.listen_to_bus(self._handle_overload_recv)
        self._start_operations()

    def start(self):
        """ Activate this ECU. All of its functions will start. """
        ecu_thread = Thread(target=self._start_thread_exec)
        ecu_thread.start()

    def listen_to_bus(self, callback: Callable) -> can.Listener:
        """
        Start listening to the bus. For each new message in the bus, the callback will be called with
        that message as input.
        :param callback: The function to call when a new message is trasmitted in the bus.
        :return The just created Listener object.
        """
        listener = BaseECUListener(callback)
        self.bus.listen(listener)
        return listener

    def stop_listening(self, listener: can.Listener):
        """
        Removes the given listener from the bus listeners
        :param listener: The listener to remove from the bus
        """
        self.bus.remove_listener(listener)

    def send_overload(self):
        """
        Sends an overload frame to the bus
        """
        self.send_msg(OVERLOAD_ID, 'overload')
        self.overloaded = True

    def _handle_overload_recv(self, msg: can.Message):
        """
        Handles the overload frame reception of this ECU from the bus
        :param msg: The message received from the bus
        """
        if msg.arbitration_id == OVERLOAD_ID and not self.overloaded:
            self.overloaded = True
            time.sleep(1)  # Make the overload effect noticeable blocking the ECU for 1 second
            self.overloaded = False


class BaseECUListener(can.Listener):
    def on_error(self, exc: Exception) -> None:
        print("The following exception occurred in the receive thread:", exc)

    def __init__(self, callback: Callable, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.callback = callback

    def on_message_received(self, msg: Message) -> None:
        self.callback(msg)
