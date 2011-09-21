# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

from Dispatcher import Dispatcher
from SharedScheduler import scheduler
import exampleConfig


def writeText(sock):
    sock.write('hola\n')


def handleConnect(sock):
    writeText(sock)
    scheduler.enterPeriodic(period=2.0, action=lambda: writeText(sock))


def handleLine(sock, line):
    print 'got:', line


def handleService(finder, serviceName, serviceEvent):
    print 'handling notification of service %s at event %s' % (serviceName, serviceEvent)
    if serviceName == exampleConfig.SERVER_ENDPOINT:
        com.connect(serviceEvent,
                    connectHandler=handleConnect,
                    lineHandler=handleLine)


def handleStdin(sock, line):
    print 'you said:', line

com = Dispatcher(moduleName='exampleClient')
if exampleConfig.NOTIFY_ENDPOINT:
    com.connectToNotificationService(exampleConfig.NOTIFY_ENDPOINT)
if exampleConfig.USE_SERVICE_DISCOVERY:
    com.findServices(protoName=exampleConfig.PROTOCOL, serviceHandler=handleService)
else:
    handleService(None, exampleConfig.SERVER_ENDPOINT, exampleConfig.SERVER_ENDPOINT)
com.connect('console:', lineHandler=handleStdin)

com.runForever()
