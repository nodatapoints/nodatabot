"""
Import pathlib and a wrapper around it and
os.chdir, to make the working directory a
consistent location
"""
from os import path, chdir
import pathlib


def change_path():
    """
    change pwd to consistent location
    """
    herbert_path = pathlib.Path(path.dirname(path.abspath(__file__)))
    chdir(herbert_path)
