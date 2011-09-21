# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

import sched
import time
import asyncore
from printTraceback import printTraceback


class ExitSchedulerLoop(Exception):
    pass


def asyncoreListenWait(delay):
    if asyncore.socket_map:
        asyncore.poll(delay)
    else:
        # asyncore.poll() returns immediately if there are no sockets to watch;
        # avoid busy loop
        time.sleep(delay)


class SchedulerPlus(sched.scheduler):
    def __init__(self, timefunc, delayfunc):
        def _delayPlus(delay):
            return self.runActionCatchExceptions(delayfunc, (delay,))
        sched.scheduler.__init__(self, timefunc, _delayPlus)
        self._collectResponseHandlers = []

    def runActionCatchExceptions(self, action, args):
        try:
            action(*args)
            if self._collectResponseHandlers:
                response = self._collectResponseHandlers[-1]()
                if response != None:
                    raise ExitSchedulerLoop(response)
        except ExitSchedulerLoop:
            # pass this on so we exit the scheduler loop
            raise
        except:
            printTraceback()
            caughtException = True
        else:
            caughtException = False
        return caughtException

    def enterSimple(self, delay, action, argument=(), priority=1):
        def _handler(*args):
            #print 'enterSimple handler: args=%s' % str(args)
            self.runActionCatchExceptions(action, args)
        return self.enter(delay, priority, _handler, argument)

    def cancelSimple(self, event):
        return self.cancel(event)

    def enterPeriodic(self, period, action, argument=(), priority=1):
        event = [None]

        def _handler(*args):
            #print 'enterPeriodic handler: args=%s' % str(args)
            caughtException = self.runActionCatchExceptions(action, args)
            if not caughtException:
                event[0] = self.enterSimple(period, _handler, argument, priority)

        event[0] = self.enterSimple(period, _handler, argument, priority)
        return event

    def cancelPeriodic(self, event):
        return self.cancel(event[0])

    def runForever(self):
        try:
            while 1:
                self.run()
                self.delayfunc(3600)
        except ExitSchedulerLoop, args:
            return args[0]

    def waitForResponse(self, collectResponseHandler):
        self._collectResponseHandlers.append(collectResponseHandler)
        result = self.runForever()
        self._collectResponseHandlers.pop(-1)
        return result

scheduler = SchedulerPlus(time.time, asyncoreListenWait)
