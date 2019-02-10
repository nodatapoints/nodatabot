from decorators import aliases, command
from basebert import BaseBert, Herberror


import requests
from requests.utils import quote
from lxml import etree


class Dudert(BaseBert):
    @aliases('dude')
    @command(pass_string=True)
    def dudensearch(self, query):
        """
        Searches for a given query in the online
        German dictionary duden.de, and displays the top result.
        """

        url = f'http://www.duden.de/suchen/dudenonline/{quote(query)}'
        listing = requests.get(url)
        if not listing.ok:
            raise Herberror(f'Could not fetch "{url}"')

        dom = etree.HTML(listing.text)

        # All links pointing to a word definition Page
        results = dom.xpath('//a[.="Zum vollständigen Artikel"]/@href')

        if not results:
            raise Herberror('Gibts nicht.')

        top_entry, *_ = results

        msg = self._parse_definition(url=top_entry)
        self.send_message(msg, parse_mode='MARKDOWN')

    def _parse_definition(self, *, word=None, url=None):
        """
        Creates a full Telegram message containing information about a
        word. The word is either passed as `word` as itself, or in an already
        formatted url pointig to the definition page.
        """
        if word:
            url = f'http://www.duden.de/rechtschreibung/{quote(word)}'

        elif not url:
            raise ValueError('No valid arguments given.')

        definition_page = requests.get(url)
        definition_page.raise_for_status()

        dom = etree.HTML(definition_page.text)

        main_block, *_ = dom.xpath('//section[@id="block-system-main"]')
        word_def, = main_block.xpath('./h1/text()')
        word_class, *_, freq = main_block.xpath('.//strong/text()')
        _, *meanings = dom.xpath('//section[@id="block-duden-tiles-1"]//a/text()')

        meanings_list_str = '\n'.join(f'{i+1}. _{meaning}_' for i, meaning in enumerate(meanings)) or '_Keine Bedeutungen gefunden._'
        return f"""*{word_def}*
_{word_class}_
Häufigkeit: {'💬'*len(freq)}

Bedeutungen:
{meanings_list_str}"""
