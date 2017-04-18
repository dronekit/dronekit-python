from __future__ import print_function
import sys


def errprinter(*args):
    logger(*args)

def logger(*args):
    print(*args, file=sys.stderr)
    sys.stderr.flush()
