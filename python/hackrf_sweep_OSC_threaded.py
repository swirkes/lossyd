import os
import subprocess
from pythonosc import udp_client
import time
import threading
import numpy as np
import random
import math
import queue

# Update the DYLD_LIBRARY_PATH environment variable to include the directory containing libhackrf.0.dylib
os.environ['DYLD_LIBRARY_PATH'] = f"{os.environ.get('DYLD_LIBRARY_PATH', '')}:/opt/homebrew/lib"

# Create a global queue for inter-thread communication
data_queue = queue.Queue()

# Global flag to control thread execution
keep_running = True

# Global hackrf_sweep process
#hackrf_process = None

# Global frequency range
global_start_freq = None
global_end_freq = None

# Global UDP client
client = udp_client.SimpleUDPClient('127.0.0.1', 57120)

def run_hackrf_sweep(f_start, f_stop, width=200000):
    command = f'hackrf_sweep -f {f_start}:{f_stop} -w {width}'
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print(f_start, f_stop, width)
    return process

def parse_hackrf_output():
    global hackrf_process
    while keep_running:
        try:
            line = hackrf_process.stdout.readline().decode('utf-8')
            if not line:
                # Check for any error message
                error_line = hackrf_process.stderr.readline().decode('utf-8')
                if error_line:
                    print(f"Error from hackrf_sweep: {error_line}")

                # Check if process is still running
                exit_code = hackrf_process.poll()
                if exit_code is not None:
                    raise RuntimeError(f"hackrf_sweep process terminated unexpectedly with exit code {exit_code}")
                    restart_hackrf_sweep()
            else:
                parsed_data = line.strip().split(',')
                cleaned_data = []
                for item in parsed_data:
                    item = item.strip()
                    try:
                        cleaned_data.append(float(item) if '.' in item else int(item))
                    except ValueError:
                        cleaned_data.append(item)
                data_queue.put(cleaned_data)
                #random_sleep = random.uniform(0.01, 0.08)
                #time.sleep(random_sleep)
        except Exception as e:
            print(f"Error occurred: {e}")
            break
    if hackrf_process and is_process_running(hackrf_process):
        hackrf_process.kill()

def send_osc_message(msg_name, data, port):
    # Ensure data is a list
    data = [data] if not isinstance(data, list) else data
    # Flatten the list and convert all numbers to float
    flat_data = [float(item) if isinstance(item, (int, float)) else item for sublist in data for item in (sublist if isinstance(sublist, list) else [sublist])]
    # Send each item as a separate message
    for item in flat_data:
        client.send_message(msg_name, item)

def process_data_item(data):
    if not keep_running:
        return
    # Assuming 'data' is the cleaned data from hackrf_sweep
    low_hz = data[2] / 1e8
    high_hz = data[3] / 1e5
    num_steps = 24
    frequencies = np.logspace(np.log10(low_hz), np.log10(high_hz), num_steps + 1)

    for i, freq in enumerate(frequencies, start=1):
        freq = round(freq, 3)
        send_osc_message(f'/sweep/{i}', [freq], 57120)
        print(f'Sending frequency message: /sweep/{i} with value {freq}')

    db_values = data[26:50]
    for i, db in enumerate(db_values, start=26):
        db = round(db, 3)
        send_osc_message(f'/sweep/{i}', [db], 57120)
        print(f'Sending dB message: /sweep/{i} with value {db}')

def wifi_channel_to_frequency(channel):
    if 1 <= channel <= 13:
        center_freq = 2412 + (channel - 1) * 5  # 5 MHz apart for channels 1-13
        start_freq = center_freq - 11
        end_freq = center_freq + 11
        return start_freq, end_freq
    elif channel == 14:
        return 2484 - 11, 2484 + 11  # Channel 14 is at 2484 MHz
    else:
        raise ValueError("Invalid Wi-Fi channel: Channels must be between 1 and 14")
    
def get_wifi_channel():
    while True:
        try:
            channel = int(input("Enter a Wi-Fi channel (1-14): "))
            if 1 <= channel <= 14:
                return channel
            else:
                print("Invalid Wi-Fi channel: Channels must be between 1 and 14")
                return get_wifi_channel()
        except ValueError:
            print("Invalid Wi-Fi channel: Channels must be an integer")
            return get_wifi_channel()

def process_data():
    while keep_running or not data_queue.empty():
        try:
            data = data_queue.get(timeout=1)  # Retrieve data from the queue
            # Insert your data processing logic here
            process_data_item(data)
        except queue.Empty:
            continue
        except Exception as e:
            print(f"Error occurred in process_data: {e}")

def is_process_running(process):
    return process.poll() is None

def restart_hackrf_sweep(f_start, f_stop, width=200000):
    global hackrf_process, global_start_freq, global_end_freq
    if hackrf_process is not None and is_process_running(hackrf_process):
        print("hackrf_sweep is already running.")
        return
    print("Restarting hackrf_sweep...")
    hackrf_process = run_hackrf_sweep(global_start_freq, global_end_freq, width=200000)

def main():
    global hackrf_process, global_start_freq, global_end_freq
    wifi_channel = get_wifi_channel()
    start_freq, end_freq = wifi_channel_to_frequency(wifi_channel)
    global_start_freq, global_end_freq = start_freq, end_freq
    hackrf_process = run_hackrf_sweep(start_freq, end_freq, width=200000)  # Frequency in MHz
    try:
        data_reading_thread = threading.Thread(target=parse_hackrf_output)  # Create a thread for reading data from hackrf_sweep
        data_processing_thread = threading.Thread(target=process_data)  # Create a thread for processing data
        
        # Start the threads
        data_reading_thread.start()
        data_processing_thread.start()

        # Optionally, wait for both threads to complete
        data_reading_thread.join()
        data_processing_thread.join()
    except KeyboardInterrupt:
        global keep_running
        keep_running = False
        print("Terminating...")


if __name__ == '__main__':
    main()
    


