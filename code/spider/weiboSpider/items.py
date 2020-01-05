# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class WeibospiderItem(scrapy.Item):

    id = scrapy.Field()
    scheme = scrapy.Field()
    create_time = scrapy.Field()
    text = scrapy.Field()
    text_length = scrapy.Field()
    user0 = scrapy.Field()
    comments = scrapy.Field()
