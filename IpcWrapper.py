
from cmuIpcPackage import CmuIpc
from PubSubWrapper import PubSubWrapper

class IpcWrapper(CmuIpc, PubSubWrapper):
    pollForMessages = True
