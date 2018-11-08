from common import hercurles_network
from basebert import Herberror
import xml.etree.ElementTree
import re

__all__ = ['tx_assert', 'load_xml', 'search_for', 't_arr_to_bytes']


def load_xml(url):
    res = hercurles_network._t_load_str(url)
    res = re.sub("xmlns=\".*?\"", "", res)
    return xml.etree.ElementTree.fromstring(res)


def search_for(searchterm):
    query = f"https://duckduckgo.com/html/?q={searchterm}"
    root = load_xml(query)

    elems = root.findall(".//a[@class='result__snippet']")

    return [elem.attrib['href'] for elem in elems]


def t_arr_to_bytes(arr):
    return bytes(" ".join(arr), encoding="utf-8")


def tx_assert(condition, msg):
    if not condition:
        raise Herberror(msg)
