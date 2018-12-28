import contextlib
import sys

class DummyFile(object):
    def write(self, x): pass

@contextlib.contextmanager
def no_stdout():
    sys.stdout = DummyFile()
    yield
    sys.stdout = sys.__stdout__
