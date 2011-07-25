import json
import time
import uuid
import struct
import socket
import asyncore
from select import select
import logging
from threading import Thread
import re
import hashlib
from geocamUtil.JsonRpc2Validation import JsonRpc2Keys
from geocamUtil.JsonRpc2Validation import JsonRpc2Validator
from geocamUtil.JsonRpc2Validation import JsonRpc2ComplianceException

class Resource(Thread):
    def __init__(self, server, rname):
        Thread.__init__(self)
        self.server = server
        self.rname = rname
        self.running = True

    def receive(self, data):
        raise NotImplementedError( "Must be implemented in subclasses" )

    def send(self, data):
        self.server.send(self.rname, data)

    def stop(self):
        self.running = False


class JsonRpc2Resource(Resource):
    def __init__(self, server, rname):
        Resource.__init__(self, server, rname)
        self.validator = JsonRpc2Validator()

    def genId(self):
        return unicode(uuid.uuid4())

    def validate(self, data):
        self.validator.validate(data)

    def sendRequest(self, method, paramObj={}):
        req = {JsonRpc2Keys.KEY_JSONRPC : '2.0',
               JsonRpc2Keys.KEY_METHOD : method,
               JsonRpc2Keys.KEY_ID : self.genId()
               }
        if paramObj:
            req[JsonRpc2Keys.KEY_PARAMS] = paramObj

        try:
            reqStr = json.dumps(req)
            self.validate(reqStr)
            Resource.send(self, reqStr)
        except ValueError as valerr:
            raise JsonRpc2ComplianceException( "Could not parse data into json object: %s"%str(valerr) )

    def sendNotification(self, method, paramObj={}):
        req = {JsonRpc2Keys.KEY_JSONRPC: '2.0',
               JsonRpc2Keys.KEY_METHOD: method}
        if paramObj:
            req[JsonRpc2Keys.KEY_PARAMS] = paramObj
        try:
            reqStr = json.dumps(req)
            self.validate(reqStr)
            Resource.send(self, reqStr)
        except ValueError as valerr:
            raise JsonRpc2ComplianceException( "Could not parse data into json object: %s"%str(valerr) )

    def sendSuccessResponse(self, id, result):
        resp = {JsonRpc2Keys.KEY_JSONRPC : '2.0',
                JsonRpc2Keys.KEY_ID : id,
                JsonRpc2Keys.KEY_RESULT : result}
        try:
            respStr = json.dumps(resp)
            self.validate(respStr)
            Resource.send(self, respStr)
        except ValueError as valerr:
            raise JsonRpc2ComplianceException( "Could not parse data into json object: %s"%str(valerr) )
        
    def sendErrorResponse(self, id, errorCode, errorMsg):
        resp = {JsonRpc2Keys.KEY_JSONRPC : '2.0',
                JsonRpc2Keys.KEY_ID : id,
                JsonRpc2Keys.KEY_ERROR :
                {JsonRpc2Keys.KEY_ERROR_CODE : errorCode,
                 JsonRpc2Keys.KEY_ERROR_MSG : errorMsg}}
        try:
            respStr = json.dumps(resp)
            self.validate(respStr)
            Resource.send(self, respStr)
        except ValueError as valerr:
            raise JsonRpc2ComplianceException( "Could not parse data into json object: %s"%str(valerr) )
        
    def send(self, data):
        raise JsonRpc2ComplianceException( "Cannot send raw data to a JsonRpc2Resource" )

class ResourceManager(Thread):
    def __init__(self, server):
        Thread.__init__(self)
        self.server = server
        self.resources = {}
        self.running = {}
        self.stopped = False
        
    def registerResource(self, rname, resource):
        self.resources[rname] = resource

    def handleIncoming(self, rname, data):
        logging.info("ResourceManager: got msg for rname=[%s] msg=[%s]"%(rname, data))
        if rname in self.resources:
            self.resources[rname].receive(data)
        else:
            logging.info("[%s] not found in resource map."%rname)

    def run(self):
        for k,v in self.resources.items():
            v.start()
            self.running[k] = v

        while(not self.stopped):
            time.sleep(5)

        logging.debug("About to stop ResourceManager")
        for name, res in self.running.items():
            res.running = False
            res.join()
        self.running = {}

class DisconnectException(Exception):
    def __init__(self,msg):
        self.msg = msg

class WebSocket(object):
    handshake = (
        "HTTP/1.1 101 Web Socket Protocol Handshake\r\n"
        "Upgrade: WebSocket\r\n"
        "Connection: Upgrade\r\n"
        "WebSocket-Origin: %(origin)s\r\n"
        "WebSocket-Location: ws://%(bind)s:%(port)s/%(resource)s\r\n"
        "Sec-Websocket-Origin: %(origin)s\r\n"
        "Sec-Websocket-Location: ws://%(bind)s:%(port)s/%(resource)s\r\n"
        "\r\n"
    )
    def __init__(self, client, server, resourceManager):
        self.client = client
        self.server = server
        self.resourceManager = resourceManager
        self.handshaken = False
        self.header = ""
        self.data = ""
        self.associatedResourceName = None

    def feed(self, data):
        if not self.handshaken:
            self.header += data
            if self.header.find('\r\n\r\n') != -1:
                parts = self.header.split('\r\n\r\n', 1)
                self.header = parts[0]
                if self.dohandshake(self.header, parts[1]):
                    logging.info("Handshake successful")
                    self.handshaken = True
        else:
            self.data += data
            msgs = self.data.split('\xff')
            self.data = msgs.pop()
            for msg in msgs:
                if len(msg) > 1:
                    if msg[0] == '\x00':
                        self.onmessage(msg[1:])
                else:
                    raise DisconnectException('Looks like client shut down')

    def dohandshake(self, header, key=None):
        logging.debug("Begin handshake: %s" % header)
        digitRe = re.compile(r'[^0-9]')
        spacesRe = re.compile(r'\s')
        part_1 = part_2 = origin = None
        for line in header.split('\r\n'):
            # Try splitting with spaces to see if we can find the GET first line
            if self.associatedResourceName is None:
                method, resource, proto = line.split(' ', 2)
                logging.debug("Method=[%s] Resource=[%s] Proto=[%s]"%(method,resource,proto))
                self.associatedResourceName = resource.strip('/')
                continue
            name, value = line.split(': ', 1)
            if name.lower() == "sec-websocket-key1":
                key_number_1 = int(digitRe.sub('', value))
                spaces_1 = len(spacesRe.findall(value))
                if spaces_1 == 0:
                    return False
                if key_number_1 % spaces_1 != 0:
                    return False
                part_1 = key_number_1 / spaces_1
            elif name.lower() == "sec-websocket-key2":
                key_number_2 = int(digitRe.sub('', value))
                spaces_2 = len(spacesRe.findall(value))
                if spaces_2 == 0:
                    return False
                if key_number_2 % spaces_2 != 0:
                    return False
                part_2 = key_number_2 / spaces_2
            elif name.lower() == "origin":
                origin = value
        logging.debug("theResource=[%s]"%(self.associatedResourceName))
        if part_1 and part_2:
            logging.debug("Using challenge + response")
            challenge = struct.pack('!I', part_1) + struct.pack('!I', part_2) + key
            response = hashlib.md5(challenge).digest()
            handshake = WebSocket.handshake % {
                'origin': origin,
                'port': self.server.port,
                'bind': self.server.bind,
                'resource': self.associatedResourceName
            }
            handshake += response
        else:
            logging.warning("Not using challenge + response")
            handshake = WebSocket.handshake % {
                'origin': origin,
                'port': self.server.port,
                'bind': self.server.bind,
                'resource': self.associatedResourceName
            }
        logging.debug("Sending handshake %s" % handshake)
        self.client.send(handshake)
        return True

    def onmessage(self, data):
        logging.info("Got message: [%s]. Passing to resource manager." % data)
        rname = self.associatedResourceName
        logging.info("About to pass client msg to resource manager with name=[%s]"%rname)
        self.resourceManager.handleIncoming(rname, data)        

    def send(self, data):
        #logging.info("Sent message: %s" % data)
        self.client.send("\x00%s\xff" % data)

    def close(self):
        self.client.close()

class WebSocketServer(object):
    def __init__(self, bind, port, cls):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((bind, port))
        self.bind = bind
        self.port = port
        self.cls = cls
        self.resourceManager = None
        self.connections = {}
        self.listeners = [self.socket]

        # Map resource names to filenos
        # This does not know anything about actual resource objects
        # it just looks at incoming requests for specific resource names
        # and associates connections to those names
        self.resourceMap = {} 

    def initResourceManager(self, cls, resourceList=[]):
        self.resourceManager = cls(self)
        for r in resourceList:
            self.resourceManager.registerResource(r.rname, r)
        self.resourceManager.start()
       
    def send(self, rname, data):
        logging.debug("WebSocketServer.send: got msg for rname=[%s] msg=[%s]"%(rname, data))
        if rname in self.resourceMap:
            flist = self.resourceMap[rname]
            for f in flist:
                if f in self.connections:
                    self.connections[f].send(data)
                else:
                    logging.info("Could not find fileno [%d] in connection list"%f)
        else:
            logging.info("Could not find [%s] in resource map."%rname)
        
    def sendToAll(self, msg):
        # Send to all clients
        for id, conn in self.connections.items():
            conn.send(msg)

    def halt(self):
        self.running = False
        self.resourceManager.stopped = True

    def listen(self, backlog=5):
        self.socket.listen(backlog)
        logging.info("Listening on %s" % self.port)
        self.running = True
        while self.running:
            rList, wList, xList = select(self.listeners, self.listeners, self.listeners, 1)
            for ready in rList:
                if ready == self.socket:
                    logging.debug("New client connection")
                    client, address = self.socket.accept()
                    fileno = client.fileno()
                    logging.debug("Added new client connection with id=[%d]"%fileno)
                    self.listeners.append(fileno)
                    self.connections[fileno] = self.cls(client, self, self.resourceManager)
                else:
                    logging.debug("Client ready for reading %s" % ready)
                    client = self.connections[ready].client
                    data = client.recv(1024)
                    fileno = client.fileno()
                    if data:
                        try:
                            self.connections[fileno].feed(data)
                            arn = self.connections[fileno].associatedResourceName
                            if arn not in self.resourceMap:
                                self.resourceMap[arn] = [fileno]
                            else:
                                if fileno not in self.resourceMap[arn]:
                                    self.resourceMap[arn].append(fileno)
                        except DisconnectException:
                            for fileno, conn in self.connections:
                                conn.close()
                            self.running = False
                    else:
                        pass
                        logging.debug("Closing client %s" % ready)
                        self.connections[fileno].close()
                        del self.connections[fileno]
                        self.listeners.remove(ready)
            for failed in xList:
                if failed == self.socket:
                    logging.error("Socket broke")
                    for fileno, conn in self.connections:
                        conn.close()
                    self.running = False

class stdin_reader(asyncore.file_dispatcher):

	def __init__(self, file, server):
		asyncore.file_dispatcher.__init__(self, file)
		self.file = file
		self.server = server

	def handle_read(self):
		buf = self.file.read()
		self.server.sendToAll(buf)

	def handle_write(self):
		pass
