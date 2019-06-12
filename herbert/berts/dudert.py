from decorators import aliases, command, doc
from basebert import BaseBert
from herberror import Herberror
import common.chatformat as cf


import requests
from requests.utils import quote
from lxml import etree


class Dudert(BaseBert):
    @aliases('urban', 'dict')
    @command(pass_string=True)
    @doc(
        """
        Have unknown words given as strings explained to you

        The UrbanDictionary utility makes use of the website "www.urbandictionary.com".\
        It is specialized for the quick explanation of common abbreviations and slang \
        of the youth that you do not understand.

        e.g: m§/urban top kek§
        """
    )
    def urbandict(self, string):
        phrase = quote(string, safe='')
        url = f'https://www.urbandictionary.com/define.php?term={phrase}'
        response = requests.get(url)
        dom = etree.HTML(response.text)

        def join_chunked(xpath):
            div = dom.xpath(xpath)[0]
            return ''.join(div.xpath('.//text()'))

        try:
            title = dom.xpath('//a[@class="word"]/text()')[0]
            meaning = join_chunked('//div[@class="meaning"]')
            example = join_chunked('//div[@class="example"]')

        except IndexError:
            # Check if its just the "not defined yet" page
            if dom.xpath('//a[text()="Define it!"]'):
                self.send_message(
                    msg=f"""\
{cf.italic("This is not defined yet!")}
{cf.link_to(f"https://www.urbandictionary.com/add.php?term={phrase}", "Want to define it?")}"""
                )
                return

            else:  # if not, its a problem
                raise

        self.send_message(f"""\
{cf.mono(title)}
{meaning}
{cf.italic(example)}""")

    @aliases('dude')
    @command(pass_string=True)
    @doc(
        """
        Searches for a given query in the online German dictionary duden.de, and displays the top result.

        The Duden utility makes use of the website "www.duden.de".\
        It is specialized for bare definitions of proper german words you could find in a dictionary, too.

        e.g: m§/dudensearch Baum§
        """
    )
    def dudensearch(self, query):
        url = f'http://www.duden.de/suchen/dudenonline/{quote(query)}'
        listing = requests.get(url)
        if not listing.ok:
            raise Herberror(f'Could not fetch "{url}"')

        dom = etree.HTML(listing.text)

        # All links pointing to a word definition Page
        results = dom.xpath('//strong/parent::a/@href')

        if not results:
            raise Herberror('Gibts nicht.')

        top_entry, *_ = results

        msg = self._parse_definition(url='http://www.duden.de/'+top_entry)
        self.send_message(msg)

    def _parse_definition(self, *, word=None, url=None):
        """
        Creates a full Telegram message containing information about a
        word. The word is either passed as `word` as itself, or in an already
        formatted url pointing to the definition page.
        """
        if word:
            url = f'http://www.duden.de/rechtschreibung/{requests.utils.quote(word)}'

        elif not url:
            raise ValueError('No valid arguments given.')

        definition_page = requests.get(url)
        definition_page.raise_for_status()

        dom = etree.HTML(definition_page.text)

        word_def = ', '.join(dom.xpath('//h1/span/text()'))
        word_class, *_ = dom.xpath('//dd[@class="tuple__val"]/text()')

        freq = dom.xpath('//span[@class="shaft__full"]/text()')[0]

        # check for single definition
        meanings = dom.xpath('//div[@id="bedeutung"]/p/text()')

        # TODO auslagern
        if not meanings:
            # if there are mutliple definitions, parse them
            for elem in dom.xpath('//div[@class="enumeration__text"]'):
                text = ''.join(elem.xpath('./descendant-or-self::*/text()'))
                if not text.strip():
                    continue
                meanings.append(text)

        meanings_list_str = '\n'.join(
            f'{i+1}. {cf.italic(meaning)}' for i, meaning in enumerate(meanings)) or cf.italic("Keine Bedeutungen gefunden.")
        return f"""{cf.bold(word_def)}
{cf.italic(word_class)}
Häufigkeit: {'💬'*len(freq)}

Bedeutungen:
{meanings_list_str}"""
