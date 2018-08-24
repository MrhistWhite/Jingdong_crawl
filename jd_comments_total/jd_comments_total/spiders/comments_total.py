# -*- coding: utf-8 -*-
import scrapy
from jd_comments_total.items import JdCommentsTotalItem
import json
import re
from jd_comments_total.settings import CAT
import time

class CommentsTotalSpider(scrapy.Spider):
    name = 'comments_total'
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
            yield scrapy.Request(response.url,callback=self.comments_total,dont_filter=True)
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
        if response.status == 302:
            print('-*-*-*- 重定向至其他页面,重新请求 -*-*-*-')
            print('----- 重定向网址为：-----', response.url)
            print(response.text[:1000])
            time.sleep(5)
            yield scrapy.Request(response.url, callback=self.comments_total,
                                 dont_filter=True)
        else:
            item_list = response.xpath('//li[@class="gl-item"]').extract()
            for i in item_list:
                sku_id = re.findall('\/(\d+).html', i)[0]
                if '全球购' in i:
                    url = """https://club.jd.com/productpage/p-{sku_id}-s-3-t-1-p-0.html""".format(sku_id=sku_id)
                else:
                    url = """https://sclub.jd.com/comment/productPageComments.action?&productId={sku_id}&score=1&sortType=5&page=0&pageSize=10&isShadowSku=0&fold=1""" \
                    .format(sku_id=sku_id)
                yield scrapy.Request(url, callback=self.comments_total,meta={'sku_id':sku_id})

    def comments_total(self, response):
        if response.status == 302:
            print('-*-*-*- 重定向至其他页面,重新请求 -*-*-*-')
            print('----- 重定向网址为：-----', response.url)
            print(response.text[:1000])
            time.sleep(5)
            yield scrapy.Request(response.url,callback=self.comments_total, meta={'sku_id':response.meta['sku_id']},dont_filter=True)
        else:
            sku_id = response.meta['sku_id']
            try:
                comment_total = JdCommentsTotalItem()
                comment_dict = json.loads(response.text)
                productCommentSummary = comment_dict['productCommentSummary']
                comment_total['comment_num'] = productCommentSummary['commentCount']  # 评价总数
                comment_total['good_comment_rate'] = productCommentSummary['goodRate']  # 好评率
                comment_total['good_comment'] = productCommentSummary['goodCount']  # 好评数
                comment_total['general_count'] = productCommentSummary['generalCount']  # 中评数
                comment_total['poor_count'] = productCommentSummary['poorCount']  # 差评数
                comment_total['default_comment_num'] = productCommentSummary['defaultGoodCount']  # 默认好评数
                comment_total['sku_id'] = int(sku_id)
                yield comment_total
            except Exception as e:
                print(e)
                print(response.url)

    # sku
    def get_sku(self, response):
        try:
            choose = re.findall('colorSize: \[(.*?)\]', response.text)[0]
            sku_list = re.findall('"skuId":(\d+)', choose)
        except:
            sku_list = []
        return sku_list