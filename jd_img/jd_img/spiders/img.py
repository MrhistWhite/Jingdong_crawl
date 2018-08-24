# -*- coding: utf-8 -*-
import scrapy
from scrapy_redis.spiders import RedisSpider
import re
import time
from jd_img.items import JdImgItem
from jd_img.settings import CAT

class ImgSpider(RedisSpider):
    name = 'img'
    allowed_domains = ['jd.com','jd.hk']

    def start_requests(self):
        for i in range(len(CAT)):
            url = CAT[i]
            yield scrapy.Request(url,callback=self.parse)

    def parse(self, response):
        try:
            if 'class="p-num"' in response.text:
                page = int(response.xpath('//span[@class="p-num"]/a/text()').extract()[-2])
            else:
                print(response.url)
                page = 100
            for i in range(1, page + 1):
                url = response.url + '&page=' + str(i) + '&sort=sort_totalsales15_desc'
                yield scrapy.Request(url, callback=self.get_items_url, meta={'page': i})
        except Exception as e:
            print('---------------------')
            print(e)
            print('---------------------')

    def get_items_url(self, response):
        item_list = response.xpath('//div[@class="p-img"]/a/@href').extract()
        for i in item_list:
            url = 'https:' + i
            yield scrapy.Request(url, callback=self.get_div_sku)

    def get_div_sku(self,response):
        status = response.status
        if status == 302:
            print('-*-*-*- 重定向至其他页面,重新请求 -*-*-*-')
            print('----- 重定向网址为：-----', response.url)
            print(response.text[:1000])
            time.sleep(5)
            yield scrapy.Request(response.url, callback=self.get_div_sku, dont_filter=True)
        else:
            sku_id_list = self.get_sku_url(response, status)
            for url in sku_id_list:
                sku_id = re.findall('\/(\d+)\.html', url)[0]
                yield scrapy.Request(url, callback=self.img, meta={'sku_id': sku_id}, dont_filter=True)

    def img(self, response):
        status = response.status
        if status == 302 or status == 301:
            print('-*-*-*- 重定向至其他页面,重新请求 -*-*-*-')
            print('----- 重定向网址为：-----', response.url)
            print(response.text[:1000])
            time.sleep(5)
            yield scrapy.Request(response.url, callback=self.img, meta={'sku_id': response.meta['sku_id']},dont_filter=True)
        else:
            yield from self.img_content(response)

    def img_content(self,response):
        print('-------------------Img crawling-------------------')
        img_list = response.xpath('//div[@class="spec-items"]/ul//li/img/@src').extract()
        sku_id = int(re.findall('\/(\d+)\.html',response.url)[0])
        if img_list == []:
            time.sleep(5)
            yield scrapy.Request(response.url,callback=self.img,dont_filter=True)
        else:
            for i in range(len(img_list)):
                if '.png' in img_list[i]:
                    continue
                else:
                    img = JdImgItem()
                    img_url = re.sub('\/s.*?jfs\/', '/jfs/', img_list[i])
                    img_url = re.sub('img\d+', 'img14', img_url)
                    img['img_url'] = 'https:' + re.sub('\/n\d+\/', '/n0/', img_url)
                    img['sku_id'] = sku_id
                    yield img

    # sku
    def get_sku_url(self, response, status):
        try:
            choose = re.findall('colorSize: \[(.*?)\]', response.text)[0]
            sku_list = re.findall('"skuId":(\d+)', choose)
        except:
            sku_list = []
        if sku_list == []:
            print('当前页面无子属性')
            url_list = [response.url]
        elif status == 301:
            url_list = ['https://item.jd.hk/' + i + '.html' for i in sku_list]
        else:
            url_list = ['https://item.jd.com/' + i + '.html' for i in sku_list]
        return url_list