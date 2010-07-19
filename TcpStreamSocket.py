
import re, sys, os, socket, time, errno
import exceptions, traceback
import asynchat
from TcpBaseSocket import TcpBaseSocket

OPTS_KEYS = ('lineMode', 'connectHandler', 'lineHandler')

class TcpStreamSocket(TcpBaseSocket):
    def __init__(self, protocol, dispatcher, optsDict):
        asynchat.async_chat.__init__(self)
        TcpBaseSocket.__init__(self, protocol, dispatcher)
        for k in OPTS_KEYS:
            setattr(self, '_' + k, optsDict[k])
        assert self._lineMode # wrapper currently only supports line buffering
        self._sock = None

    def connect(self, serverPort):
        self.endpoint = '%s:%s' % (self._protocol._protoName, serverPort)
        host, portString = serverPort.split(':', 1)
        port = int(portString)
        self.startup()
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        #print 'connecting to server at %s' % self.endpoint
        asynchat.async_chat.connect(self, (host, port))

    def _initServerSocket(self, sock, addressInfo):
        self._sock = sock
        hostIp, hostPort = addressInfo
        try:
            hostName, _, _ = socket.gethostbyaddr(hostIp)
        except (socket.gaierror, socket.herror):
            # could not resolve hostname, just use ip address
            endpointHostName = hostIp
        else:
            endpointHostName = re.sub('\..*$', '', hostName)
        self.endpoint = '%s:%s:%s' % (self._protocol._protoName, endpointHostName, hostPort)
        print '\naccepting client connection from %s' % self.endpoint
        self.startup()
        
    def write(self, text):
        try:
            self.send(text)
        except socket.error:
            self.close()
            raise # let SharedScheduler handle the exception

    def startup(self):
        self._closed = False
        self._ibuffer = []
        if self._sock != None:
            self.set_socket(self._sock) # tell asyncore base class about the socket
        self.set_terminator('\n')

    def handle_connect(self):
        """What to do when we are connected."""
        if self._connectHandler:
            self._connectHandler(self)

    def handleLine(self, line):
        """What to do when we receive a line."""
        if self._lineHandler:
            self._lineHandler(self, line)

    def collect_incoming_data(self, data):
        self._ibuffer.append(data)

    def found_terminator(self):
        cmd = "".join(self._ibuffer)
        cmd = re.sub(r'\r$', '', cmd)
        self._ibuffer = []
        self.handleLine(cmd)

    def handle_error(self):
        errClass, errObject, errTB = sys.exc_info()[:3]
        if isinstance(errObject, socket.error) and errObject.args[0] == errno.ECONNREFUSED:
            print >>sys.stderr, 'connection to %s refused' % self.endpoint
            self.abort()
        else:
            self.abort()
            raise # pass the buck to SharedScheduler error handler
