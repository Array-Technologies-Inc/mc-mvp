import os
import socket
import time
from os import environ
from time import sleep
import requests

from devices.common import messages_pb2

VMAGENT_URL = os.environ.get('VMAGENT_URL', "http://vmagent:8429/api/v1/import/prometheus")
GW_ID=os.environ.get('GW_ID', '1')

def send_telemetry_request(node: str):
    # Create a message object
    message = messages_pb2.TelemetryRequest()

    # Serialize the message to a byte string
    message_data = message.SerializeToString()

    # Create a socket object
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect to the server
    print(f'Connecting to {node}:6543')
    client_socket.connect((node, 6543))

    # Send the length of the message first
    client_socket.send(len(message_data).to_bytes(4, 'big'))

    # Send the actual message
    client_socket.send(message_data)

    # Wait for the response from the server
    response_length = client_socket.recv(4)
    if not response_length:
        return

    response_length = int.from_bytes(response_length, 'big')
    response_data = client_socket.recv(response_length)

    # Parse the response message
    response_message = messages_pb2.Telemetry()
    response_message.ParseFromString(response_data)

    # Print the response from the server
    print(f"Received from response from {node}:\n{response_message}")

    # Push the data to vmagent
    push_telemetry_to_vmagent(node, response_message)

    client_socket.close()

def push_telemetry_to_vmagent(node: str, response_message: messages_pb2.Telemetry):
    # Prepare metrics data in Prometheus format
    metrics = []
    gw_label = f'gw="GW-{GW_ID}"'
    job_label = f'job="gw{GW_ID}-scrape"'
    timestamp = time.time()

    # Current position
    metrics.append(f"telemetry_current_position{{node=\"{node}\", {gw_label}, {job_label}}} {response_message.current_position} {timestamp}")

    # Target position
    metrics.append(f"telemetry_target_position{{node=\"{node}\", {gw_label}, {job_label}}} {response_message.target_position} {timestamp}")

    # Battery state of charge (SOC)
    metrics.append(f"telemetry_battery_soc{{node=\"{node}\", {gw_label}, {job_label}}} {response_message.battery_soc} {timestamp}")

    # Charging status (0 for False, 1 for True)
    charging_value = 1 if response_message.charging else 0
    metrics.append(f"telemetry_charging{{node=\"{node}\", {gw_label}, {job_label}}} {charging_value} {timestamp}")

    # Mode (you can use a numeric value or string depending on your `TrackerMode` enum)
    metrics.append(f"telemetry_mode{{node=\"{node}\", {gw_label}, {job_label}}} {response_message.mode} {timestamp}")

    # Combine all the metrics into a single payload
    payload = "\n".join(metrics)

    # Send the data to vmagent
    headers = {
        'Content-Type': 'text/plain',
    }
    response = requests.post(VMAGENT_URL, headers=headers, data=payload)

    # Check for successful push
    if response.status_code > 200 and response.status_code < 400:
        print(f"[{response.status_code}]Successfully pushed telemetry data for {node} to vmagent.")
        print(payload)
    else:
        print(f"Failed to push telemetry data for {node} to vmagent. Status code: {response.status_code}, Response: {response.text}")

def main():
    NODES_COUNT = int(environ.get('NODES_COUNT'))
    nodes = [f'gw-{GW_ID}_tracker_{i}' for i in range(2, NODES_COUNT+1)]
    nodes.append('tracker')
    print(nodes)

    while True:
        for node in nodes:
            send_telemetry_request(node)
        sleep(10)

if __name__ == "__main__":
    main()
