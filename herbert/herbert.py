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

from asciimath import AsciiBert
from diamaltbert import DiaMaltBert
from gamebert import GameBert
from hashbert import HashBert
from helpbert import HelpBert
from hercurles import Hercurles
from interprert import InterpRert
from kalcbert import KalcBert
from ping import PingBert
from texbert import TexBert
from todobert import TodoBert
from xkcdert import XKCDert
from helpbert import HelpBert
from asciimath import AsciiBert


# Autoregister the included Berts
for _, c in getmembers(sys.modules[__name__], isclass):
    if issubclass(c, BaseBert) and c is not BaseBert:
        register_bert(c)


if __name__ == '__main__':
    idle()

