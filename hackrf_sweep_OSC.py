import os
import subprocess
from pythonosc import udp_client
import time
import threading
import numpy as np

# Update the DYLD_LIBRARY_PATH environment variable to include the directory containing libhackrf.0.dylib
os.environ['DYLD_LIBRARY_PATH'] = f"{os.environ.get('DYLD_LIBRARY_PATH', '')}:/opt/homebrew/lib"

# Global flag to control thread execution
keep_running = True

# Global UDP client
client = udp_client.SimpleUDPClient('127.0.0.1', 57120)

def run_hackrf_sweep(f_start, f_stop, width=10000000):
    command = f'hackrf_sweep -f {f_start}:{f_stop} -w {width}'
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    return process

def parse_hackrf_output(process):
    while True:
        line = process.stdout.readline().decode('utf-8')
        if not line:
            break
        # Parse the line into an array
        parsed_data = line.strip().split(',')
        # Remove whitespace and convert to number (when possible)
        cleaned_data = []
        for item in parsed_data:
            item = item.strip()
            try:
                cleaned_data.append(float(item) if '.' in item else int(item))
            except ValueError:
                cleaned_data.append(item)
        yield cleaned_data  # Use yield to create a generator
        time.sleep(0.5)

def scan_networks():
    while True:
        # Execute the airport -s command and capture its output
        result = subprocess.run(
            ["/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport", "-s"],
            text=True,
            capture_output=True
        )
        output = result.stdout.strip().split('\n')[1:]  # Skip the header line

        # Split each line of output into an array of strings
        networks = [line.split() for line in output]
        
        yield networks  # Use yield to create a generator


def send_osc_message(msg_name, data, port):
    # Ensure data is a list
    data = [data] if not isinstance(data, list) else data
    # Flatten the list and convert all numbers to float
    flat_data = [float(item) if isinstance(item, (int, float)) else item for sublist in data for item in (sublist if isinstance(sublist, list) else [sublist])]
    # Send each item as a separate message
    for item in flat_data:
        client.send_message(msg_name, item)




def process_hackrf():
    # Start the hackrf_sweep process at channel 7 (2431 MHz)
    hackrf_process = run_hackrf_sweep(2431, 2453, 500000)  # Frequency in MHz
    for data in parse_hackrf_output(hackrf_process):
        if not keep_running:
            break
        print(data)
        low_hz = data[2] / 1e8
        #print(low_hz)
        high_hz = data[3] / 1e5
        #print(high_hz)
        num_steps = 10
        frequencies = np.logspace(np.log10(low_hz), np.log10(high_hz), num_steps + 1)
        #step_size = (high_hz - low_hz) / num_steps
        #frequencies = [low_hz + i * step_size for i in range(num_steps + 1)]
        for i, freq in enumerate(frequencies, start=1):
            freq = round(freq, 3)
            send_osc_message(f'/sweep/{i}', [freq], 57120)
            #print(f'Sending frequency message: /sweep/{i} with value {freq}')
            print(freq)

        db_values = data[6:17]
        for i, db in enumerate(db_values, start=12):
            db = round(db, 3)
            send_osc_message(f'/sweep/{i}', [db], 57120)
            #print(f'Sending dB message: /sweep/{i} with value {db}')



def process_networks():
    for data in scan_networks():
        if not keep_running:
            break
        print(data)
        transposed_data = list(zip(*data))
        for i, item in enumerate(transposed_data, start=1):
            # Convert tuple to list and send as a separate message
            send_osc_message(f'/networks/{i}', list(item), 57120)



if __name__ == '__main__':
    try:
        # Create threads for processing hackrf and scanning networks
        hackrf_thread = threading.Thread(target=process_hackrf)
        #networks_thread = threading.Thread(target=process_networks)

        # Start the threads
        hackrf_thread.start()
        #networks_thread.start()

        # Optionally, wait for both threads to complete
        hackrf_thread.join()
        #networks_thread.join()
    except KeyboardInterrupt:
        keep_running = False
        print("Terminating...")


