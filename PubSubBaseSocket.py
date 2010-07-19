
class PubSubBaseSocket(object):
    def __init__(self, protocol, dispatcher):
        self._protocol = protocol
        self._dispatcher = dispatcher
        self._subscriptions = []

    def _subscribe(self, name, handler):
        self._protocol.subscribeWithHandler(name, handler)
        self._subscriptions.append(name)

    def close(self):
        for sub in self._subscriptions:
            self._dispatcher.unsubscribe(sub)
