from __future__ import print_function

import logging
import sys


def errprinter(*args):
    logger(*args)


def logger(*args):
    print(*args, file=sys.stderr)
    sys.stderr.flush()


class ErrprinterHandler(logging.Handler):
    """Logging handler to support the deprecated `errprinter` argument to connect()"""

    def __init__(self, errprinter):
        logging.Handler.__init__(self)
        self.errprinter = errprinter

    def emit(self, record):
        msg = self.format(record)
        self.errprinter(msg)
