import subprocess
from pythonosc import udp_client


def scan_networks():
    # Execute the airport -s command and capture its output
    result = subprocess.run(
        ["/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport", "-s"],
        text=True,
        capture_output=True
    )
    output = result.stdout.strip().split('\n')[1:]  # Skip the header line

    # Split each line of output into an array of strings
    networks = [line.split() for line in output]
    return networks

def send_osc_message(msg_name, data):
    client = udp_client.SimpleUDPClient('127.0.0.1', 57120)  # Adjust IP and port as needed
    client.send_message(msg_name, data)

if __name__ == '__main__':
    networks = scan_networks()
    send_osc_message('/networks', networks)
    print(networks)