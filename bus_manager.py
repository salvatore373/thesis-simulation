import can


# The manager of the bus and all the connected ECUs
class BusManager:
    def __init__(self):
        # Initialize CAN Bus interface
        # can_interface = 'vcan0'  # virtual CAN Bus interface name
        # self.bus = can.interface.Bus(can_interface, bustype='socketcan')
        # TODO: consider using ThreadSafeBus
        self.bus_send = can.interface.Bus('test', interface='virtual')
        self.bus_recv = can.interface.Bus('test', interface='virtual')

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

    # TODO: keep or leave?
    # def register_ecu(self, id_min: int, id_max: int, ecu_id: string):
    #     """
    #     Tries to connect the ECU with the given IDs range to the bus.
    #     :param id_min: The minimum ID that the ECU will send to this bus
    #     :param id_max: The maximum ID that the ECU will send to this bus
    #     :param ecu_id: A unique name of the ECU to connect
    #
    #     :return: Whether the ECU has been registered or not
    #     """
    #     if self.id_ranges.get(ecu_id) is not None:
    #         # This ECU has already been registered
    #         return False
    #
    #     for range in self.id_ranges.values():
    #         if id_min >= range[0] and id_max <= range[1] or \
    #                 range[0] <= id_min <= range[1] or \
    #                 range[0] <= id_max <= range[1]:
    #             # The given range is included in an already registered range
    #             return False
    #
    #     self.id_ranges[ecu_id] = (id_min, id_max)
    #     return True

    def show_bus(self):
        """
        Prints to console all the traffic on the bus
        """
        # recvMsg = self.bus_recv.recv(timeout=5)
        # while recvMsg is not None:
        #     print(recvMsg)
        #     time.sleep(2)
        # else:
        #     print("None")
        #
        # print('stop')
        # Print msgs to the bus
        print_listener = can.Printer()
        self.listen(print_listener)

    def shutdown(self):
        """
        Close the bus
        """
        self.bus_recv.shutdown()
        self.bus_send.shutdown()
