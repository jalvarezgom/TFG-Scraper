import scrapy


class tutorialSpider(scrapy.Spider):
    name = "tutorial"
    start_urls = [
        'http://quotes.toscrape.com/page/1/',
    ]


    def parse(self, response):
        for quote in response.css("div.quote"):
            yield {
                'text':quote.css("span.text::text").extract_first(),
                'author':quote.css("small.author::text").extract_first(),
                'tags':quote.css("a.tag::text").extract()
            }

        siguiente=response.css('li.next a::attr(href)').extract_first()
        if siguiente is not None:
            print (siguiente)
            yield response.follow(siguiente, callback=self.parse)


