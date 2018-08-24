# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class JdCategoryItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    sku_id = scrapy.Field()
    name = scrapy.Field()
    parent_level = scrapy.Field()
    cat = scrapy.Field()
    last_cat = scrapy.Field()
