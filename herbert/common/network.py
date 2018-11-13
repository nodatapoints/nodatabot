import urllib3
import certifi
import re

from urllib.parse import quote
from basebert import Herberror

# fake it 'til you make it
from common.herbert_utils import tx_assert

__all__ = ['load', 'load_str', 'load_content', 'gen_filename_from_url', 'is_image_content_type',
           'NetworkError']

USER_AGENT = {'user-agent': 'Mozilla/5.0 (X11; Linux i686; rv:64.0) Gecko/20100101 Firefox/64.0'}
USER_AGENT_CURL = {'user-agent': 'curl/7.58.0'}

# CONSTANTS
RESPONSE_STAT_ERR = "Invalid Response status"
NO_RESPONSE_ERR = "Could not connect to specified URL."
NOT_TEXT_ERR = "The requested web page couldn't be converted to text."

HTTP_STAT_OK = 200
REQUEST_TYPE_GET = "GET"

# GLOBAL
urllib3.disable_warnings()
http = urllib3.PoolManager(10, USER_AGENT, cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())

http_plain = urllib3.PoolManager(10, USER_AGENT_CURL, cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())


class NetworkError(Herberror):
    """ Signal that some connection or request went wrong """


def load(url, fake_ua=True):
    """
    Interacts with urllib3 to send a GET request to a given URL.

    @brief retrieve the contents of a given website
    @param url the url to look up
    @param fake_ua if set to true (default), use a firefox user-agent string
    @returns a response obj containing the data, if the lookup
             was successful
    @throws a NetworkError containing a description, if the
            lookup failed
    """
    try:
        if fake_ua:
            return http.request(REQUEST_TYPE_GET, url, retries=2)
        else:
            return http_plain.request(REQUEST_TYPE_GET, url, retries=2)

    except urllib3.exceptions.HTTPError:
        raise NetworkError(NO_RESPONSE_ERR)


def load_str(url, **kwargs):
    """"
    loads a web page and tries to convert it to text

    @brief make a string from load()
    @param url the url to look up
    @returns a string containing the data, if the lookup
             was successful
    @throws a NetworkError containing a description, if the
            lookup failed

    """
    res = load(url, **kwargs)

    tx_assert(res.status == HTTP_STAT_OK,
              f"{RESPONSE_STAT_ERR}: {res.status}\nResponse Header: `{res.headers}`",
              err_class=NetworkError)

    charset = response_extract_charset(res.headers)

    try:
        return res.data.decode(charset or 'utf-8')

    except UnicodeDecodeError:
        raise Herberror(NOT_TEXT_ERR)


def load_content(url, **kwargs):
    """
    loads a web page from url, figures out the content type
    and returns it together with the pure binary data

    @brief get data and data type of a web page
    @param url the url to look up
    @returns a tuple of a content_type string and a binary data string
    """
    res = load(url, **kwargs)

    tx_assert(res.status == HTTP_STAT_OK, f"{RESPONSE_STAT_ERR}: {res.status}", err_class=NetworkError)

    content_type = res.headers.get("Content-Type")
    content_type = re.split(";", content_type)[0]

    return content_type, res.data


def is_image_content_type(content_type):
    """
    @brief Checks whether content_type is the content type of an image
    @param content_type a utf8 encoded string
    @returns a boolean value depending on whether or not content_type
             is an image
    """
    return content_type.startswith("image")


_ending = {
    "text/plain": "txt",
}


def gen_filename_from_url(url, content_type="text/plain"):
    """
    When replying with a file (@see t_reply_filed),
    the file needs to get a name. in this context,
    the filename should reflect the original request
    url. This function encodes the url to allow it
    to be used as a filename

    @brief Converts a url to a filename
    @param url some url string
    @param content_type the content_type string from
           an http-header. used to determine filename suffixes.
    @returns an arbitrary string meant to reflect the
             url and represent a file.
    """
    return re.sub("[:/ \t\n]", "_", url) + "." + _ending.get(content_type, re.split("/", content_type)[1])


def response_extract_charset(response_header):
    """
    figure out the response character encoding from an http-
    header, if any.

    @brief get the character encoding from a header
    @param response_header a urllib3 response header
    @returns a string containing the name of the encoding
             or None if no encoding could be found.
    """
    base = response_header.get("Content-Type")
    try:
        value = re.split("charset=", base)[1]
        value = re.split("(; ,)", value)[0]
        return value or None

    except IndexError:
        return None


def get_url_safe_string(inn):
    return quote(inn, safe='')
