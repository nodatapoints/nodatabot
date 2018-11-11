from common import network
from basebert import Herberror
from urllib.parse import quote
import re

from lxml import etree

from common.network import NetworkError

parser = etree.XMLParser(recover=True)

__all__ = ['tx_assert', 'load_xml', 'search_for', 't_arr_to_bytes']


def load_xml(url, **kwargs):
    res = network.t_load_str(url, **kwargs)
    res = re.sub('xmlns=".*?"', " ", res)
    return etree.fromstring(res, parser=parser)


SPACES = "\\s+"
PLUS = "+"


def search_for(query):
    # TODO properly escape this query
    url = f"https://duckduckgo.com/html/?q={quote(re.sub(SPACES, PLUS, query))}"

    try:
        root = load_xml(url)
    except NetworkError:
        raise Herberror("Searching failed because of network problems.")

    elements = root.findall(".//a[@class='result__snippet']")

    return [elem.attrib['href'] for elem in elements]


def t_arr_to_bytes(arr):
    return bytes(" ".join(arr), encoding="utf-8")


def tx_assert(condition, msg, err_class=Herberror):
    if not condition:
        raise err_class(msg)
