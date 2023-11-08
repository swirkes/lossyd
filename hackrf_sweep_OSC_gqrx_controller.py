import os
import subprocess
from pythonosc import udp_client
import time
import threading
import socket
import ipywidgets as widgets
from IPython.display import display

# Update the DYLD_LIBRARY_PATH environment variable to include the directory containing libhackrf.0.dylib
os.environ['DYLD_LIBRARY_PATH'] = f"{os.environ.get('DYLD_LIBRARY_PATH', '')}:/opt/homebrew/lib"

# Global flag to control thread execution
keep_running = True

# Global UDP client
client = udp_client.SimpleUDPClient('127.0.0.1', 57120)

def test_gqrx_connection(host='localhost', port=7356):
    try:
        # Create a socket and connect to Gqrx
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))

        # Send a command to get the frequency
        s.sendall(b'f\n')
        frequency = s.recv(1024).decode('utf-8').strip()

        s.close()
        return f'Connected successfully! Current frequency: {frequency} Hz'
    except Exception as e:
        return f'Failed to connect: {e}'

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
        time.sleep(0.25)

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
    hackrf_process = run_hackrf_sweep(2440, 2550, 500000)  # Frequency in MHz
    for data in parse_hackrf_output(hackrf_process):
        if not keep_running:
            break
        print(data)
        low_hz = data[2] / 1e7
        high_hz = data[3] / 1e6
        num_steps = 4
        step_size = (high_hz - low_hz) / num_steps
        frequencies = [low_hz + i * step_size for i in range(num_steps + 1)]
        for i, freq in enumerate(frequencies, start=1):
            freq = round(freq, 3)
            send_osc_message(f'/sweep/{i}', [freq], 57120)
            #print(freq)

        db_values = data[6:11]
        for i, db in enumerate(db_values, start=6):
            db = round(db, 3)
            send_osc_message(f'/sweep/{i}', [db], 57120)
            #print(db)



def process_networks():
    for data in scan_networks():
        if not keep_running:
            break
        print(data)
        transposed_data = list(zip(*data))
        for i, item in enumerate(transposed_data, start=1):
            # Convert tuple to list and send as a separate message
            send_osc_message(f'/networks/{i}', list(item), 57120)

    
class GqrxController:
    def __init__(self, host='localhost', port=7356):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))

    def send_command(self, cmd):
        if self.sock.fileno() == -1:
            raise OSError('Socket is closed')
        
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        self.sock.sendall((cmd + '\n').encode('utf-8'))
        response = self.sock.recv(1024).decode('utf-8').strip()
        return response
    
    def start_dsp(self):
        return self.send_command('U DSP 1')
    
    def stop_dsp(self):
        return self.send_command('U DSP 0')

    def get_frequency(self):
        return float(self.send_command('f'))

    def set_frequency(self, freq):
        self.send_command(f'F {freq}')
        return self.get_frequency()

    def close(self):
        self.sock.close()

# Define a function to update frequency
def update_frequency(freq):
    gqrx.set_frequency(freq)
    print(f"Frequency set to: {freq} Hz")

def scan_channel_7(gqrx, start_freq, end_freq, step_size, scan_delay):
    try:
        # Start DSP processing
        gqrx.start_dsp()
        print("DSP processing started.")

        freq = start_freq
        while freq <= end_freq and keep_running:
            gqrx.set_frequency(freq)
            # Add your processing logic here
            time.sleep(scan_delay)
            freq += step_size

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Stop DSP processing
        gqrx.stop_dsp()
        print("DSP processing stopped.")



if __name__ == '__main__':
    # Test the connection to Gqrx
    print(test_gqrx_connection())

    # Create a GqrxController instance
    gqrx = GqrxController()

    #Set up frequency range to scan
    start_freq = 2.431e9  # 2.434 GHz
    end_freq = 2.453e9  # 2.454 GHz
    step_size = 1e4  # 1 kHz steps
    scan_delay = 0.05  # half-second delay between steps

    try:
        # Create threads for processing hackrf and scanning networks
        #hackrf_thread = threading.Thread(target=process_hackrf)
        #networks_thread = threading.Thread(target=process_networks)
        scan_channel_7_thread = threading.Thread(target=scan_channel_7, 
            args=(gqrx, start_freq, end_freq, step_size, scan_delay)
        )

        # Start the threads
        #hackrf_thread.start()
        #networks_thread.start()
        scan_channel_7_thread.start()
        print("Channel 7 scanning started...")

        # Optionally, wait for both threads to complete
        #hackrf_thread.join()
        #networks_thread.join()
        scan_channel_7_thread.join()
    except KeyboardInterrupt:
        keep_running = False
        print("Terminating...")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        gqrx.close()
        print("Gqrx controller closed.")


