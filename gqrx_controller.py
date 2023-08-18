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
