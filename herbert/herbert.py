#!/usr/bin/python3.7
# Beep boop ich bin eingentlich bloß die liste aller berts die was am doen sind

# change pwd to consistent location
import os
import pathlib
herbert_path = pathlib.Path(os.path.dirname(os.path.abspath(__file__)))
os.chdir(herbert_path)

from core import *
from gamebert import GameBert
from texbert import TexBert
from ping import PingBert
from hashbert import HashBert
from hercurles import Hercurles
from kalcbert import KalcBert
from diamaltbert import DiaMaltBert
from helpbert import HelpBert
from interprert import InterpRert

register_bert(GameBert)
register_bert(PingBert)
register_bert(Hercurles)
register_bert(HashBert)
register_bert(KalcBert)
register_bert(DiaMaltBert)
register_bert(HelpBert)
register_bert(TexBert)
register_bert(InterpRert)

if __name__ == '__main__':
    idle()
