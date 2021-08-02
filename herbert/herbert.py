#!/usr/bin/python3.7
"""
Beep boop ich bin eigentlich bloß die liste aller berts die was am doen sind
"""

import sys
import logging
from inspect import getmembers, isclass

from core import Herbert
import basebert

# pylint: disable = unused-import
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
from berts.wikibert import WikiBert

from berts.testbert import TestBert

__all__ = ['main']


def configure_logs(log_lvl: int) -> None:
    """ setup logging for herbert """
    logging.basicConfig()
    logging.getLogger('herbert.SETUP').setLevel(log_lvl)
    logging.getLogger('herbert.RUNTIME').setLevel(log_lvl)


def create_bot() -> Herbert:
    """ perform some setup """
    bot = Herbert()

    # Autoregister the included Berts
    for _, c in getmembers(sys.modules[__name__], isclass):
        if issubclass(c, basebert.BaseBert) and c is not basebert.BaseBert:
            bot.register_bert(c)

    bot.register_inline_handler()

    return bot


def main() -> None:
    """ main entrypoint, runs bot """
    configure_logs(logging.DEBUG)
    create_bot().idle()


if __name__ == '__main__':
    main()
