# -*- coding: utf-8 -*-
import scrapy
import pandas as pd
from jd_barcode_spu.items import JdBarcodeSpuItem
import time
import re
from jd_barcode_spu.settings import CAT

class BarcodeSpuSpider(scrapy.Spider):
    name = 'barcode_spu'
    allowed_domains = ['jd.com']

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
            sku_id_list = self.get_sku_url(response,status)
            for url in sku_id_list:
                sku_id = re.findall('\/(\d+)\.html',url)[0]
                yield scrapy.Request(url, callback=self.barcode_spu, meta={'sku_id':sku_id}, dont_filter=True)

    def barcode_spu(self, response):
        status = response.status
        if status == 301 or status == 302:
            print('-*-*-*- 重定向至其他页面,重新请求 -*-*-*-')
            print('----- 重定向网址为：-----', response.url)
            print(response.text[:1000])
            time.sleep(5)
            yield scrapy.Request(response.url,callback=self.barcode_spu, meta={'sku_id':response.meta['sku_id']},
                                                                               dont_filter=True)
        else:
            yield from self.barcode_spu_content(response)

    def barcode_spu_content(self,response):
        print('-------------------Barcode_spu crawling-------------------')
        print('barcode_spu 开启时间', time.strftime("%H:%M:%S", time.localtime()))
        starttime = time.time()
        barcode_spu = JdBarcodeSpuItem()
        e_name, name = self.get_item_name(response)
        sku_id=response.meta['sku_id']
        barcode_spu['sku_id'] = int(sku_id)
        barcode_spu['name'] = name
        endtime = time.time()
        span = endtime - starttime
        print('barcode_spu 爬取时长为', span)
        yield barcode_spu

    #获取商品的全名与英文名
    def get_item_name(self,response):
        name = ''.join(re.findall('商品名称：(.*?)<', response.text))
        if name != '':
            if '/' in name:
                e_name=name.split('/')[0]
            elif re.search('[\u4e00-\u9fa5]+', name):
                e_name = ''
            else:
                e_name = name
        else:
            print('-----',name)
            print('-----',response.text)
            e_name=''
            name=response.xpath('//div[@class="sku-name"]/text()').extract_first().strip()
        return e_name, name

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