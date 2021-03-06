# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

import sys
import comExceptions
from comExceptions import BadEndpointError
import SharedScheduler


class Dispatcher:
    def __init__(self, moduleName, scheduler=None, period=0.1):
        if scheduler == None:
            scheduler = SharedScheduler.scheduler
        self._moduleName = moduleName
        self._scheduler = scheduler
        self._period = period
        self._handlers = {}
        self._protocols = {}
        self._polling = False
        self._handleMessagesTimer = None

    def connectToNotificationService(self, notificationService):
        protocol, addr = self._splitProtocol(notificationService)
        protocol.connectToNotificationService(self._moduleName, addr)
        self._startHandling()

    def getProtocol(self, protoName, endpoint=None):
        if endpoint == None:
            endpoint = protoName
        try:
            return self._protocols[protoName]
        except KeyError:
            protocol = self._loadProtocol(protoName, endpoint)
            self._protocols[protoName] = protocol
            return protocol

    def subscribe(self, event, handler):
        if event in self._handlers:
            raise comExceptions.EventAlreadyBoundError(event)
        else:
            self._handlers[event] = handler
            protocol, addr = self._splitProtocol(event)
            protocol.subscribe(addr)

    def unsubscribe(self, event):
        protocol, eventName = self._splitProtocol(event)
        protocol.unsubscribe(eventName)
        del self._handlers[eventName]

    def publish(self, event, data):
        protocol, eventName = self._splitProtocol(event)
        protocol.publish(eventName, data)

    def handleMessage(self):
        for protocolName, protocol in self._protocols.iteritems():
            if protocol.pollForMessages and protocol.isMessage():
                eventName, data = protocol.getMessage()
                event = ':'.join((protocolName, eventName))
                self._handlers[event](event, data)
                return True
        return False

    def handleMessages(self):
        while self.handleMessage():
            pass

    def connect(self, endpoint, lineMode=True, readHandler=None, connectHandler=None,
                lineHandler=None):
        protocol, addr = self._splitProtocol(endpoint)
        sock = protocol.connect(self, addr,
                                dict(lineMode=lineMode,
                                     readHandler=readHandler,
                                     connectHandler=connectHandler,
                                     lineHandler=lineHandler))
        self._startHandling()
        return sock

    def listen(self, endpoint, maxConnections=1, lineMode=True, acceptHandler=None,
               connectHandler=None, readHandler=None, lineHandler=None, createSocketHandler=None):
        protocol, addr = self._splitProtocol(endpoint)
        sock = protocol.listen(self, addr,
                               dict(maxConnections=maxConnections,
                                    lineMode=lineMode,
                                    acceptHandler=acceptHandler,
                                    createSocketHandler=createSocketHandler,
                                    connectHandler=connectHandler,
                                    readHandler=readHandler,
                                    lineHandler=lineHandler))
        self._startHandling()
        return sock

    def findServices(self, protoName, announceServices=None, serviceHandler=None):
        if announceServices == None:
            announceServices = []
        if ':' in protoName:
            protoName, _ = self._splitProtocol(protoName)
        self.getProtocol(protoName).findServices(announceServices, serviceHandler)

    def runForever(self):
        return self._scheduler.runForever()

    def waitForResponse(self, collectResponseHandler):
        return self._scheduler.waitForResponse(collectResponseHandler)

    def close(self):
        if self._polling:
            self._scheduler.cancelPeriodic(self._handleMessagesTimer)
        for protocol in self._protocols.itervalues():
            protocol.close()

    def _loadProtocol(self, protoName, endpoint):
        if protoName == 'console':
            protoName = 'file'  # alias
        implName = '%sWrapper' % protoName.capitalize()  # e.g. TcpWrapper
        modName = 'geocamPycroCom.%s' % implName  # e.g. geocamPycroCom.tcpWrapper
        try:
            __import__(modName)
        except ImportError:
            raise BadEndpointError("can't load protocol", endpoint)
        mod = sys.modules[modName]
        cls = getattr(mod, implName)  # e.g. geocamPycroCom.TcpWrapper.TcpWrapper
        return cls(self, protoName)

    def _splitProtocol(self, endpoint):
        try:
            protoName, rest = endpoint.split(':', 1)
        except ValueError:
            raise BadEndpointError('not in form "protocol:address"', endpoint)
        return self.getProtocol(protoName), rest

    def _startHandling(self, period=0.1):
        if not self._polling:
            if sum([p.pollForMessages for p in self._protocols.itervalues()]):
                self._handleMessagesTimer = (self._scheduler.enterPeriodic
                                             (period=self._period, action=self.handleMessages))
                self._polling = True
