
from ServiceFinder import ServiceFinder
from PubSubStreamSocket import PubSubStreamSocket
from PubSubListenSocket import PubSubListenSocket

class PubSubWrapper(ServiceFinder):
    def __init__(self, dispatcher, protoName):
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
