import socket

class GqrxController:
    """Class to interact with Gqrx using TCP commands."""
    
    def __init__(self, host='localhost', port=7356):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect()

    def connect(self):
        """Establish a connection to the Gqrx server."""
        try:
            self.sock.connect((self.host, self.port))
        except Exception as e:
            print(f"Error connecting: {e}")
            self.sock = None

    def send_command(self, cmd):
        """Send a command to the Gqrx server and return the response."""
        if self.sock:
            try:
                self.sock.sendall((cmd + '\n').encode('utf-8'))
                response = self.sock.recv(1024).decode('utf-8').strip()
                return response
            except Exception as e:
                print(f"Error sending command: {e}")
                return None
        else:
            print("Not connected.")
            return None

    def get_frequency(self):
        """Get the current frequency from Gqrx."""
        return float(self.send_command('f'))

    def set_frequency(self, freq):
        """Set the frequency in Gqrx."""
        self.send_command(f'F {freq}')
        return self.get_frequency()

    def close(self):
        """Close the connection to the Gqrx server."""
        if self.sock:
            self.sock.close()

