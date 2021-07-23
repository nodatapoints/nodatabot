import requests

from basebert import BaseBert
from herberror import Herberror
from common.chatformat import link_to
from decorators import aliases, command, doc


class WikiRequestFailure(Exception):
    """
    Raised if the wiki api is not reachable or returns
    failure
    """


URL = 'https://en.wikipedia.org/w/api.php'


def find_extracts(query):
    """
    Wiki api call
    lookup the short extract for an article
    """
    params = {
        'action': 'query',
        'prop': 'extracts',
        'exintro': '1',
        'explaintext': '1',
        'format': 'json',
        'titles': query,
        'redirects': '1'
    }

    res = requests.get(URL, params)

    if res.ok:
        return res.json()
    raise WikiRequestFailure()


def find_url(pageid):
    """
    Wiki api call
    lookup the url for a given pageid
    """
    params = {
        'action': 'query',
        'prop': 'info',
        'inprop': 'url',
        'pageids': pageid,
        'format': 'json'
    }

    res = requests.get(URL, params)

    pages = res.json()['query']['pages']

    if len(pages) != 1:
        raise WikiRequestFailure()

    page, = pages.values()
    return page['fullurl']


class WikiBert(BaseBert):
    """
    Expose wiki api calls as bot commands
    """

    @aliases('wiki', 'w')
    @command(pass_string=True)
    @doc("""Search for a thing on wikipedia""")
    def getwikipage(self, query):
        """
        Use the wiki api calls to return some
        relevant information for the search query
        """
        try:
            extracts = find_extracts(query)
            print(extracts)

            pages = extracts.get('query', dict()).get('pages', None)
            if pages is None:
                self.send_message("No Data")
                return

            for k, val in pages.items():
                link = find_url(k)
                title = val['title']
                extract = val['extract']
                self.send_message(f'{link_to(link, title)}\n{extract}')

        except WikiRequestFailure as err:
            raise Herberror("Failure performing WikiMedia API Request") from err
        except Exception as err:
            raise Herberror("Unexpected failure performing WikiMedia API Request (invalid response format?)") from err
