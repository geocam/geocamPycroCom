# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

from weakref import WeakKeyDictionary

class WeakSet(object):
    def __init__(self):
        self._vals = WeakKeyDictionary()

    def add(self, elt):
        self._vals[elt] = 1

    def remove(self, elt):
        del self._vals[elt]

    def __iter__(self):
        # try to ensure that the dictionary doesn't change size during
        # iteration by freezing it with the keys() function.
        self._tmp = self._vals.keys()
        for elt in self._tmp:
            yield elt
        del self._tmp
