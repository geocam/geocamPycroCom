# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

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
