from twisted.protocols import basic
from frn.utils import parse_dict


class InvalidServerResponse(Exception):
    pass


class InvalidClientRequest(Exception):
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
        line = str(line).decode('utf8').encode('iso-8859-1')
        basic.LineReceiver.sendLine(self, line)


class CommandClient(LineReceiver):
    def __init__(self):
        self.commandQueue = []

    def sendCommand(self, command, before, handler):
        wasEmpty = not self.commandQueue
        self.commandQueue.append((command, before, handler))
        if wasEmpty:
            self.__sendNextCommand()

    def __sendNextCommand(self):
        if self.commandQueue:
            command, before, handler = self.commandQueue[0]
            if before:
                before()
            if command:
                self.sendLine(command)
            else:
                self.__finishCommand()

    def __finishCommand(self):
        if self.commandQueue:
            self.commandQueue.pop(0)
        self.__sendNextCommand()

    def decodedLineReceived(self, line):
        if self.commandQueue:
            if self.commandQueue[0][2](line) is not True:
                self.__finishCommand()
        else:
            raise InvalidServerResponse('Unexpected line receveived.')

    def finish(self):
        self.sendCommand(None, self.transport.loseConnection, None)


class CommandServer(LineReceiver):
    def __init__(self):
        self.commandHandlers = {}

    def registerCommand(self, name, handler, allowedArgs=False):
        self.commandHandlers[name] = (handler, allowedArgs)

    def deregisterCommands(self):
        self.commandHandlers = {}

    def decodedLineReceived(self, line):
        parts = line.split(':', 1)
        command = parts[0]
        if len(parts) == 1:
            args = {}
        elif parts[1] and parts[1][0] == '<':
            args = parse_dict(parts[1])
        else:
            args = {'_': parts[1]}
        if command in self.commandHandlers:
            handler, allowedArgs = self.commandHandlers[command]
            if allowedArgs is False:
                handler(args)
            else:
                handler({key: args[key] for key in allowedArgs})
        else:
            raise InvalidClientRequest('Unknown command "%s".' % command)
