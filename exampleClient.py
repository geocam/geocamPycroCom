
from Dispatcher import Dispatcher
from SharedScheduler import scheduler
from exampleConfig import *

def writeText(sock):
    sock.write('hola\n')

def handleConnect(sock):
    writeText(sock)
    scheduler.enterPeriodic(period=2.0, action=lambda: writeText(sock))

def handleLine(sock, line):
    print 'got:', line

def handleService(finder, serviceName, serviceEvent):
    print 'handling notification of service %s at event %s' % (serviceName, serviceEvent)
    if serviceName == SERVER_ENDPOINT:
        sock = com.connect(serviceEvent,
                           connectHandler = handleConnect,
                           lineHandler = handleLine)

def handleStdin(sock, line):
    print 'you said:', line

com = Dispatcher(moduleName='exampleClient')
if NOTIFY_ENDPOINT:
    com.connectToNotificationService(NOTIFY_ENDPOINT)
if USE_SERVICE_DISCOVERY:
    com.findServices(protoName = PROTOCOL, serviceHandler = handleService)
else:
    handleService(None, SERVER_ENDPOINT, SERVER_ENDPOINT)
sock = com.connect('console:', lineHandler = handleStdin)

com.runForever()
