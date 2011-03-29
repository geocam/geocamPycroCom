# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

import time
from PubSubBaseSocket import PubSubBaseSocket
from PubSubStreamSocket import PubSubStreamSocket

OPTS_KEYS = ('maxConnections', 'acceptHandler', 'createSocketHandler')

class PubSubListenSocket(PubSubBaseSocket):
    def __init__(self, protocol, dispatcher, optsDict):
        super(PubSubListenSocket, self).__init__(protocol, dispatcher)
        for k in OPTS_KEYS:
            setattr(self, '_'+k, optsDict[k])
        self._optsDict = optsDict

    def listen(self, listenEvent):
        self.endpoint = '%s:%s' % (self._protocol.protoName, listenEvent)
        self._listenEvent = listenEvent
        self._protocol.subscribeWithHandler(self._listenEvent, self._pingHandler)
        
    def _pingHandler(self, name, data):
        cmd, self._acceptSendEvent = data.split()
        assert cmd == 'ping'
        self.handleAccept()
        self._acceptSendEvent = None

    def accept(self):
        recvEvent = '%s-%f' % (self._listenEvent, time.time())
        self._protocol.publish(self._acceptSendEvent, 'ack ' + recvEvent)
        acceptSocket = self.handleCreateSocket()
        acceptSocket._initServerSocket(self._acceptSendEvent, recvEvent)
        return acceptSocket

    def handleAccept(self):
        """What to do when a client tries to connect."""
        # clientSock, clientEventName = self.accept()
        # ...
        if self._acceptHandler != None:
            self._acceptHandler(self)
        else:
            self.accept()

    def handleCreateSocket(self):
        """How to create a stream socket."""
        if self._createSocketHandler != None:
            return self._createSocketHandler(self)
        else:
            return PubSubStreamSocket(self._protocol, self._dispatcher, self._optsDict)
