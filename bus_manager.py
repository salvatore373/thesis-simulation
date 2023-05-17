import can


# The manager of the bus and all the connected ECUs
class BusManager:
    def __init__(self):
        # Initialize CAN Bus interface
        self.bus_send = can.ThreadSafeBus('test', interface='virtual')
        self.bus_recv = can.ThreadSafeBus('test', interface='virtual')

        self.notifier = can.Notifier(self.bus_recv, [])

    def send(self, msg: can.Message):
        """
        Send the given message to the bus
        :param msg: The message to send to the bus
        """
        self.bus_send.send(msg)

    def listen(self, listener: can.Listener):
        """
        Add the given listener to the list of bus listeners.
        :param listener: The listener to add
        """
        self.notifier.add_listener(listener)

    def remove_listener(self, listener: can.Listener):
        """
        Removes the given listener from the list of bus listeners.
        :param listener: The listener to remove
        """
        self.notifier.remove_listener(listener)

    def show_bus(self):
        """
        Prints to console all the traffic on the bus
        """
        print_listener = can.Printer()
        self.listen(print_listener)

    def shutdown(self):
        """
        Close the bus
        """
        self.bus_recv.shutdown()
        self.bus_send.shutdown()
