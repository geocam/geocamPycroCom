# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

from FileStreamSocket import FileStreamSocket


class FileWrapper:
    pollForMessages = False

    def __init__(self, dispatcher, protoName):
        self._dispatcher = dispatcher
        self._protoName = protoName

    def connect(self, dispatcher, unusedAddr, optsDict):
        sock = FileStreamSocket(optsDict)
        assert unusedAddr == ''
        sock.connect()
        return sock
