from twisted.internet import reactor, protocol
from frn.common.protocol import CommandClient
from frn.sysman.model import Server, Net, Client
from frn.utils import parse_dict, serialize_dict


class ManagerClient(CommandClient):
    def __init__(self):
        CommandClient.__init__(self)

    def updateServers(self):
        self.sendCommand('SM', self._beforeUpdateServers, self._handleUpdateServers)

    def serversUpdated(self, servers):
        pass

    def _beforeUpdateServers(self):
        self._servers = []
        self._remainingServers = None
        self._currentServer = None
        self._remainingNets = None
        self._currentNet = None
        self._remainingClients = None

    def _handleUpdateServers(self, line):
        if self._remainingServers is None:
            self._remainingServers = int(line)
        elif not self._currentServer:
            host, port = line.split(' - Port: ', 1)
            self._currentServer = Server(host, int(port))
        elif self._remainingNets is None:
            self._remainingNets = int(line)
        elif self._currentNet is None:
            self._currentNet = Net(line)
        elif self._remainingClients is None:
            self._remainingClients = int(line)
        else:
            client = Client.from_dict(parse_dict(line))
            self._currentNet.clients.append(client)
            self._remainingClients -= 1

        if self._currentNet and self._remainingClients == 0:
            self._currentServer.nets.append(self._currentNet)
            self._currentNet = None
            self._remainingClients = None
            self._remainingNets -= 1

        if self._currentServer and self._remainingNets == 0:
            self._servers.append(self._currentServer)
            self._currentServer = None
            self._remainingNets = None
            self._remainingServers -= 1

        if self._remainingServers == 0:
            self.serversUpdated(self._servers)
            return False
        return True  # expect more data


class ManagerClientFactory(protocol.Factory):
    def buildProtocol(self, addr):
        return ManagerClient()
