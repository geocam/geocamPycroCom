
import simplejson

class ServiceFinder(object):
    """Mixin that provides service finding functionality on top of a pub-sub protocol."""

    def findServices(self, announceServices, serviceHandler):
        self._serviceHandler = serviceHandler
        self._announceServices = {}
        self._allServices = {}
        for serviceEntry in announceServices:
            if isinstance(serviceEntry, str):
                self._announceServices[serviceEntry] = serviceEntry
            else:
                serviceName, serviceEvent = serviceEntry
                self._announceServices[serviceName] = serviceEvent
        self._startHandling()
            
    def getAllServices(self):
        return self._allServices

    def _packMessageString(self):
        msgStruct = [self._dispatcher._moduleName, self._announceServices]
        return simplejson.dumps(msgStruct)

    def _startHandling(self):
        self.subscribeWithHandler('marco', self._marcoHandler)
        self.subscribeWithHandler('polo', self._poloHandler)
        self.publish('marco', self._packMessageString())

    def _marcoHandler(self, event, data):
        moduleName, newServices = simplejson.loads(data)
        self._handleNewServices(newServices)
        if moduleName != self._dispatcher._moduleName:
            self.publish('polo', self._packMessageString())

    def _poloHandler(self, event, data):
        moduleName, newServices = simplejson.loads(data)
        self._handleNewServices(newServices)

    def _handleNewServices(self, newServices):
        for serviceName, serviceEvent in newServices.iteritems():
            if not (serviceName in self._allServices
                    and self._allServices[serviceName] == serviceEvent):
                self._allServices[serviceName] = serviceEvent
                self.handleService(serviceName, serviceEvent)

    def handleService(self, serviceName, serviceEvent):
        """What to do when we hear about a new service."""
        if self._serviceHandler != None:
            self._serviceHandler(self, serviceName, serviceEvent)
