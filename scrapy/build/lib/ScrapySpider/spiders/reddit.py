import scrapy
from ScrapySpider.reddit_item import reddit_item

class QuotesSpider(scrapy.Spider):
    name = "reddit"
    """allowed_domains=[
        'https://www.reddit.com'
    ]"""
    start_urls = [
        'https://www.reddit.com/r/pcgaming/'
    ]

    def parse(self, response):
        for topic in response.css("div.thing"):
            item = reddit_item()
            item['user'] = topic.css("a.title::text").extract_first()
            item['title'] = topic.css("a.author::text").extract_first()
            url=topic.css("a.title::attr(href)").extract_first()
            if url[:4] != "http":
                url = "https://www.reddit.com" + url
            item['url'] = url

            request = scrapy.Request(url,callback=self.parse_topic)
            request.meta['item']=item
            yield request


    def parse_topic(self, response):
        text = response.css("div.entry div.expando p::text").extract()
        item = response.meta['item']
        item['content']= text
        """print(item)"""
        yield item




