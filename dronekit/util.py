from __future__ import print_function
import sys
import logging
import logging.config

class Logger():
    def __init__(self):
        logging.config.fileConfig("/etc/shotmanager.conf")
        self.xlog = logging.getLogger("dkpy")

    def log(self, data):
        self.xlog.info(str(data).replace("\0", ""))

logger = Logger()

def errprinter(*args):
    logger(*args)

def logger(*args):
    print(*args, file=sys.stderr)
    logger.log(*args)
    sys.stderr.flush()
