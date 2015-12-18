class Server():
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.nets = []

    @classmethod
    def from_dict(cls, data):
        server = cls(data.get('SN'), int(data.get('PT')))
        server.version = data.get('VX')
        server.email = data.get('OW')
        server.password = data.get('PW')
        return server


class Net():
    def __init__(self, name):
        self.name = name
        self.clients = []


class Client():
    @classmethod
    def from_dict(cls, data):
        client = cls()
        client.name = data.get('ON')
        client.email = data.get('EA')
        client.password = data.get('PW')
        client.city = data.get('CT')
        client.country = data.get('NN')
        client.band = data.get('BC')
        client.description = data.get('DS')
        client.type = data.get('CL')
        client.ip = data.get('IP')
        return client
