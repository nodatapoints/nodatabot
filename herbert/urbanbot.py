import requests
from scrapy.http import HtmlResponse
from urllib.parse import quote

from decorators import *
from basebert import Herberror

class UrbanBert():
	@aliases('urban', 'dict')
	@command
	def urbandict(self, args):
		"""
		Have unknown words given as strings explained to you
		"""
		url = f'https://www.urbandictionary.com/define.php?term={phrase}'
		response = requests.get(url)
		site = HtmlResponse(url=response.url, body=response.content)


		def join_chunked(xpath):
    		div = site.xpath(xpath)[0]
    		chunks = div.xpath('.//text()').extract()
    		return ''.join(chunks)

    	title = site.xpath('//a[@class="word"]/text()').extract_first()
    	meaning = join_chunked('//div[@class="meaning"]')
    	example = join_chunked('//div[@class="example"]')

    	self.reply_text(f'**{title}:**\n{meaning}\n__{example}__')















