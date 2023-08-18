
import socket
import ipywidgets as widgets
from IPython.display import display

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
    
class GqrxController:
    def __init__(self, host='localhost', port=7356):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))

    def send_command(self, cmd):
        self.sock.sendall((cmd + '\n').encode('utf-8'))
        response = self.sock.recv(1024).decode('utf-8').strip()
        return response

    def get_frequency(self):
        return float(self.send_command('f'))

    def set_frequency(self, freq):
        self.send_command(f'F {freq}')
        return self.get_frequency()

    def close(self):
        self.sock.close()

# Test the connection
test_gqrx_connection()

# Create an instance of GqrxController
gqrx = GqrxController()

# Define a function to update frequency
def update_frequency(freq):
    gqrx.set_frequency(freq)
    print(f"Frequency set to: {freq} Hz")

# Create a slider for frequency control
freq_slider = widgets.FloatSlider(
    value=gqrx.get_frequency(),
    min=2.3e9,  # 2.3 GHz
    max=2.5e9,  # 2.5 GHz
    step=1e6,  # 1 MHz step
    description='Frequency:',
    continuous_update=False
)
widgets.interactive(update_frequency, freq=freq_slider)


class MockGqrxTCPInterface:
    def __init__(self):
        # Simulated state variables
        self.frequency = 2.4e9  # 2.4 GHz
        self.gain = 50  # in dB
        self.signal_strength = -50  # in dBm

    def set_frequency(self, freq):
        self.frequency = freq
        # Simulate a change in signal strength based on frequency change
        self.signal_strength = -50 + (2.4e9 - freq) * 1e-8
        return self.frequency

    def get_frequency(self):
        return self.frequency

    def set_gain(self, gain):
        self.gain = gain
        # Simulate a change in signal strength based on gain change
        self.signal_strength += gain * 0.1
        return self.gain

    def get_signal_strength(self):
        return self.signal_strength



class MockGqrxTCPServer:
    def __init__(self, host='localhost', port=7356):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((host, port))
        self.server_socket.listen(1)
        self.mock_gqrx = MockGqrxTCPInterface()

    def start(self):
        print("Server started. Waiting for connections...")
        conn, addr = self.server_socket.accept()
        print(f"Connection from {addr}")
        
        while True:
            data = conn.recv(1024).decode('utf-8').strip()
            if not data:
                break
            if data == 'f':
                freq = self.mock_gqrx.get_frequency()
                conn.sendall(str(freq).encode('utf-8'))
            # Add more commands as needed

        conn.close()
        print("Connection closed.")

# Start the server
server = MockGqrxTCPServer()
server.start()





# Test the connection
gqrx = GqrxController()
current_freq = gqrx.get_frequency()
gqrx.close()
current_freq

class GqrxController:
    def __init__(self, host='localhost', port=7356):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))

    def send_command(self, cmd):
        self.sock.sendall((cmd + '\n').encode('utf-8'))
        response = self.sock.recv(1024).decode('utf-8').strip()
        return response

    def get_frequency(self):
        return float(self.send_command('f'))

    def set_frequency(self, freq):
        self.send_command(f'F {freq}')
        return self.get_frequency()

    def close(self):
        self.sock.close()

# Test the connection
gqrx = GqrxController()
current_freq = gqrx.get_frequency()
gqrx.close()
current_freq

# Create an instance of the mock interface
mock_gqrx = MockGqrxTCPInterface()

# Print the initial frequency and signal strength
print(f"Initial Frequency: {mock_gqrx.get_frequency()} Hz")
print(f"Initial Signal Strength: {mock_gqrx.get_signal_strength()} dBm")

# Change the frequency
new_freq = 2.45e9  # 2.45 GHz
mock_gqrx.set_frequency(new_freq)

# Print the updated frequency and signal strength
print(f"Updated Frequency: {mock_gqrx.get_frequency()} Hz")
print(f"Updated Signal Strength: {mock_gqrx.get_signal_strength()} dBm")

# Change the gain and observe the effect on signal strength
mock_gqrx.set_gain(60)  # Increase gain to 60 dB
print(f"Signal Strength after Gain Change: {mock_gqrx.get_signal_strength()} dBm")




