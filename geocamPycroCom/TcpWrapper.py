# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

import sys
from TcpStreamSocket import TcpStreamSocket
from TcpListenSocket import TcpListenSocket
from WeakSet import WeakSet


class TcpWrapper:
    pollForMessages = False

    def __init__(self, dispatcher, protoName):
        self._dispatcher = dispatcher
        self._protoName = protoName
        self._sockets = WeakSet()

    def connect(self, dispatcher, serverPort, optsDict):
        sock = TcpStreamSocket(self, dispatcher, optsDict)
        sock.connect(serverPort)
        self._sockets.add(sock)
        return sock

    def listen(self, dispatcher, listenPort, optsDict):
        sock = TcpListenSocket(self, dispatcher, optsDict)
        sock.listen(listenPort)
        self._sockets.add(sock)
        return sock

    def close(self):
        for sock in self._sockets:
            try:
                sock.close()
            except:  # pylint: disable=W0702
                errClass, errObject, _errTB = sys.exc_info()[:3]
                print >> sys.stderr, ('could not close socket -- %s.%s: %s'
                                      % (errClass.__module__,
                                         errClass.__name__,
                                         str(errObject)))
