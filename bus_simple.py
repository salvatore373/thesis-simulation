# Simulates and ECU sending periodic messages on CAN bus

import can
import time

# Initialize CAN Bus interface
can_interface = 'vcan0'  # virtual CAN Bus interface name
bus = can.interface.Bus(can_interface, bustype='socketcan')

recvMsg = bus.recv(timeout=None)
while recvMsg is not None:
    print(recvMsg)
    time.sleep(2)
else:
    print("None")

print('4')
