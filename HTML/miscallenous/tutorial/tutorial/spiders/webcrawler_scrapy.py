import scrapy
from scrapy.spiders import CrawlSpider


class QuoteSpider(CrawlSpider):

    name = 'quotes'

    start_urls = ['http://quotes.toscrape.com/']

    allowed_domains = ['quotes.toscrape.com']


    def parse_start_url(self, response):

        for quote in response.css('div.quote'):

            # yield {
            #     'quote':  quote.css('span.text::text').extract_first(),
            #     'author': quote.css('small::text').extract_first()
            #     }
            #
            # author_link = 'http://quotes.toscrape.com' + quote.css('a::attr(href)').extract_first()

            yield scrapy.Request(author_link, callback=self.parse_author_info)


    def parse_author_info(self, response):

        print response.css('span.author-born-date::text').extract_first()
