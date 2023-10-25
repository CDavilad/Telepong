# protocol.py
import json
import socket
from constants import SERVER_ADDRESS, PORT, RECV_BUFFER_SIZE, ENCODING_FORMAT

class SocketProtocol:
    
    def __init__(self, server_address=SERVER_ADDRESS, port=PORT):
        self.server_address = server_address
        self.port = port
        self.sock = None

    def connect(self):
        if self.sock is None:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.server_address, self.port))
    
    def close(self):
        if self.sock:
            self.sock.close()
            self.sock = None

    def send(self, message):
        if self.sock:
            self.sock.sendall(message.encode(ENCODING_FORMAT))
        else:
            raise Exception("Socket not connected")

    def receive(self):
        if self.sock:
            data = self.sock.recv(RECV_BUFFER_SIZE)
            return data.decode(ENCODING_FORMAT)
        else:
            raise Exception("Socket not connected")
        
    def get_local_address(self):
        if self.sock:
            return self.sock.getsockname()
        else:
            return None
