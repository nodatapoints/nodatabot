import requests
from scrapy.http import HtmlResponse
from urllib.parse import quote

from decorators import *
from basebert import Herberror, BaseBert


class UrbanBert(BaseBert):
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
            raise Herberror('This is probably not a valid query')

        outp = f'`{title}:`\n{meaning}\n_{example}_'
        self.reply_text(outp)
