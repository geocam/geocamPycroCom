
import re, platform, os, time
from PubSubBaseSocket import PubSubBaseSocket

OPTS_KEYS = ('lineMode', 'connectHandler', 'readHandler', 'lineHandler')

class PubSubStreamSocket(PubSubBaseSocket):
    def __init__(self, protocol, dispatcher, optsDict):
        super(PubSubStreamSocket, self).__init__(protocol, dispatcher)
        for k in OPTS_KEYS:
            setattr(self, '_'+k, optsDict[k])
        self._clear()

    def _getUniqueName(self):
        return '%s:%s-%d-%f' % (self._protocol._protoName, platform.node(), os.getpid(), time.time())

    def _clear(self):
        self._connected = False
        self._recvBuf = []

    def connect(self, pingEvent):
        self.endpoint = '%s:%s' % (self._protocol.protoName, pingEvent)
        self._pingEvent = pingEvent
        self._recvEvent = self._getUniqueName()
        self._subscribe(self._recvEvent, self._recvHandler)
        self._protocol.publish(self._pingEvent, 'ping ' + self._recvEvent)

    def _initServerSocket(self, sendEvent, recvEvent):
        self._sendEvent = sendEvent
        self._recvEvent = recvEvent
        self._subscribe(self._recvEvent, self._recvHandler)
        self._connected = True
        self.handleConnect()

    def _recvHandler(self, name, data):
        if self._connected:
            if self._lineMode:
                self._checkForNewLine(data)
            else:
                self._recvBuf.append(data)
                self.handleRead()
        else:
            cmd, self._sendEvent = data.split()
            assert cmd == 'ack'
            self._connected = True
            self.handleConnect()

    def _checkForNewLine(self, data):
        newLineIndex = data.find('\n')
        if newLineIndex == -1:
            self._recvBuf.append(data)
        else:
            line = ''.join(self._recvBuf) + data[:newLineIndex]
            line = re.sub('\r$', '', line)
            self._recvBuf = [data[(newLineIndex+1):]]
            self.handleLine(line)

    def read(self, numBytes=None):
        joined = ''.join(self._recvBuf)
        if numBytes != None and numBytes < len(joined):
            self._recvBuf = [joined[numBytes:]]
            return joined[:numBytes]
        else:
            self._recvBuf = []
            return joined

    def write(self, data):
        self._protocol.publish(self._sendEvent, data)

    push = write # emulate async_chat.push

    def close(self):
        self._clear()
        super(PubSubStreamSocket, self).close()

    def handleLine(self, line):
        """What to do when lineMode is True and we get a new line."""
        if self._lineHandler != None:
            self._lineHandler(self, line)

    def handleRead(self):
        """What to do when lineMode is False and there is data available for reading."""
        if self._readHandler != None:
            self._readHandler(self)

    def handleConnect(self):
        """What to do when there is a valid connection."""
        if self._connectHandler != None:
            self._connectHandler(self)
