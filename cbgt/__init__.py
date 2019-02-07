#!usr/bin/env python
import os
import glob

modules = glob.glob(os.path.dirname(__file__)+"/*.py")
__all__ = [ os.path.basename(f)[:-3] for f in modules]
_package_dir = os.path.dirname(os.path.realpath(__file__))


__version__ = '0.0.1'

from . import netgen
from . import analyzefx
from . import sim
from . import vis

try:
    import cbgt
except ImportError:
    pass
