import os
import subprocess
from pythonosc import udp_client
import time
import threading
import numpy as np
import random
import math

# Update the DYLD_LIBRARY_PATH environment variable to include the directory containing libhackrf.0.dylib
os.environ['DYLD_LIBRARY_PATH'] = f"{os.environ.get('DYLD_LIBRARY_PATH', '')}:/opt/homebrew/lib"

# Global flag to control thread execution
keep_running = True

# Global UDP client
client = udp_client.SimpleUDPClient('127.0.0.1', 57120)

def run_hackrf_sweep(f_start, f_stop, width=200000):
    command = f'hackrf_sweep -f {f_start}:{f_stop} -w {width}'
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print(f_start, f_stop, width)
    return process

# def parse_hackrf_output(process):
#     while True:
#         line = process.stdout.readline().decode('utf-8')
#         if not line:
#             break
#         # Parse the line into an array
#         parsed_data = line.strip().split(',')
#         # Remove whitespace and convert to number (when possible)
#         cleaned_data = []
#         for item in parsed_data:
#             item = item.strip()
#             try:
#                 cleaned_data.append(float(item) if '.' in item else int(item))
#             except ValueError:
#                 cleaned_data.append(item)
#         yield cleaned_data  # Use yield to create a generator
#         random_sleep = random.uniform(0.01, 0.08)
#         time.sleep(random_sleep)

# def parse_hackrf_output(process):
#     while True:
#         # Non-blocking read from the process output
#         try:
#             line = process.stdout.readline().decode('utf-8')
#             if not line:
#                 # Check if process is still running
#                 if process.poll() is not None:
#                     exit_code = process.poll()
#                     if exit_code is not None:
#                         raise RuntimeError(f"hackrf_sweep process terminated unexpectedly with exit code {exit_code}")
#             else:
#                 parsed_data = line.strip().split(',')
#                 # Remove whitespace and convert to number (when possible)
#                 cleaned_data = []
#                 for item in parsed_data:
#                     item = item.strip()
#                     try:
#                         cleaned_data.append(float(item) if '.' in item else int(item))
#                     except ValueError:
#                         cleaned_data.append(item)
#                 yield cleaned_data  # Use yield to create a generator
#                 random_sleep = random.uniform(0.01, 0.08)
#                 time.sleep(random_sleep)
#                 pass
#         except Exception as e:
#             print(f"Error occurred: {e}")
#             break

def parse_hackrf_output(process):
    while True:
        try:
            line = process.stdout.readline().decode('utf-8')
            if not line:
                # Check for any error message
                error_line = process.stderr.readline().decode('utf-8')
                if error_line:
                    print(f"Error from hackrf_sweep: {error_line}")

                # Check if process is still running
                exit_code = process.poll()
                if exit_code is not None:
                    raise RuntimeError(f"hackrf_sweep process terminated unexpectedly with exit code {exit_code}")
            else:
                parsed_data = line.strip().split(',')
                cleaned_data = []
                for item in parsed_data:
                    item = item.strip()
                    try:
                        cleaned_data.append(float(item) if '.' in item else int(item))
                    except ValueError:
                        cleaned_data.append(item)
                yield cleaned_data  # Use yield to create a generator
                random_sleep = random.uniform(0.01, 0.08)
                time.sleep(random_sleep)
        except Exception as e:
            print(f"Error occurred: {e}")
            break



def send_osc_message(msg_name, data, port):
    # Ensure data is a list
    data = [data] if not isinstance(data, list) else data
    # Flatten the list and convert all numbers to float
    flat_data = [float(item) if isinstance(item, (int, float)) else item for sublist in data for item in (sublist if isinstance(sublist, list) else [sublist])]
    # Send each item as a separate message
    for item in flat_data:
        client.send_message(msg_name, item)

def process_hackrf(wifi_channel, bin_width=200000):
    start_freq, end_freq = wifi_channel_to_frequency(wifi_channel)
    hackrf_process = run_hackrf_sweep(start_freq, end_freq, bin_width)  # Frequency in MHz
    for data in parse_hackrf_output(hackrf_process):
        if not keep_running:
            break
        #print(data)
        low_hz = data[2] / 1e8
        #print(low_hz)
        high_hz = data[3] / 1e5
        #print(high_hz)
        num_steps = 24
        frequencies = np.logspace(np.log10(low_hz), np.log10(high_hz), num_steps + 1)
        #step_size = (high_hz - low_hz) / num_steps
        #frequencies = [low_hz + i * step_size for i in range(num_steps + 1)]
        for i, freq in enumerate(frequencies, start=1):
            #freq = 2595 * math.log10(1 + freq / 700.0) # Convert to mel scale
            freq = round(freq, 3)
            send_osc_message(f'/sweep/{i}', [freq], 57120)
            print(f'Sending frequency message: /sweep/{i} with value {freq}')
            #print(freq)

        db_values = data[6:31]
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

def main():
    wifi_channel = get_wifi_channel()
    try:
        # Create threads for processing hackrf and scanning networks
        hackrf_thread = threading.Thread(target=process_hackrf, args=(wifi_channel,))
       
        # Start the threads
        hackrf_thread.start()
       
        # Optionally, wait for both threads to complete
        hackrf_thread.join()
    except KeyboardInterrupt:
        keep_running = False
        print("Terminating...")


if __name__ == '__main__':
    main()
    


