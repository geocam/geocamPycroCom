
class ComError(Exception):
    pass

class DisconnectedError(ComError):
    pass

class EventAlreadyBoundError(ComError):
    pass

class BadEndpointError(ComError):
    pass
