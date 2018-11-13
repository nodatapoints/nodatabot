import pathlib

from os import path, chdir


# change pwd to consistent location
def change_path():
    herbert_path = pathlib.Path(path.dirname(path.abspath(__file__)))
    chdir(herbert_path)
