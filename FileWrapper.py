
from FileStreamSocket import FileStreamSocket

class FileWrapper:
    pollForMessages = False

    def __init__(self, dispatcher, protoName):
        self._dispatcher = dispatcher
        self._protoName = protoName

    def connect(self, dispatcher, unusedAddr, optsDict):
        sock = FileStreamSocket(optsDict)
        assert unusedAddr == ''
        sock.connect()
        return sock
