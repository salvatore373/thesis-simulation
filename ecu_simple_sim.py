# Simulates and ECU sending periodic messages on CAN bus

import can
import time

# Initialize CAN Bus interface
can_interface = 'vcan0'  # virtual CAN Bus interface name
bus = can.interface.Bus(can_interface, bustype='socketcan')


def send_periodic_msgs_ecu():
    # Define periodic message to send
    message_id = 0x123
    message_data = [0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF]
    message_period = 1.0  # message period in seconds

    # Start sending messages
    while True:
        message = can.Message(arbitration_id=message_id, data=message_data, is_extended_id=False)
        bus.send(message)
        time.sleep(message_period)


send_periodic_msgs_ecu()
