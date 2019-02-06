from common import network
from basebert import Herberror
from urllib.parse import quote
import re
import json

from lxml import etree

from common.network import NetworkError

parser = etree.XMLParser(recover=True)

__all__ = ['load_json', 'load_xml', 'search_for']


def load_json(url, **kwargs):
    res = network.load(url, **kwargs).data
    return json.loads(res)


def load_xml(url, **kwargs):
    res = network.load_str(url, **kwargs)
    res = re.sub('xmlns=".*?"', " ", res)
    return etree.fromstring(res, parser=parser)


SPACES = "\\s+"
PLUS = "+"


def search_for(query):
    # TODO properly escape this query
    url = f"https://duckduckgo.com/html/?q={quote(re.sub(SPACES, PLUS, query))}"

    try:
        root = load_xml(url)

        elements = root.findall(".//a[@class='result__snippet']")

        return [elem.attrib['href'] for elem in elements]

    except etree.ParseError:
        raise Herberror("Searching failed. Unexpected result structure.")

    except NetworkError:
        raise Herberror("Searching failed because of network problems.")
