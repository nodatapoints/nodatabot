from common import network
from basebert import Herberror
from urllib.parse import quote
import re

from lxml import etree

from common.network import NetworkError

parser = etree.XMLParser(recover=True)

__all__ = ['load_xml', 'search_for']


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
