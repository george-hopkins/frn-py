#!/usr/bin/env python

from twisted.internet import reactor
from twisted.internet.endpoints import connectProtocol, TCP4ClientEndpoint
from frn.sysman.protocol import ManagerClient


class DumpingManagerClient(ManagerClient):
    def connectionMade(self):
        self.updateServers()
        self.finish()

    def connectionLost(self, reason):
        reactor.stop()

    def serversUpdated(self, servers):
        for server in servers:
            print "%s:%d" % (server.host, server.port)
            for net in server.nets:
                print "  %s (%d clients)" % (net.name, len(net.clients))
                for client in net.clients:
                    print "    %s (%s)" % (client.name, client.country)


if __name__ == '__main__':
    destination = TCP4ClientEndpoint(reactor, 'sysman.freeradionetwork.eu', 10025)
    connectProtocol(destination, DumpingManagerClient())
    reactor.run()
