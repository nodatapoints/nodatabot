#!/usr/bin/python3.7

from core import *
from gamebert import GameBert
from hashbert import HashBert
from hercurles import Hercurles

register_bert(Hercurles)
register_bert(GameBert)
register_bert(HashBert)

if __name__ == '__main__':
    idle()
