# -*- coding: utf-8 -*-
import scrapy
import json
import re
from jd_comment_tag_total.items import JdCommentTagTotalItem
from jd_comment_tag_total.settings import CAT
import time

class CommentTagTotalSpider(scrapy.Spider):
    name = 'comment_tag_total'
    allowed_domains = ['jd.com']

    def start_requests(self):
        for i in range(len(CAT)):
            url = CAT[i]
            yield scrapy.Request(url, callback=self.parse)

    def parse(self, response):
        if response.status == 302:
            print('-*-*-*- 重定向至其他页面,重新请求 -*-*-*-')
            print('----- 重定向网址为：-----', response.url)
            print(response.text[:1000])
            time.sleep(5)
            yield scrapy.Request(response.url, callback=self.get_tags, dont_filter=True)
        else:
            try:
                if 'class="p-num"' in response.text:
                    page = int(response.xpath('//span[@class="p-num"]/a/text()').extract()[-2])
                else:
                    print(response.url)
                    page = 100
                for i in range(1, page + 1):
                    url = response.url + '&page=' + str(i) + '&sort=sort_totalsales15_desc'
                    yield scrapy.Request(url, callback=self.get_items_url)
            except Exception as e:
                print('---------------------')
                print(e)
                print('---------------------')

    def get_items_url(self, response):
        if response.status == 302 :
            print('-*-*-*- 重定向至其他页面,重新请求 -*-*-*-')
            print('----- 重定向网址为：-----', response.url)
            print(response.text[:1000])
            time.sleep(5)
            yield scrapy.Request(response.url, callback=self.get_tags, dont_filter=True)
        else:
            item_list = response.xpath('//li[@class="gl-item"]').extract()
            for i in item_list:
                sku_id = re.findall('\/(\d+).html', i)[0]
                if '全球购' in i:
                    url = """https://club.jd.com/productpage/p-{sku_id}-s-3-t-1-p-0.html""".format(sku_id=sku_id)
                else:
                    url = """https://sclub.jd.com/comment/productPageComments.action?&productId={sku_id}&score=1&sortType=5&page=0&pageSize=10&isShadowSku=0&fold=1""" \
                        .format(sku_id=sku_id)
                yield scrapy.Request(url, callback=self.get_tags, meta={'sku_id': sku_id})

    def get_tags(self,response):
        if response.status == 302:
            print('-*-*-*- 重定向至其他页面,重新请求 -*-*-*-')
            print('----- 重定向网址为：-----', response.url)
            print(response.text[:1000])
            time.sleep(5)
            yield scrapy.Request(response.url, callback=self.get_tags,
                                 meta={'sku_id': response.meta['sku_id'],
                                       'score': response.meta['score']}, dont_filter=True)
        else:
            sku_id = response.meta['sku_id']
            commment_dict = json.loads(response.text)
            hot_tag = commment_dict['hotCommentTagStatistics']
            tag_num = len(hot_tag)
            for i in range(tag_num):
                tag_item = JdCommentTagTotalItem()
                tag_item['tag_num'] = tag_num
                tag_item['tag_name'] = hot_tag[i]['name']
                tag_item['tag_count'] = hot_tag[i]['count']
                tag_item['sku_id'] = int(sku_id)
                yield tag_item

