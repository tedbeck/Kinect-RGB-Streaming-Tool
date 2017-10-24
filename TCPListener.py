import socket

class TCPListener():
    # creates local socket to receive data from C# server for XBox 360 Kinect

    def __init__(self):
        self.TCP_IP = '127.0.0.1'
        self.TCP_PORT = 5000
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.TCP_IP, self.TCP_PORT))

    def receive_bytes(self):
        # push data from socket
        return self.sock.recv(100)

