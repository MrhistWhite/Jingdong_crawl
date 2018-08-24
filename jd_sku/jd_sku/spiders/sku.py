# -*- coding: utf-8 -*-
import scrapy
import re
import pandas as pd
import time
from jd_sku.items import JdSkuItem
import json
from jd_sku.settings import CAT

class SkuSpider(scrapy.Spider):
    name = 'sku'
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
            sku_id = re.findall('\/(\d+)\.html',url)[0]
            yield scrapy.Request(url, callback=self.sku, meta={'sku_id':sku_id})

    def sku(self, response):
        status = response.status
        pre = response.meta['sku_id']
        if status == 301:
            url = re.sub('.com','.hk',response.url)
            yield scrapy.Request(url,callback=self.sku, meta={'sku_id': pre})
        elif status == 302:
            print('-*-*-*- 重定向至其他页面,重新请求 -*-*-*-')
            print('----- 重定向网址为：-----', response.url)
            print(response.text[:1000])
            time.sleep(5)
            yield scrapy.Request(response.url, callback=self.sku, meta={'sku_id': pre},
                                 dont_filter=True)
        else:
            yield from self.sku_content(response)

    def sku_content(self, response):
        print('-------------------Sku crawling-------------------')
        print('Sku 开启时间', time.strftime("%H:%M:%S", time.localtime()))
        starttime = time.time()
        sku = JdSkuItem()
        df = self.get_sku(response)
        if type(df) == int:
            return
        else:
            pre = response.meta['sku_id']
            if 'domain=jd.hk' in response.text:
                cat_raw = re.findall('cat: \[(.*?)\]', response.text, re.S)[0]
                cat_name = re.findall('catName: \["(.*?)","(.*?)","(.*?)"\]', response.text, re.S)[0][-1]
            else:
                cat_raw = re.findall('cat=(\d+,\d+,\d+)', response.text)[0]
                cat_name = response.xpath('//div[@class="crumb fl clearfix"]/div/a/text()').extract()[-1]
            cat = cat_raw.split(',')[-1]
            e_name, name_raw = self.get_item_name(response)
            for index in df.index:
                for col in df.columns:
                    pre_sku_id = 0 if index == pre else pre
                    sku['value'] = df.ix[index, col]
                    sku['sku_name'] = re.sub('选择', '', col)
                    sku['sku_id'] = index
                    sku['goods_name'] = name_raw
                    sku['end_cat'] = cat
                    sku['cat_name'] = cat_name
                    sku['pre_sku_id'] = pre_sku_id
                    endtime = time.time()
                    span = endtime - starttime
                    print('sku 爬取时长为', span)
                    yield sku

    # sku
    def get_sku(self, response):
        try:
            choose = re.findall('colorSize: \[(.*?)\]', response.text)[0]
            property_list = re.findall('{".*?":.*?}', choose)
            property_dict = dict()
            for i in range(len(property_list)):
                property_dict[i] = json.loads(property_list[i])
            df = pd.DataFrame(property_dict).T.set_index('skuId')
        except:
            print(response.url)
            df = 0
        return df

    # 获取商品的全名与英文名
    def get_item_name(self, response):
        name = ''.join(re.findall('商品名称：(.*?)<', response.text))
        if name != '':
            if '/' in name:
                e_name = name.split('/')[0]
            elif re.search('[\u4e00-\u9fa5]+', name):
                e_name = ''
            else:
                e_name = name
        else:
            e_name = ''
            name = response.xpath('//div[@class="sku-name"]/text()').extract_first().strip()
        return e_name, name