# -*- coding: utf-8 -*-
import scrapy
from jd_brand.items import JdBrandItem
import time
import re
from jd_brand.settings import CAT

class BrandSpider(scrapy.Spider):
    name = 'brand'
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
                yield scrapy.Request(url, callback=self.get_items_url)
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
                yield scrapy.Request(url, callback=self.brand, meta={'sku_id': sku_id}, dont_filter=True)

    def brand(self, response):
        status = response.status
        if status == 302 or status == 301:
            print('-*-*-*- 重定向至其他页面,重新请求 -*-*-*-')
            print('----- 重定向网址为：-----', response.url)
            print(response.text[:1000])
            time.sleep(5)
            yield scrapy.Request(response.url,callback=self.brand,meta={'sku_id': response.meta['sku_id']},dont_filter=True)
        else:
            yield from self.brand_content(response)

    def brand_content(self,response):
        print('-------------------Brand crawling-------------------')
        print('brand 开启时间', time.strftime("%H:%M:%S", time.localtime()))
        starttime = time.time()
        sku_id = re.findall('\/(\d+)\.html',response.url)[0]
        brand = JdBrandItem()
        brand['sku_id'] = int(sku_id)
        brand['name'], brand['e_name'] = self.get_brand_name(response)
        endtime = time.time()
        span = endtime - starttime
        print('brand 爬取时长为', span)
        yield brand

    # 获取品牌的中文名与英文名
    def get_brand_name(self, response):
        name_raw = ''.join(re.findall("<li title='(.*?)'>品牌：", response.text))
        if '（' in name_raw:
            e_name = re.findall('（(.*?)）', name_raw)[0]
            chinese = re.sub('（.*?）', '', name_raw)
        elif re.search('[\u4e00-\u9fa5]+', name_raw):
            chinese = name_raw
            e_name = ''
        else:
            e_name = name_raw
            chinese = ''
        return chinese, e_name

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