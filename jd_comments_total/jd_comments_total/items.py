# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class JdCommentsTotalItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    sku_id = scrapy.Field()
    comment_num = scrapy.Field()
    good_comment_rate = scrapy.Field()
    good_comment = scrapy.Field()
    general_count = scrapy.Field()
    poor_count = scrapy.Field()
    default_comment_num = scrapy.Field()
