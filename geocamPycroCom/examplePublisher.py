# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

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
