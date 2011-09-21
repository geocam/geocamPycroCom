# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

# disable bogus pylint warnings about trying to access or set missing class members
# pylint: disable=E1101,W0201

from ServiceFinder import ServiceFinder
from PubSubStreamSocket import PubSubStreamSocket
from PubSubListenSocket import PubSubListenSocket


class PubSubWrapper(ServiceFinder):
    def __init__(self, dispatcher, protoName):
        super(PubSubWrapper, self).__init__()
        self._dispatcher = dispatcher
        self._protoName = protoName
        self.setupProtocol()

    def subscribeWithHandler(self, event, handler):
        self._dispatcher.subscribe('%s:%s' % (self._protoName, event), handler)

    def connect(self, dispatcher, pingEvent, optsDict):
        sock = PubSubStreamSocket(self, dispatcher, optsDict)
        sock.connect(pingEvent)
        return sock

    def listen(self, dispatcher, listenEvent, optsDict):
        sock = PubSubListenSocket(self, dispatcher, optsDict)
        sock.listen(listenEvent)
        return sock
