import time
from ecus.base_ecu import BaseECU


class FakeECU(BaseECU):
    def _start_operations(self):
        # TODO: DEBUG
        message_id = 0x123

        # Start sending messages
        while True:
            print("sent")
            self.send_msg(message_id, 'salvatore')
            time.sleep(2)

    def __init__(self, bus):
        super().__init__(bus)
