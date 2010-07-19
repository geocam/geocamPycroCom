
from Dispatcher import Dispatcher
from SharedScheduler import scheduler
from exampleConfig import *

def publishMessage():
    com.publish('%s:foo' % PROTOCOL, 'bar')
    print 'published message'

com = Dispatcher(moduleName='examplePublisher')
com.connectToNotificationService(NOTIFY_ENDPOINT)
scheduler.enterPeriodic(period=1.0, action=publishMessage)
scheduler.runForever()
