from decorators import aliases, command
from basebert import BaseBert, Herberror


import requests
from requests.utils import quote
from scrapy.http import HtmlResponse
from lxml import etree


class Dudert(BaseBert):
    @aliases('urban', 'dict')
    @command(pass_string=True)
    def urbandict(self, string):
        """
        Have unknown words given as strings explained to you

        The UrbanDictionary utility makes use of the website "www.urbandictionary.com".\
        It is specialized for the quick explanation of common abbreviations and slang \
        of the youth that you do not understand.

        e.g `/urban top kek`
        """
        phrase = quote(string, safe='')
        url = f'https://www.urbandictionary.com/define.php?term={phrase}'
        response = requests.get(url)
        site = HtmlResponse(url=response.url, body=response.content)

        def join_chunked(xpath):
            div = site.xpath(xpath)[0]
            chunks = div.xpath('.//text()').extract()
            return ''.join(chunks)
        try:
            title = site.xpath('//a[@class="word"]/text()').extract_first()
            meaning = join_chunked('//div[@class="meaning"]')
            example = join_chunked('//div[@class="example"]')
        except Exception:
            raise Herberror('This is not a valid query')

        outp = f'`{title}:`\n{meaning}\n_{example}_'
        self.reply_text(outp)

    @aliases('dude')
    @command(pass_string=True)
    def dudensearch(self, query):
        """
        Searches for a given query in the online German dictionary duden.de, and displays the top result.\
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
        _, *meanings = dom.xpath(
                '//section[@id="block-duden-tiles-1"]//a/text()')

        meanings_list_str = '\n'.join(
            f'{i+1}. _{meaning}_' for i, meaning in enumerate(meanings)) or '_Keine Bedeutungen gefunden._'
        return f"""*{word_def}*
_{word_class}_
Häufigkeit: {'💬'*len(freq)}

Bedeutungen:
{meanings_list_str}"""
