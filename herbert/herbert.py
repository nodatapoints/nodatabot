#!/usr/bin/python3.7
"""
Beep boop ich bin eigentlich bloß die liste aller berts die was am doen sind
"""

import sys
import logging
from inspect import getmembers, isclass

import core
import basebert

from berts.asciimath import AsciiBert
from berts.diamaltbert import DiaMaltBert
from berts.gamebert import GameBert
from berts.hashbert import HashBert
from berts.helpbert import HelpBert
from berts.hercurles import Hercurles
from berts.interprert import InterpRert
from berts.kalcbert import KalcBert
from berts.ping import PingBert
from berts.texbert import TexBert
from berts.todobert import TodoBert
from berts.xkcdert import XKCDert
from berts.unicodert import UniCoDert
from berts.stackbert import StackBert
from berts.dudert import Dudert

from berts.testbert import TestBert


def configure_logs(log_lvl):
    logging.basicConfig()
    logging.getLogger('herbert.SETUP').setLevel(log_lvl)
    logging.getLogger('herbert.RUNTIME').setLevel(log_lvl)


def start_bot():
    core.init()

    # Autoregister the included Berts
    for _, c in getmembers(sys.modules[__name__], isclass):
        if issubclass(c, basebert.BaseBert) and c is not basebert.BaseBert:
            core.register_bert(c)

    core.register_inline_handler()

    if __name__ == '__main__':
        core.idle()


configure_logs(logging.DEBUG)
start_bot()
