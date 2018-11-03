import hercurles
import xml.etree.ElementTree
import re

__all__ = ['load_xml', 'search_for', '_t_bytes']


def load_xml(url):
    res = hercurles._t_load_str(url)
    res = re.sub("xmlns=\".*?\"", "", res)
    return xml.etree.ElementTree.fromstring(res)


def search_for(searchterm):
    query = f"https://duckduckgo.com/html/?q={searchterm}"
    root = load_xml(query)

    elems = root.findall(".//a[@class='result__snippet']")

    return [elem.attrib['href'] for elem in elems]


def _t_bytes(arr):
    return bytes(" ".join(arr), encoding="utf-8")

