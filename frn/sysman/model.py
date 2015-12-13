class Server():
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.nets = []

class Net():
    def __init__(self, name):
        self.name = name
        self.clients = []

class Client():
    def __init__(self, data):
        self.data = data

    @property
    def name(self):
        return self.data.get('ON')

    @property
    def country(self):
        return self.data.get('NN')

    @property
    def city(self):
        return self.data.get('CT')

    @property
    def band(self):
        return self.data.get('BC')

    @property
    def description(self):
        return self.data.get('DS')
