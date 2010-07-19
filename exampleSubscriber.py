
import time
from Dispatcher import Dispatcher
from SharedScheduler import scheduler
from exampleConfig import *

def fooHandler(name, data):
    print 'got "%s" "%s"' % (name, data)

com = Dispatcher(moduleName='exampleSubscriber')
com.connectToNotificationService(NOTIFY_ENDPOINT)
com.subscribe('%s:foo' % PROTOCOL, fooHandler)
scheduler.runForever()
