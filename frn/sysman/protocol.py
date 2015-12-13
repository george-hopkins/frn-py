from twisted.internet import reactor, protocol
from frn.common.protocol import LineReceiver, IllegalServerResponse
from frn.sysman.model import Server, Net, Client
import frn.utils

class ManagerClient(LineReceiver):
    def __init__(self):
        self._commandQueue = []

    def sendCommand(self, command, before, handler):
        wasEmpty = not self._commandQueue
        self._commandQueue.append((command, before, handler))
        if wasEmpty:
            self._sendNextCommand()

    def _sendNextCommand(self):
        if self._commandQueue:
            command, before, handler = self._commandQueue[0]
            if before:
                before()
            if command:
                self.sendLine(command)

    def _commandEnded(self):
        if self._commandQueue:
            self._commandQueue.pop(0)
        self._sendNextCommand()

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
            host, port = line.split(' - Port: ', 2)
            self._currentServer = Server(host, int(port))
        elif self._remainingNets is None:
            self._remainingNets = int(line)
        elif self._currentNet is None:
            self._currentNet = Net(line)
        elif self._remainingClients is None:
            self._remainingClients = int(line)
        else:
            client = Client(frn.utils.parse_arguments(line))
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
            self._commandEnded()

    def decodedLineReceived(self, line):
        if self._commandQueue:
            self._commandQueue[0][2](line)
        else:
            raise IllegalServerResponse('Unexpected line receveived.')

    def quit(self):
        self.sendCommand(None, self.transport.loseConnection, None)

class ManagerClientFactory(protocol.Factory):
    def buildProtocol(self, addr):
        return ManagerClient(self)
