DEBUG=False

try:
    from local_config import *
except ImportError:
    # no local config found
    pass