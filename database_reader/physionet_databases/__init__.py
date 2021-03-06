# -*- coding: utf-8 -*-
"""
facilities for easy reading of `official` databases from physionet

data from `official` physionet databases can be loaded from its server at use,
or downloaded using `wfdb` easily beforehand

About the header (.hea) files:
https://physionet.org/physiotools/wag/header-5.htm
"""

from .afdb import *
from .aftdb import *
from .apnea_ecg import *
from .bidmc import *
from .butqdb import *
from .capslpdb import *
from .cinc2017 import *
from .cinc2018 import *
from .cinc2020 import *
from .cinc2021 import *
from .edb import *
from .ltafdb import *
from .ltstdb import *
from .ludb import *
from .mimic3 import *
from .mitdb import *
from .nstdb import *
from .qtdb import *
from .slpdb import *
from .stdb import *
from .ucddb import *
from .incartdb import *
from .ptbdb import *
from .ptb_xl import *


__all__ = [s for s in dir() if not s.startswith("_")]
