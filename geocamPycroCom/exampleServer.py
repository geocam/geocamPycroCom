# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

from Dispatcher import Dispatcher
import exampleConfig


def handleConnect(sock):
    print 'got connection'


def handleLine(sock, line):
    print 'got:', line
    sock.write('ciao\n')

com = Dispatcher(moduleName='exampleServer')
if exampleConfig.NOTIFY_ENDPOINT:
    com.connectToNotificationService(exampleConfig.NOTIFY_ENDPOINT)
com.listen(exampleConfig.SERVER_ENDPOINT,
           connectHandler=handleConnect,
           lineHandler=handleLine)
if exampleConfig.USE_SERVICE_DISCOVERY:
    com.findServices(protoName=exampleConfig.PROTOCOL, announceServices=[exampleConfig.SERVER_ENDPOINT])
com.runForever()
