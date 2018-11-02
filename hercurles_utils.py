import hercurles as H
import xml.etree.ElementTree as ET
import re

__all__ = ['load_xml', 'search_for']


def load_xml(url):
    res = H._t_load_str(url)
    res = re.sub("xmlns=\".*?\"", "", res)
    return ET.fromstring(res)


def search_for(searchterm):
    query = f"https://duckduckgo.com/html/?q={searchterm}"
    root = load_xml(query)

    elems = root.findall(".//a[@class='result__snippet']")

    return [elem.attrib['href'] for elem in elems]




