class AccessDenied(Exception):
    pass


class InvalidCredentials(Exception):
    pass


class RegistrationFailed(Exception):
    def __init__(self, message=None):
        self.message = message


class ServerAddressInUse(Exception):
    pass


class ServerInaccessible(Exception):
    pass


class AlreadyLoggedIn(Exception):
    pass


class Backend(object):
    def list_servers(self):
        return []

    def register(self, client):
        raise RegistrationFailed('Registration is not implemented.')

    def dynamic_password(self, email, password, server):
        raise NotImplementedError()

    def server_connect(self, server):
        raise AccessDenied()

    def server_connected(self, server):
        pass

    def server_disconnected(self, server):
        pass

    def client_connect(self, server, net, client):
        raise AccessDenied()

    def client_disconnected(self, server, client_id):
        pass
