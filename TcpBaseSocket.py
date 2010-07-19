
import asynchat
import sys

class TcpBaseSocket(asynchat.async_chat):
    def __init__(self, protocol, dispatcher):
        self._protocol = protocol
        self._dispatcher = dispatcher

    def abort(self):
        self.discard_buffers()
        if self.connected:
            self.close()
            print 'TcpBaseSocket: closed connection'
        self._closed = True

    def handle_close(self):
        self.abort()

    def handle_error(self):
        self.abort()
        raise # pass the buck to scheduler error handling
