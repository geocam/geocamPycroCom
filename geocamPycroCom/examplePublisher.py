# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

from Dispatcher import Dispatcher
from SharedScheduler import scheduler
import exampleConfig


def publishMessage():
    com.publish('%s:foo' % exampleConfig.PROTOCOL, 'bar')
    print 'published message'

com = Dispatcher(moduleName='examplePublisher')
com.connectToNotificationService(exampleConfig.NOTIFY_ENDPOINT)
scheduler.enterPeriodic(period=1.0, action=publishMessage)
scheduler.runForever()
