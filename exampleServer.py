# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

from Dispatcher import Dispatcher
from exampleConfig import *

def handleConnect(sock):
    print 'got connection'

def handleLine(sock, line):
    print 'got:', line
    sock.write('ciao\n')

com = Dispatcher(moduleName='exampleServer')
if NOTIFY_ENDPOINT:
    com.connectToNotificationService(NOTIFY_ENDPOINT)
com.listen(SERVER_ENDPOINT,
           connectHandler = handleConnect,
           lineHandler = handleLine)
if USE_SERVICE_DISCOVERY:
    com.findServices(protoName = PROTOCOL, announceServices = [SERVER_ENDPOINT])
com.runForever()
