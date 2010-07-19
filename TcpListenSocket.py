
import sys, os, socket
import asynchat
from TcpBaseSocket import TcpBaseSocket
from TcpStreamSocket import TcpStreamSocket
from printTraceback import printTraceback

OPTS_KEYS = ('maxConnections', 'acceptHandler', 'createSocketHandler')

class TcpListenSocket(TcpBaseSocket):
    def __init__(self, protocol, dispatcher, optsDict):
        TcpBaseSocket.__init__(self, protocol, dispatcher)
        for k in OPTS_KEYS:
            setattr(self, '_'+k, optsDict[k])
        self._optsDict = optsDict

    def listen(self, listenPort):
        self.endpoint = '%s:%s' % (self._protocol._protoName, listenPort)
        self._host, self._portString = listenPort.split(':', 1)
        self._port = int(self._portString)
        if self._host == 'localhost':
            self._host = ''
        asynchat.async_chat.__init__(self)
        print '%s: starting' % self.__class__.__name__
        sys.stdout.flush()
        print '  creating socket'
        sys.stdout.flush()
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        print '  binding to port %d (on loopback interface only!)' % self._port
        sys.stdout.flush()
        self.bind((self._host, self._port))
        print '  port bound, calling listen'
        sys.stdout.flush()
        asynchat.async_chat.listen(self, self._maxConnections)
        print '  called listen'
        sys.stdout.flush()
    
    def handle_accept(self):
        if self._acceptHandler != None:
            self._acceptHandler(self)
        else:
            rawSock, addressInfo = self.accept()
            streamSock = self.handleCreateSocket()
            streamSock._initServerSocket(rawSock, addressInfo)
            self._protocol._sockets.add(streamSock)
            return streamSock

    def handleCreateSocket(self):
        """How to create a stream socket."""
        if self._createSocketHandler != None:
            return self._createSocketHandler(self)
        else:
            return TcpStreamSocket(self._protocol, self._dispatcher, self._optsDict)
