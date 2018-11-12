#!/usr/bin/python3.7
# Beep boop ich bin eigentlich bloß die liste aller berts die was am doen sind

import pathlib
import sys
from inspect import getmembers, isclass
from os import path, chdir

# change pwd to consistent location
herbert_path = pathlib.Path(path.dirname(path.abspath(__file__)))
chdir(herbert_path)

from core import *
from basebert import BaseBert

from gamebert import GameBert
from texbert import TexBert
from ping import PingBert
from hashbert import HashBert
from hercurles import Hercurles
from kalcbert import KalcBert
from diamaltbert import DiaMaltBert
from interprert import InterpRert
from xkcdert import XKCDert
from helpbert import HelpBert
from asciimath import AsciiBert
from testbert import TestBert


# Autoregister the included Berts
for _, c in getmembers(sys.modules[__name__], isclass):
    if issubclass(c, BaseBert) and c is not BaseBert:
        register_bert(c)


if __name__ == '__main__':
    idle()

