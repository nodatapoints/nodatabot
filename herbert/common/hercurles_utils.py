from common import network
from basebert import Herberror
import re

from lxml import etree
parser = etree.XMLParser(recover=True)

__all__ = ['tx_assert', 'load_xml', 'search_for', 't_arr_to_bytes']


def load_xml(url):
    res = network.t_load_str(url)
    res = re.sub('xmlns=".*?"', " ", res)
    try:
        return etree.fromstring(res, parser=parser)
    except etree.ParseError as e:
        raise
        # print("That Parse eror, again. Heres info: ", e)
        # with open("dump.err.txt", "w") as fobj:
        #    fobj.write(res)

        # print("Loaded XML saved to dump.err.txt")


SPACES = "\\s+"
PLUS = "+"


def search_for(query):
    # TODO properly escape this query
    url = f"https://duckduckgo.com/html/?q={re.sub(SPACES, PLUS, query)}"

    root = load_xml(url)

    elements = root.findall(".//a[@class='result__snippet']")

    return [elem.attrib['href'] for elem in elements]


def t_arr_to_bytes(arr):
    return bytes(" ".join(arr), encoding="utf-8")


def tx_assert(condition, msg):
    if not condition:
        raise Herberror(msg)
