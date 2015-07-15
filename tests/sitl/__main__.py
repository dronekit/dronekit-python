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
    sitl_args = ['dronekit-sitl', 'copter-3.3-rc5', '-I0', '-S', '--model', 'quad', '--home=-35.363261,149.165230,584,353']

    speedup = os.environ.get('TEST_SPEEDUP', '1')
    rate = os.environ.get('TEST_RATE', '200')
    sitl_args += ['--speedup', str(speedup), '-r', str(rate)]

    # Change CPU core affinity.
    # TODO change affinity on osx/linux
    if sys.platform == 'win32':
        # 0x14 = 0b1110 = all cores except cpu 1
        sitl = Popen(['start', '/affinity', '14', '/realtime', '/b', '/wait'] + sitl_args, shell=True, stdout=PIPE, stderr=PIPE)
    else:
        sitl = Popen(sitl_args, stdout=PIPE, stderr=PIPE)
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

    mavproxy_verbose = False
    timeout = 5*60

    try:
        p = Popen([sys.executable, '-m', 'MAVProxy.mavproxy', '--logfile=' + tempfile.mkstemp()[1], '--master=tcp:127.0.0.1:5760'], cwd=testpath, env=newenv, stdin=PIPE, stdout=PIPE, stderr=PIPE if not mavproxy_verbose else None)
        bg.append(p)

        # TODO this sleep is only for us to waiting until
        # all parameters to be received; would prefer to
        # move this to testlib.py and happen asap
        while p.poll() == None:
            line = p.stdout.readline()
            if mavproxy_verbose:
                sys.stdout.write(line)
                sys.stdout.flush()
            if 'parameters' in line:
                break

        time.sleep(3)

        # NOTE these are *very inappropriate settings*
        # to make on a real vehicle. They are leveraged
        # exclusively for simulation. Take heed!!!
        p.stdin.write('param set ARMING_CHECK 0\n')
        p.stdin.write('param set FS_THR_ENABLE 0\n')
        p.stdin.write('param set FS_GCS_ENABLE 0\n')
        p.stdin.write('param set EKF_CHECK_THRESH 0\n')

        p.stdin.write('module load droneapi.module.api\n')
        p.stdin.write('api start testlib.py\n')
        p.stdin.flush()

        if mavproxy_verbose:
            while True:
                nextline = p.stdout.readline()
                if nextline == '' and p.poll() != None:
                    break
                sys.stdout.write(nextline)
                sys.stdout.flush()
        else:
            wait_timeout(p, timeout)
    except RuntimeError:
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
        print('[runner] ...failed with dronekit error code ' + str(p.returncode))
    else:
        print('[runner] ...success.')

    sys.stdout.flush()
    sys.stderr.flush()
    time.sleep(5)
    return p.returncode

retry = int(os.environ.get('TEST_RETRY', '1'))
for path in os.listdir(testpath):
    if path.startswith('test_') and path.endswith('.py'):
        name = path[:-3]
        i = retry
        while True:
            ret = lets_run_a_test(name)
            if ret == 0:
                break
            i = i - 1
            if i == 0:
                print('[runner] aborting after failed test.')
                sys.exit(ret)
            print('[runner] retrying %s %s more times' % (name, i, ))

print('[runner] finished.')
sys.stdout.flush()
sys.stdout.close()
sys.stderr.flush()
sys.stderr.close()
