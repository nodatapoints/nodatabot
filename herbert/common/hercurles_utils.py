from common import network
from basebert import Herberror
import xml.etree.ElementTree
import re

__all__ = ['tx_assert', 'load_xml', 'search_for', 't_arr_to_bytes']


def load_xml(url):
    res = network.t_load_str(url)
    # TODO only do this for pages with xmlns
    res = re.sub('xmlns=".*?"', " ", res)
    return xml.etree.ElementTree.fromstring(res)


SPACES = "\\s+"
PLUS = "+"


def search_for(query):
    # TODO properly escape this query

    url = f"https://duckduckgo.com/html/?q={re.sub(SPACES, PLUS, query)}"
    print(url)
    root = load_xml(url)

    elements = root.findall(".//a[@class='result__snippet']")

    return [elem.attrib['href'] for elem in elements]


def t_arr_to_bytes(arr):
    return bytes(" ".join(arr), encoding="utf-8")


def tx_assert(condition, msg):
    if not condition:
        raise Herberror(msg)
