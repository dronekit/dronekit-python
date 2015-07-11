#!/usr/bin/env python -u

from __future__ import print_function
import time
import os
from subprocess import Popen, PIPE
import atexit
import sys
import tempfile

bg = []
def cleanup_processes():
    for p in bg:
        p.kill()
atexit.register(cleanup_processes)

testpath = os.path.dirname(__file__)

from functools import wraps
import errno
import os
import signal

class TimeoutError(Exception):
    pass

def timeout(seconds=10, error_message='Timeout Occurred'):
    def decorator(func):
        def _handle_timeout(signum, frame):
            raise TimeoutError(error_message)

        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)
            return result

        return wraps(func)(wrapper)

    return decorator



def lets_run_a_test(name):
    sitl = Popen(['dronekit-sitl', 'copter-3.3-rc5', '-I0', '-S', '--model', 'quad', '--home=-35.363261,149.165230,584,353'], stdout=PIPE, stderr=PIPE)
    bg.append(sitl)

    time.sleep(5)

    newenv = os.environ.copy()
    newenv['PYTHONUNBUFFERED'] = '1'

    newenv['TEST_WRITE_OUT'] = str(os.dup(1))
    newenv['TEST_WRITE_ERR'] = str(os.dup(2))
    newenv['TEST_NAME'] = name

    print('[runner] ' + name, file=sys.stderr)
    p = Popen(['mavproxy.py', '--logfile=' + tempfile.mkstemp()[1], '--master=tcp:127.0.0.1:5760', '--cmd=module load droneapi.module.api; ; api start testlib.py'], cwd=testpath, env=newenv, stdout=PIPE, stderr=PIPE)
    bg.append(p)

    @timeout(90, 'Test timed out after 90s')
    def communicate():
        p.communicate()

    try:
        communicate()
    except TimeoutError as e:
        p.kill()
        print('Error:', e.message)
        p.returncode = 143
    bg.remove(p)

    sitl.kill()
    bg.remove(sitl)

    if p.returncode != 0:
        sys.exit(p.returncode)
    
    time.sleep(5)

for i in os.listdir(testpath):
    if i.startswith('test_') and i.endswith('.py'):
        lets_run_a_test(i[:-3])
