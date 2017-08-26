from scrapy import Item, Field


class reddit_item(Item):
    User = Field()
    Title = Field ()
    url = Field ()
    # define the fields for your item here like:
    # name = scrapy.Field()
