import sys

__version__ = '0.1.1'

if sys.version_info[0] == 2:
    raise RuntimeError('valohai-local-run requires Python 3; you have %s' % sys.version)
