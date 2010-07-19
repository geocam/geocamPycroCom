
import sys
import traceback

def printTraceback():
    errClass, errObj, errTB = sys.exc_info()[:3]
    traceback.print_tb(errTB)
    print >>sys.stderr, '%s.%s: %s' % (errClass.__module__,
                                       errClass.__name__,
                                       str(errObj))
    if isinstance(errObj, KeyboardInterrupt):
        sys.exit(0)
