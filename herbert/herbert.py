#!/usr/bin/python3.7

from core import *
from gamebert import GameBert
from texbert import TexBert
from ping import PingBert
from hashbert import HashBert
from hercurles import Hercurles
from philip import PhilipBert
from helpbert import HelpBert

register_bert(GameBert)
register_bert(PingBert)
register_bert(Hercurles)
register_bert(HashBert)
register_bert(PhilipBert)
register_bert(HelpBert)
register_bert(TexBert)

if __name__ == '__main__':
    idle()
