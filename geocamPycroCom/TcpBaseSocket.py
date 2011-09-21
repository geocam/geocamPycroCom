# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

# suppress warnings about unimplemented abstract methods
# pylint: disable=W0223

import asynchat


class TcpBaseSocket(asynchat.async_chat):
    def __init__(self, protocol, dispatcher):
        asynchat.async_chat.__init__(self)
        self._protocol = protocol
        self._dispatcher = dispatcher
        self._closed = False

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
        raise  # pass the buck to scheduler error handling
