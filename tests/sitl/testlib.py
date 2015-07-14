"""
We can't use nose right now, so we recreate some of
nose's features in a compatible way, but run it in-process.
"""

import inspect
import traceback
import os
import sys
import importlib

def assert_equals(a, b, msg=None):
    if not a == b:
        raise AssertionError(msg or "%r != %r" % (a, b))

def override_io():
    old_out = sys.stdout
    old_err = sys.stderr

    fd_out = int(os.environ['TEST_WRITE_OUT'])
    fd_err = int(os.environ['TEST_WRITE_ERR'])
    if sys.platform == 'win32':
        import msvcrt
        fd_out = msvcrt.open_osfhandle(fd_out, 0)
        fd_err = msvcrt.open_osfhandle(fd_err, 0)
    api_out = os.fdopen(fd_out, 'w')
    api_err = os.fdopen(fd_err, 'w')

    class Intercept:
        def __init__(self, api, old):
            self.api = api
            self.old = old

        def write(self, data):
            import threading
            if threading.current_thread().name.startswith('APIThread'):
                self.api.write(data)
            else:
                self.old.write(data)

        def flush(self):
            self.api.flush()
            self.old.flush()

    sys.stdout = Intercept(api_out, old_out)
    sys.stderr = Intercept(api_err, old_err)

def unoverride_io():
    sys.stdout.api.close()
    sys.stdout = sys.stdout.old
    sys.stderr.api.close()
    sys.stderr = sys.stderr.old

def run_tests(lib):
    # Work around weird test reloading issues.
    try:
        sys.local_connect = local_connect
    except:
        pass

    try:
        sys.path.append(os.path.dirname('__file__'))
        mod = importlib.import_module(lib)

        tests = []
        for (name, m) in inspect.getmembers(mod, inspect.isfunction):
            if name.startswith('test_'):
                tests.append(m)

        if len(tests) == 0:
            return

        override_io()

        for test in tests:
            test(sys.local_connect)
            sys.stdout.write('.')
    except:
        print '\nERROR'
        traceback.print_exc()

        sys.stdout.flush()
        sys.stderr.flush()
        unoverride_io()
        os._exit(1)

    print '\nOK'

    sys.stdout.flush()
    sys.stderr.flush()
    unoverride_io()
    os._exit(0)

run_tests(os.environ['TEST_NAME'])
