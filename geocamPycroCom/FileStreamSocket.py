# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

import asyncore, sys, traceback, re

OPTS_KEYS = ('lineMode', 'connectHandler', 'lineHandler')

class FileStreamSocket(asyncore.file_dispatcher):
    """Implement part of async_chat but on top of asyncore.file_dispatcher instead
    of asyncore.dispatcher.  Also implement default handlers for simple line-oriented
    I/O."""
    def __init__(self, optsDict):
        for k in OPTS_KEYS:
            setattr(self, '_' + k, optsDict[k])
        assert self._lineMode # wrapper only currently supports line buffering

    def connect(self):
        inputFd = sys.stdin.fileno()
        self._outputFile = sys.stdout
        asyncore.file_dispatcher.__init__(self, inputFd)
        self.set_terminator('\n') # default, can change
        self._ibuffer = []

    def write(self, text):
        self._outputFile.write(text)

    def set_terminator(self, terminator):
        self._terminator = terminator

    def handle_connect(self):
        if self._connectHandler:
            self._connectHandler(self)

    def writable(self):
        return False

    def handle_read(self):
        remainingData = self.read(1024)
        while 1:
            remainingData = self._processUpToTerminator(remainingData)
            if not remainingData:
                break

    def _processUpToTerminator(self, data):
        termIndex = data.find(self._terminator)
        if termIndex == -1:
            self.collect_incoming_data(data)
            return ''
        else:
            self.collect_incoming_data(data[:termIndex])
            self.found_terminator()
            return data[(termIndex+1):]

    def collect_incoming_data(self, data):
        self._ibuffer.append(data)

    def found_terminator(self):
        line = ''.join(self._ibuffer)
        line = re.sub(r'\r$', '', line)
        self.handleLine(line)
        self._ibuffer = []
    
    def handle_error(self):
        raise # pass the buck to scheduler error handling

    def handleLine(self, line):
        if self._lineHandler != None:
            self._lineHandler(self, line)
