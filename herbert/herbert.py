#!/usr/bin/python3.7

from core import *
from gamebert import GameBert
# from hashbert import HashBert
# from hercurles import Hercurles
# from philip import PhilipBert

register_bert(GameBert)
# register_bert(Hercurles)
# register_bert(HashBert)
# register_bert(PhilipBert)

if __name__ == '__main__':
    idle()
