from scrapy import Item, Field


class reddit_item(Item):
    user = Field()
    title = Field ()
    content = Field ()
    url = Field ()
    # define the fields for your item here like:
    # name = scrapy.Field()
