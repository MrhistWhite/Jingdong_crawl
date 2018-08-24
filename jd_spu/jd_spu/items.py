# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class JdSpuItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    goods_name = scrapy.Field()
    end_cat = scrapy.Field()
    sku_id = scrapy.Field()
    spu_name = scrapy.Field()
    value = scrapy.Field()
    cat_name = scrapy.Field()
    pre_sku_id = scrapy.Field()
