# -*- coding: utf-8 -*-
import scrapy
import hashlib
from jd_comments_item.items import JdCommentsItemItem
import json
import datetime
import time
import re
from jd_comments_item.settings import CAT

class CommentsItemSpider(scrapy.Spider):
    name = 'comments_item'
    allowed_domains = ['jd.com']

    def start_requests(self):
        for i in range(len(CAT)):
            url = CAT[i]
            yield scrapy.Request(url,callback=self.parse)

    def parse(self, response):
        if response.status == 302:
            print('-*-*-*- 重定向至其他页面,重新请求 -*-*-*-')
            print('----- 重定向网址为：-----', response.url)
            print(response.text[:1000])
            time.sleep(5)
            yield scrapy.Request(response.url,callback=self.parse, dont_filter=True)
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
            yield scrapy.Request(response.url, callback=self.get_items_url,
                                 dont_filter=True)
        else:
            item_list = response.xpath('//li[@class="gl-item"]').extract()
            for i in item_list:
                sku_id = re.findall('\/(\d+).html', i)[0]
                for j in range(1,4):
                    if '全球购' in i:
                        url = """https://club.jd.com/productpage/p-{sku_id}-s-{score}-t-1-p-0.html""".format(sku_id=sku_id,score=j)
                    else:
                        url = 'https://sclub.jd.com/comment/productPageComments.action?&productId={goods_id}&score={score}&sortType=5&page={page}&pageSize=10' \
                            .format(goods_id=sku_id, page=0, score=j)
                    yield scrapy.Request(url, callback=self.get_comments, meta={'score': j, 'sku_id': sku_id})

    def get_comments(self, response):
        score = response.meta['score']
        sku_id = response.meta['sku_id']
        comment_dict = json.loads(response.text)
        maxpage = comment_dict['maxPage']
        if response.status == 302:
            print('-*-*-*- 重定向至其他页面,重新请求 -*-*-*-')
            print('----- 重定向网址为：-----', response.url)
            print(response.text[:1000])
            time.sleep(5)
            yield scrapy.Request(response.url,callback=self.get_comments, meta={'score': score, 'sku_id': sku_id},dont_filter=True)
        elif maxpage != 0:
            for i in range(maxpage):
                if 'sclub' in response.url:
                    url = 'https://sclub.jd.com/comment/productPageComments.action?&productId={goods_id}&score={score}&sortType=5&page={page}&pageSize=10' \
                        .format(goods_id=sku_id, page=i, score=score)
                else:
                    url = """https://club.jd.com/productpage/p-{sku_id}-s-{score}-t-1-p-{page}.html""".format(sku_id=sku_id,score=score,page=i)
                yield scrapy.Request(url,callback=self.comment_item_content, meta={'sku_id':sku_id, 'score': score})
        else:
            return

    def comment_item_content(self,response):
        if response.status == 302:
            print('-*-*-*- 重定向至其他页面,重新请求 -*-*-*-')
            print('----- 重定向网址为：-----', response.url)
            print(response.text[:1000])
            time.sleep(5)
            yield scrapy.Request(response.url, callback=self.comment_item_content, meta={'sku_id': response.meta['sku_id'],
                                                                    'score':response.meta['score']},dont_filter=True)
        else:
            score = response.meta['score']
            comment_item = JdCommentsItemItem()
            comment_dict = json.loads(response.text)
            content_list = comment_dict['comments']
            for i in range(len(content_list)):
                print('-------------------Comment_item crawling-------------------')
                content = content_list[i]
                comment_item['comment_context'] = content['content']  # 评价内容
                comment_item['comment_time'] = datetime.datetime.strptime(content['creationTime'],
                                                                          '%Y-%m-%d %H:%M:%S')  # 评价时间
                comment_item['comment_score'] = content['score']  # 评价星级
                comment_item['comment_level'] = score  # 评价等级
                comment_item['sku_id'] = response.meta['sku_id']
                comment_item['reference_id'] = int(content['referenceId'])
                comment_item['referenceName'] = content['referenceName']
                comment_item['ismobile'] = int(content['isMobile'])
                comment_item['afterdays'] = content['afterDays']
                comment_item['mobileVersion'] = content['mobileVersion']
                comment_item['userClientShow'] = re.sub('来自','',content['userClientShow'])
                comment_item['userLevelName'] = content['userLevelName']
                comment_item['days'] = content['days']
                comment_item['recommend'] = int(content['recommend'])
                comment_item['plusAvailable'] = content['plusAvailable']
                comment_item['anonymousFlag'] = content['anonymousFlag']
                comment_item['guid'] = content['guid']
                comment_item['referenceTime'] = datetime.datetime.strptime(content['referenceTime'],
                                                                          '%Y-%m-%d %H:%M:%S')
                comment_item['referenceType'] = content['referenceType']
                comment_item['referenceTypeId'] = content['referenceTypeId']
                try:
                    comment_item['title'] = content['title']
                except:
                    comment_item['title'] = ''
                comment_item['usefulVoteCount'] = content['usefulVoteCount']
                comment_item['uselessVoteCount'] = content['uselessVoteCount']
                comment_item['replyCount'] = content['replyCount']
                comment_item['replyCount2'] = content['replyCount2']
                comment_item['userLevelId'] = content['userLevelId']
                comment_item['userProvince'] = content['userProvince']
                comment_item['viewCount'] = content['viewCount']
                comment_item['orderId'] = content['orderId']
                comment_item['isReplyGrade'] = int(content['isReplyGrade'])
                comment_item['nickname'] = content['nickname']
                comment_item['userClient'] = content['userClient']
                comment_item['userImgFlag'] = content['userImgFlag']
                if 'afterUserComment' in content.keys():
                    comment_item['add_content'] = content['afterUserComment']['hAfterUserComment']['content']
                else:
                    comment_item['add_content'] = ''
                h1 = hashlib.md5()
                token_raw = str(comment_item['comment_context']) + comment_item['guid'] + str(comment_item['sku_id']) + \
                            str(comment_item['comment_score']) + str(comment_item['comment_level']) + str(comment_item['comment_time'])
                h1.update(token_raw.encode(encoding='utf-8'))
                comment_item['token'] = h1.hexdigest()
                yield comment_item


