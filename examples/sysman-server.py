#!/usr/bin/env python

from twisted.internet import reactor
from twisted.internet.endpoints import serverFromString
from frn.sysman.protocol import ManagerServerFactory
from frn.sysman.backend import Backend, RegistrationFailed  # AccessDenied, InvalidCredentials, ServerAddressInUse, ServerInaccessible, AlreadyLoggedIn


class DummyBackend(Backend):
    def __init__(self):
        self.client_ids = 0

    def list_servers(self):
        return []

    def register(self, client):
        raise RegistrationFailed('Registration is not implemented.')

    def dynamic_password(self, email, password, server):
        raise NotImplementedError()

    def server_connect(self, server):
        # raise InvalidCredentials()
        pass

    def server_connected(self, server):
        print "[Server] %s:%d connected" % (server.host, server.port)

    def server_disconnected(self, server):
        print "[Server] %s:%d disconnected" % (server.host, server.port)

    def client_connect(self, server, net, client):
        # raise InvalidCredentials()
        self.client_ids += 1
        client_id = str(self.client_ids)
        print "[Client] #%s connected (%s)" % (client_id, client.email)
        return client_id

    def client_disconnected(self, server, client_id):
        print "[Client] #%s disconnected" % client_id
        pass

if __name__ == '__main__':
    serverFromString(reactor, "tcp:10025").listen(ManagerServerFactory(DummyBackend()))
    reactor.run()
