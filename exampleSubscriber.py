# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

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
