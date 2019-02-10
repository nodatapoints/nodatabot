#!/usr/bin/python3.7
# Beep boop ich bin eigentlich bloß die liste aller berts die was am doen sind

import sys
from inspect import getmembers, isclass

import core
import basebert

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
from urbanbert import UrbanBert
from unicodert import UniCoDert

from testbert import TestBert


def start_bot():
    core.init()

    # Autoregister the included Berts
    for _, c in getmembers(sys.modules[__name__], isclass):
        if issubclass(c, basebert.BaseBert) and c is not basebert.BaseBert:
            core.register_bert(c)

    core.register_inline_handler()

    if __name__ == '__main__':
        core.idle()


start_bot()
