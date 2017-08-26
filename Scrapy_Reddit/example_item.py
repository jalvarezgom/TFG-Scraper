from scrapy import Item, Field


class reddit_item(Item):
    User = Field()
    Title = Field ()
    url = Field ()