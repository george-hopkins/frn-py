from twisted.protocols import basic

class IllegalServerResponse(Exception):
    pass

class LineReceiver(basic.LineReceiver):
    def decodedLineReceived(self, line):
        """Override this for when each line is received."""
        raise NotImplementedError

    def lineReceived(self, line):
        """Decode a received line."""
        line = line.decode('iso-8859-1').encode('utf8')
        self.decodedLineReceived(line)

    def sendLine(self, line):
        """Send a line to the other end of the connection."""
        line = line.decode('utf8').encode('iso-8859-1')
        basic.LineReceiver.sendLine(self, line)
