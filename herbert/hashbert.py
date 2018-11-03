"""
Herbert Submodule
@see herbert.core

Provides an interface to several
Hashing algorithms
"""

from core import *
from decorators import *
from herbert_utils import *

from hercurles_chat import *
from hercurles_utils import *

import hashlib as hl
import base64 as b64
import re

__all__ = ["HashBert"]

class HashBert(BaseBert):
  @command
  def md5(self, bot, update, args):
    self.reply(bot, update, hl.md5(_t_bytes(args)).hexdigest())

  @aliases('sha512', 'hash', 'sha')
  @command
  def sha512(self, bot, update, args):
    self.reply(bot, update, hl.sha512(_t_bytes(args)).hexdigest())

  @command
  def b64enc(self, bot, update, args):
    self.reply(bot, update, b64e(args))

  @command
  def b64dec(self, bot, update, args):
    self.reply(bot, update, b64d(args))

  @command
  def hashit(self, bot, update, args):
    import telegram
    self.reply(bot, update, hash_all(_t_bytes(args)), parse_mode=telegram.ParseMode.MARKDOWN) 

  @aliases('rotate', 'shift', 'ceasar')
  @command
  def rot(self, bot, update, args):
    assert len(args) >= 2, "Not enough arguments: /rot <shift> <text>"
    
    shift, *rest = args

    res = rotate(int(float(shift)), " ".join(rest))
    
    self.reply(bot, update, res)



def rotate_char(shift, char, low, high):
  return chr((shift + ord(char) - ord(low)) % (ord(high) - ord(low) + 1) + ord(low))


def rotate(shift, string):
  res = ""
  for char in string:
    if 'a' <= char <= 'z':
      res += rotate_char(shift, char, 'a', 'z')
    elif 'A' <= char <= 'Z':
      res += rotate_char(shift, char, 'A', 'Z')
    else:
      res += char
  return res
      


def hash_all(arg):
  res = ""
  for name in hl.algorithms_available:
    try:
      h = hl.new(name)
      h.update(arg)
      res += f"{re.sub('_', '-', name)}: ```{h.hexdigest()}```\n\n"
    except:
      pass
  
  return res


def b64e(args):
  return b64.b64encode(_t_bytes(args)).decode("utf-8")

def b64d(args):
  return b64.b64decode(_t_bytes(args)).decode("utf-8")

