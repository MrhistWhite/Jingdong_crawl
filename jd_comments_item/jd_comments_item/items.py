# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class JdCommentsItemItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    sku_id = scrapy.Field()
    comment_context = scrapy.Field()
    comment_time = scrapy.Field()
    comment_score = scrapy.Field()
    token = scrapy.Field()
    comment_level = scrapy.Field()
    referenceName = scrapy.Field()
    afterdays = scrapy.Field()
    ismobile = scrapy.Field()
    mobileVersion = scrapy.Field()
    userClientShow = scrapy.Field()
    userLevelName = scrapy.Field()
    days = scrapy.Field()
    recommend = scrapy.Field()
    plusAvailable = scrapy.Field()
    anonymousFlag = scrapy.Field()
    guid = scrapy.Field()
    referenceTime = scrapy.Field()
    referenceType = scrapy.Field()
    referenceTypeId = scrapy.Field()
    title = scrapy.Field()
    usefulVoteCount = scrapy.Field()
    uselessVoteCount = scrapy.Field()
    replyCount = scrapy.Field()
    replyCount2 = scrapy.Field()
    userLevelId = scrapy.Field()
    userProvince = scrapy.Field()
    viewCount = scrapy.Field()
    orderId = scrapy.Field()
    isReplyGrade = scrapy.Field()
    nickname = scrapy.Field()
    userClient = scrapy.Field()
    userImgFlag = scrapy.Field()
    add_content = scrapy.Field()
    reference_id = scrapy.Field()