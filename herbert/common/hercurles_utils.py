"""
Provide a number of network helpers
Originally meant for berts.hercurles, but
also used in different contexts
"""
from urllib.parse import quote
import re
import json
from dataclasses import dataclass

from lxml import etree

from common import network
from common.network import NetworkError
from herberror import Herberror


PARSER = etree.XMLParser(recover=True)

__all__ = ['load_json', 'load_xml', 'search_for']


def load_json(url: str, **kwargs):
    """
    Load the content of the given url and try to
    convert it into a JSON-representation
    """
    res = network.load(url, **kwargs).data
    return json.loads(res)


def load_xml(url: str, **kwargs):
    """
    Load the content of the given url and try to
    convert it into a XML-representation
    """
    res = network.load_str(url, **kwargs)
    res = re.sub('xmlns=".*?"', " ", res)
    return etree.fromstring(res, parser=PARSER)


SPACES = "\\s+"
PLUS = "+"

@dataclass
class SearchResult:
    url: str
    title: str


def search_for(query: str):
    """
    Look up the given search term on duckduckgo and return
    a list of the results from the first page
    """
    url = f"https://duckduckgo.com/html/?q={quote(re.sub(SPACES, PLUS, query))}"

    try:
        root = load_xml(url)

        find_urls = etree.XPath(
            ".//div[re:test(@class, 'web-result', 'i')]//a[@class='result__a']",
            namespaces=dict(re='http://exslt.org/regular-expressions')
        )

        elements = find_urls(root)
        return [elem.attrib['href'] for elem in elements]

    except etree.ParseError as err:
        raise Herberror("Searching failed. Unexpected result structure.") from err

    except NetworkError as err:
        raise Herberror("Searching failed because of network problems.") from err
