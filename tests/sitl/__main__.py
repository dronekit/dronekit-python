#!/usr/bin/env python -u

from __future__ import print_function
import time
import os
from subprocess import Popen, PIPE
import atexit
import sys
import tempfile
from functools import wraps
import errno
import os
import signal
import time
import psutil

def wait_timeout(proc, seconds):
    """Wait for a process to finish, or raise exception after timeout"""
    start = time.time()
    end = start + seconds
    interval = min(seconds / 1000.0, .25)

    while True:
        result = proc.poll()
        if result is not None:
            return result
        if time.time() >= end:
            raise RuntimeError("Process timed out")
        time.sleep(interval)

def kill(proc_pid):
    process = psutil.Process(proc_pid)
    for proc in process.children(recursive=True):
        try:
            proc.kill()
        except psutil.NoSuchProcess:
            pass
    try:
        process.kill()
    except psutil.NoSuchProcess:
        pass

if sys.platform == "win32":
    import msvcrt
    import _subprocess
else:
    import fcntl

bg = []
def cleanup_processes():
    for p in bg:
        kill(p.pid)
atexit.register(cleanup_processes)

testpath = os.path.dirname(__file__)


def wrap_fd(pipeout):
    # Prepare to pass to child process
    if sys.platform == "win32":
        curproc = _subprocess.GetCurrentProcess()
        pipeouth = msvcrt.get_osfhandle(pipeout)
        pipeoutih = _subprocess.DuplicateHandle(curproc, pipeouth, curproc, 0, 1, _subprocess.DUPLICATE_SAME_ACCESS)
        return (str(int(pipeoutih)), pipeoutih)
    else:
        return (str(pipeout), None)

def lets_run_a_test(name):
    sitl = Popen(['dronekit-sitl', 'copter-3.3-rc5', '-I0', '-S', '--model', 'quad', '--home=-35.363261,149.165230,584,353'], stdout=PIPE, stderr=PIPE)
    bg.append(sitl)

    while sitl.poll() == None:
        line = sitl.stdout.readline()
        if 'Waiting for connection' in line:
            break
    if sitl.poll() != None and sitl.returncode != 0:
        print('[runner] ...aborting with SITL error code ' + str(sitl.returncode))
        sys.stdout.flush()
        sys.stderr.flush()
        sys.exit(sitl.returncode)

    newenv = os.environ.copy()
    newenv['PYTHONUNBUFFERED'] = '1'

    if sys.platform == 'win32':
        out_fd = 1
        err_fd = 2
    else:
        out_fd = os.dup(1)
        err_fd = os.dup(2)

    (out_fd, out_h) = wrap_fd(out_fd)
    (err_fd, err_h) = wrap_fd(err_fd)

    newenv['TEST_WRITE_OUT'] = out_fd
    newenv['TEST_WRITE_ERR'] = err_fd
    newenv['TEST_NAME'] = name

    print('[runner] ' + name, file=sys.stderr)
    sys.stdout.flush()
    sys.stderr.flush()

    timeout = 300
    try:
        p = Popen([sys.executable, '-m', 'MAVProxy.mavproxy', '--logfile=' + tempfile.mkstemp()[1], '--master=tcp:127.0.0.1:5760', '--cmd=module load droneapi.module.api; ; api start testlib.py'], cwd=testpath, env=newenv, stdout=PIPE, stderr=PIPE)
        bg.append(p)
        wait_timeout(p, timeout)
    except TimeoutExpired:
        kill(p.pid)
        p.returncode = 143
        print('Error: Timeout after ' + str(timeout) + ' seconds.')
    bg.remove(p)

    if sys.platform == 'win32':
        out_h.Close()
        err_h.Close()

    kill(sitl.pid)
    bg.remove(sitl)

    if p.returncode != 0:
        print('[runner] ...aborting with dronekit error code ' + str(p.returncode))
        sys.stdout.flush()
        sys.stderr.flush()
        sys.exit(p.returncode)
    
    print('[runner] ...success.')
    time.sleep(5)

for i in os.listdir(testpath):
    if i.startswith('test_') and i.endswith('.py'):
        lets_run_a_test(i[:-3])

print('[runner] finished.')
sys.stdout.flush()
sys.stdout.close()
sys.stderr.flush()
sys.stderr.close()
