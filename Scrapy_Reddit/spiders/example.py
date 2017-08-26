import scrapy


class tutorialSpider(scrapy.Spider):
    name = "tutorial"
    start_urls = [
        'http://quotes.toscrape.com/page/1/',
        'http://quotes.toscrape.com/page/2/',
    ]


    def parse(self, response):
        for quote in response.css("div.quote"):
            yield {
                'text':quote.css("span.text::text").extract_first(),
                'author':quote.css("small.author::text").extract_first(),
                'tags':quote.css("a.tag::text").extract()
            }

            #print(quote.css("span.text::text").extract_first())
            #print(quote.css("small.author::text").extract_first())
            #print(quote.css("a.tag::text").extract())



''' Forma antigua
    def start_requests(self):
        urls = [
            'http://quotes.toscrape.com/page/1/',
            'http://quotes.toscrape.com/page/2/',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)
'''