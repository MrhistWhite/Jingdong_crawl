# -*- coding: utf-8 -*-
import scrapy
import hashlib
from jd_comment_tag_item.items import JdCommentTagItemItem
import json
import datetime
import re
from jd_comment_tag_item.settings import CAT
import time

class CommentTagItemSpider(scrapy.Spider):
    name = 'comment_tag_item'
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
            yield scrapy.Request(response.url,callback=self.get_tags, dont_filter=True)
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
            yield scrapy.Request(response.url,callback=self.get_tags, meta={'sku_id':response.meta['sku_id']},dont_filter=True)
        else:
            item_list = response.xpath('//div[@class="p-img"]/a/@href').extract()
            for i in item_list:
                sku_id = re.findall('\/(\d+).html',i)[0]
                url = 'https:' + i
                yield scrapy.Request(url, callback=self.get_div_sku,meta={'sku_id':sku_id})

    def get_div_sku(self,response):
        if response.status == 302:
            print('-*-*-*- 重定向至其他页面,重新请求 -*-*-*-')
            print('----- 重定向网址为：-----', response.url)
            print(response.text[:1000])
            time.sleep(5)
            yield scrapy.Request(response.url,callback=self.get_tags, meta={'sku_id':response.meta['sku_id']}, dont_filter=True)
        else:
            sku_id_list = self.get_sku(response)
            if sku_id_list == []:
                print('当前页面无子属性')
                sku_id = re.findall('\/(\d+).html',response.url)[0]
                url = """https://sclub.jd.com/comment/productPageComments.action?&productId={sku_id}&score=3&sortType=5&page=0&pageSize=10&isShadowSku=0&fold=1""" \
                    .format(sku_id=sku_id)
                yield scrapy.Request(url,callback=self.get_tags,meta={'sku_id':sku_id},dont_filter=True)
            else:
                for i in sku_id_list:
                    url = """https://sclub.jd.com/comment/productPageComments.action?&productId={sku_id}&score=3&sortType=5&page=0&pageSize=10&isShadowSku=0&fold=1""" \
                        .format(sku_id=i)
                    yield scrapy.Request(url,callback=self.get_tags,meta={'sku_id':i})

    def get_tags(self,response):
        if response.status == 302:
            print('-*-*-*- 重定向至其他页面,重新请求 -*-*-*-')
            print('----- 重定向网址为：-----', response.url)
            print(response.text[:1000])
            time.sleep(5)
            yield scrapy.Request(response.url,callback=self.get_tags, meta={'sku_id':response.meta['sku_id']},dont_filter=True)
        else:
            text = json.loads(response.text)
            tags = text['hotCommentTagStatistics']
            page = text['maxPage']
            sku_id = response.meta['sku_id']
            for i in range(len(tags)):
                for j in range(page):
                    id = tags[i]['id']
                    name = tags[i]['name']
                    url = """https://sclub.jd.com/comment/productPageComments.action?&productId={sku_id}&score=3&sortType=5&page={page}&pageSize=10&isShadowSku=0&rid={id}&fold=1"""\
                    .format(sku_id=sku_id,page=j,id=id)
                    yield scrapy.Request(url,callback=self.comment_tag_item,meta={'sku_id':sku_id,'name':name})

    def comment_tag_item(self, response):
        if response.status == 302:
            print('-*-*-*- 重定向至其他页面,重新请求 -*-*-*-')
            print('----- 重定向网址为：-----', response.url)
            print(response.text[:1000])
            time.sleep(5)
            yield scrapy.Request(response.url,callback=self.get_tags, meta={'sku_id':response.meta['sku_id']},dont_filter=True)
        else:
            print('-------------------Comment_tag_item crawling-------------------')
            sku_id = response.meta['sku_id']
            comment_item = JdCommentTagItemItem()
            comment_dict = json.loads(response.text)
            content_list = comment_dict['comments']
            for i in range(len(content_list)):
                content = content_list[i]
                comment_item['tag_name'] = response.meta['name']
                comment_item['comment_context'] = content['content']  # 评价内容
                comment_item['comment_time'] = datetime.datetime.strptime(content['creationTime'],
                                                                          '%Y-%m-%d %H:%M:%S')  # 评价时间
                score = content['score']
                comment_item['comment_score'] = 5 if score == 0 else score # 评价星级
                comment_item['sku_id'] = sku_id
                comment_item['referenceName'] = content['referenceName']
                comment_item['ismobile'] = int(content['isMobile'])
                comment_item['afterdays'] = content['afterDays']
                comment_item['mobileVersion'] = content['mobileVersion']
                comment_item['userClientShow'] = re.sub('来自', '', content['userClientShow'])
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
                comment_item['title'] = content['title']
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
                            str(comment_item['comment_score']) + str(comment_item['tag_name']) + str(
                    comment_item['comment_time'])
                h1.update(token_raw.encode(encoding='utf-8'))
                comment_item['token'] = h1.hexdigest()
                yield comment_item

    # sku
    def get_sku(self, response):
        try:
            choose = re.findall('colorSize: \[(.*?)\]', response.text)[0]
            sku_list = re.findall('"skuId":(\d+)', choose)
        except:
            sku_list = []
        return sku_list
