# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

from Dispatcher import Dispatcher
from SharedScheduler import scheduler
import exampleConfig


def fooHandler(name, data):
    print 'got "%s" "%s"' % (name, data)

com = Dispatcher(moduleName='exampleSubscriber')
com.connectToNotificationService(exampleConfig.NOTIFY_ENDPOINT)
com.subscribe('%s:foo' % exampleConfig.PROTOCOL, fooHandler)
scheduler.runForever()
