from __future__ import print_function
import sys


def errprinter(*args):
    print(*args, file=sys.stderr)
    sys.stderr.flush()
