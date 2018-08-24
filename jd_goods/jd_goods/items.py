# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class JdGoodsItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    base_price = scrapy.Field()
    end_cat = scrapy.Field()
    e_name = scrapy.Field()
    origin = scrapy.Field()
    spec = scrapy.Field()
    packing = scrapy.Field()
    keep_days = scrapy.Field()
    unit = scrapy.Field()
    name = scrapy.Field()
    sku_id = scrapy.Field()
    cat_name = scrapy.Field()
    pre_sku_id = scrapy.Field()
    pos = scrapy.Field()
    sub_title = scrapy.Field()
    title = scrapy.Field()
