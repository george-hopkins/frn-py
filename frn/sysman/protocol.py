import logging
from twisted.internet import reactor, protocol
from frn.common.protocol import CommandClient, CommandServer
from frn.sysman import VERSION
from frn.sysman.backend import AccessDenied, InvalidCredentials, RegistrationFailed, ServerAddressInUse, ServerInaccessible, AlreadyLoggedIn
from frn.sysman.model import Server, Net, Client
from frn.server import VERSION as SERVER_VERSION
from frn.client import VERSION as CLIENT_VERSION
from frn.utils import parse_dict, serialize_dict, generate_challenge, solve_challenge


SERVER_TIMEOUT = 6  # ping interval is 3 seconds


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


class ManagerServer(CommandServer):
    def __init__(self, backend):
        CommandServer.__init__(self)
        self.backend = backend
        self.logger = logging.getLogger(__name__)
        self.server = None
        self.serverTimeout = None
        self.registerCommand('SM', self.handleServerList)
        self.registerCommand('IG', self.handleRegister)
        self.registerCommand('DP', self.handleDynamicPassword)
        self.registerCommand('SC', self.handleServerConnect)

    def handleServerList(self):
        servers = self.backend.list_servers()
        self.sendLine(len(servers))
        for server in servers:
            self.sendLine(server.name)
            self.sendLine(len(server.nets))
            for net in server.nets:
                self.sendLine(net.name)
                self.sendLine(len(net.clients))
                for client in server.clients:
                    self.sendLine(self.serializeClient(client))

    def handleDynamicPassword(self, args):
        email = args.get('EA')
        password = args.get('PW')
        server = args.get('Sr')
        if email or password:
            self.sendLine('-')
            return
        try:
            dynamicPassword = self.backend.dynamic_password(email, password, server)
            self.sendLine(dynamicPassword)
        except (NotImplementedError, InvalidCredentials):
            self.sendLine('-')

    def handleRegister(self, args):
        client = Client.from_dict(args)
        try:
            self.backend.register(client)
            self.sendLine('OK')
        except RegistrationFailed as ex:
            self.sendLine(ex.message or 'NU')

    def handleServerConnect(self, args):
        server = Server.from_dict(args)
        result = -10
        challenge = ''
        if server.version != SERVER_VERSION:
            result = -6
        else:
            try:
                self.backend.server_connect(server)
                result = 0
            except InvalidCredentials:
                result = -4
            except ServerAddressInUse:
                result = -8
            except ServerInaccessible:
                result = -5
            except AlreadyLoggedIn:
                result = -9
            except AccessDenied:
                result = -7
        if result == 0:
            challenge = generate_challenge()
            passcode = solve_challenge(challenge)
            self.server = server
            self.deregisterCommands()
            self.registerCommand(str(passcode), self.handlePasscode)
        # 0: OK, -1: error, -2: busy, -3: communication error, -4: wrong credentials, -5: not accessible
        # -6: server version too old, -7: access denied, -8: address occupied, -9: same credentials online
        # -10...: unknown error
        self.sendLine(serialize_dict([
            ('SV', SERVER_VERSION),
            ('CV', CLIENT_VERSION),
            ('MC', VERSION),
            ('AL', result),
            ('KP', challenge),
        ]))

    def handlePasscode(self, args):
        self.deregisterCommands()
        self.backend.server_connected(self.server)
        self.resetServerTimeout()
        self.registerCommand('CC', self.handleClientConnect)
        self.registerCommand('CD', self.handleClientDisconnect)
        self.registerCommand('P', self.handlePing)

    def handleClientConnect(self, args):
        client = Client.from_dict(args)
        network = args.get('NT')
        try:
            id = self.backend.client_connect(self.server, network, client)
            self.sendLine(id)
        except InvalidCredentials:
            self.sendLine('WRONG')
        except AccessDenied:
            self.sendLine('BLOCK')

    def handleClientDisconnect(self, args):
        id = args.get('ID')
        self.backend.client_disconnected(self.server, id)
        self.sendLine('OK')

    def handlePing(self, args):
        self.resetServerTimeout()
        self.logger.debug('Ping')
        self.sendLine('F')

    def connectionLost(self, reason):
        if self.server:
            self.backend.server_disconnected(self.server)

    def onServerTimeout(self):
        self.transport.loseConnection()

    def resetServerTimeout(self):
        if self.serverTimeout:
            self.serverTimeout.cancel()
        self.serverTimeout = reactor.callLater(SERVER_TIMEOUT, self.onServerTimeout)

    def serializeClient(self, client):
        return serialize_dict([
            ('ON', client.name),
            ('BC', client.band),
            ('DS', client.description),
            ('NN', client.country),
            ('CT', client.city),
        ])


class ManagerServerFactory(protocol.Factory):
    def __init__(self, backend):
        self.backend = backend

    def buildProtocol(self, addr):
        return ManagerServer(self.backend)
