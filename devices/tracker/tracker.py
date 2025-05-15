import socket
import threading
import time
from enum import Enum
from dataclasses import dataclass, field
import random

from devices.common import messages_pb2

BATTERY_THRESHOLD = 20  # %
UPDATE_INTERVAL = 10  # Seconds
ANGULAR_SPEED = 0.2  # Degrees per second
MOVEMENT_CYCLE_PERIOD = 60  # Seconds


class TrackerMode(Enum):
    AUTO = 0
    OFF = 1


@dataclass(init=True, repr=True)
class Data:
    mac: str = field(
        default_factory=lambda: ":".join(
            ["{:02x}".format(random.randint(0, 255)) for _ in range(6)]
        )
    )
    sw_version: str = field(
        default_factory=lambda: random.choice(["1.1.0", "1.2.0", "1.2.3"])
    )
    current_position: float = field(default_factory=lambda: random.randint(-55, 55))
    target_position: float = field(default=55)
    battery_soc: float = field(default_factory=lambda: random.randint(0, 100))
    mode: TrackerMode = field(default=TrackerMode.AUTO)
    charging: bool = field(default=False)


class Tracker:
    def __init__(self):
        self.data = Data()
        self.lock = threading.Lock()
        self.last_update = time.time()

    def print_state(self):
        print(
            f"MAC: {self.data.mac} | Version :{self.data.sw_version} | Mode: {self.data.mode} || "
            f"Position: Current={self.data.current_position:.2f} Expected={self.data.target_position:.2f} || "
            f"SOC: {self.data.battery_soc:.2f} | Charging: {self.data.charging}"
        )

    def _move(self):
        distance_to_target = abs(self.data.target_position - self.data.current_position)
        elapsed = time.time() - self.last_update
        if distance_to_target > 0.0:
            self.last_update = time.time()
            move = min(
                ANGULAR_SPEED * elapsed, distance_to_target
            )  # Move by 0.2 degrees/s or the remaining distance
            self.data.current_position += (
                move
                if self.data.target_position > self.data.current_position
                else -move
            )
            self.data.battery_soc -= min(self.data.battery_soc, move * 1.0)
            print(f"Moving {move:.2f} degrees")
        else:
            print("Setpoint reached")
            if elapsed > MOVEMENT_CYCLE_PERIOD:
                self.data.target_position = -1 * self.data.target_position
                print("!! Updated setpoint !!")

    def update(self):
        """
        Update function that simulates device movement and updates battery SOC.
        The update occurs every 20 seconds, and the device rotates towards its target position.
        """
        time.time()
        while True:
            with self.lock:
                # Only update if the mode is AUTO and the battery is sufficient
                if self.data.battery_soc >= min(BATTERY_THRESHOLD * 2.5, 90):
                    self.data.charging = False

                if self.data.mode == TrackerMode.AUTO:
                    if not self.data.charging:
                        # Check if the battery is sufficient to move
                        if self.data.battery_soc >= BATTERY_THRESHOLD:
                            self._move()
                            self.print_state()
                        else:
                            self.data.charging = True
                            print(f"Battery too low to move")
                            self.print_state()
                    else:
                        self.data.battery_soc = min(100.0, self.data.battery_soc + 4.0)
                        print(f"Tracker controller on charging mode")
                        self.print_state()
                else:
                    print(f"Tracker is in {self.data.mode.name} mode. No movement.")
                    self.print_state()

            # Sleep for UPDATE_INTERVAL seconds before updating again
            time.sleep(UPDATE_INTERVAL)

    def start_update_loop(self):
        """
        Start the update loop in a separate thread so it runs continuously.
        """
        update_thread = threading.Thread(target=self.update)
        update_thread.daemon = (
            True  # Daemonize the thread so it closes when the main program ends
        )
        update_thread.start()

    def _handle_client(self, client_socket):
        # Receive the length of the incoming message (4 bytes)
        message_length = client_socket.recv(4)
        if not message_length:
            return

        # Convert to integer (this is the length of the protobuf message)
        message_length = int.from_bytes(message_length, "big")

        # Receive the actual message
        message_data = client_socket.recv(message_length)

        # Decode the protobuf message
        message = messages_pb2.TelemetryRequest()
        message.ParseFromString(message_data)

        # Print the received message
        print(f"Received telemetry request")

        # Send a response back
        response = messages_pb2.Telemetry(
            mac=self.data.mac,
            target_position=self.data.target_position,
            current_position=self.data.current_position,
            battery_soc=self.data.battery_soc,
            charging=self.data.charging,
            mode=messages_pb2.TrackerMode.OFF if self.data.mode == TrackerMode.OFF else messages_pb2.TrackerMode.AUTO
        )
        response_data = response.SerializeToString()

        # Send back the length of the response first
        client_socket.send(len(response_data).to_bytes(4, "big"))

        # Send the actual response
        client_socket.send(response_data)
        client_socket.close()

    def start_server(self):
        # Server setup
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(("0.0.0.0", 6543))
        server_socket.listen(5)

        print("Server is listening on port 6543...")

        while True:
            # Wait for a client to connect
            client_socket, addr = server_socket.accept()
            print(f"Connection from {addr}")

            # Handle the client connection
            self._handle_client(client_socket)

def main():
    tracker = Tracker()
    # Start the update loop in the background
    tracker.start_update_loop()
    tracker.start_server()


if __name__ == "__main__":
  main()