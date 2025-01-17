import socket
import pickle

soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
port = 9999

class Network:
    def __init__(self):
        self.client = soc
        self.server = input("ip du serveur: ")
        self.port = port
        self.addr = (self.server, self.port)
        self.position = self.connect()

    def get_position(self):
        return self.position

    def connect(self):
        try:
            self.client.connect(self.addr)
            return pickle.loads(self.client.recv(2048))
        except:
            pass

    def send(self, data):
        try:
            self.client.send(pickle.dumps(data))
            return pickle.loads(self.client.recv(2048))
        except:
            print("\n\n----------- impossible de communiquer avec le serveur -----------\n\n")
