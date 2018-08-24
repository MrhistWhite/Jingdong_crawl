# -*- coding: utf-8 -*-
import scrapy
import time
from jd_spu.items import JdSpuItem
import re
from jd_spu.settings import CAT

class SpuSpider(scrapy.Spider):
    name = 'spu'
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
            sku_id = re.findall('\/(\d+).html',url)[0]
            yield scrapy.Request(url, callback=self.get_div_sku,meta={'sku_id':sku_id})

    def get_div_sku(self,response):
        pre = response.meta['sku_id']
        status = response.status
        if status == 302:
            print('-*-*-*- 重定向至其他页面,重新请求 -*-*-*-')
            print('----- 重定向网址为：-----', response.url)
            print(response.text[:1000])
            time.sleep(5)
            yield scrapy.Request(response.url, callback=self.get_div_sku,meta={'sku_id':pre},dont_filter=True)
        else:
            sku_id_list = self.get_sku_url(response, status)
            for url in sku_id_list:
                sku_id = re.findall('\/(\d+)\.html', url)[0]
                pre_sku_id = 0 if sku_id == pre else pre
                yield scrapy.Request(url, callback=self.spu, meta={'sku_id': sku_id, 'pre_sku_id':pre_sku_id}, dont_filter=True)

    def spu(self, response):
        status = response.status
        if status == 302 or status == 301:
            print('-*-*-*- 重定向至其他页面,重新请求 -*-*-*-')
            print('----- 重定向网址为：-----', response.url)
            print(response.text[:1000])
            time.sleep(5)
            sku_id = response.meta['sku_id']
            pre_sku_id = response.meta['pre_sku_id']
            yield scrapy.Request(response.url, callback=self.spu, meta={'sku_id': sku_id,'pre_sku_id':pre_sku_id},dont_filter=True)
        else:
            yield from self.spu_content(response)

    def spu_content(self,response):
        print('-------------------Spu crawling-------------------')
        print('Spu 开启时间', time.strftime("%H:%M:%S", time.localtime()))
        starttime = time.time()
        spu = JdSpuItem()
        property_dict = self.get_spu(response)
        if 'domain=jd.hk' in response.text:
            cat_raw = re.findall('cat: \[(.*?)\]', response.text, re.S)[0]
            cat_name = re.findall('catName: \["(.*?)","(.*?)","(.*?)"\]', response.text, re.S)[0][-1]
        else:
            cat_raw = re.findall('cat=(\d+,\d+,\d+)', response.text)[0]
            cat_name = response.xpath('//div[@class="crumb fl clearfix"]/div/a/text()').extract()[-1]
        sku_id = response.meta['sku_id']
        e_name, name_raw = self.get_item_name(response)
        cat = cat_raw.split(',')[-1]
        pre_sku_id = response.meta['pre_sku_id']
        for i in property_dict.keys():
            spu['spu_name'] = i
            spu['value'] = property_dict[i]
            spu['goods_name'] = name_raw
            spu['end_cat'] = cat
            spu['cat_name'] = cat_name
            spu['sku_id'] = int(sku_id)
            spu['pre_sku_id'] = int(pre_sku_id)
            endtime = time.time()
            span = endtime - starttime
            print('spu 爬取时长为', span)
            yield spu

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

    #spu
    def get_spu(self,response):
        property_list = response.xpath('//div[@class="p-parameter"]/ul//li/text()').extract()
        property_list = [i for i in property_list if i.strip() != '']
        property_dict = dict()
        for item in property_list:
            if item[-1] == ' ':
                patt = item + '<.*?>(.*?)<'
                property_dict[item.split('：')[0]] = re.findall(patt, response.text, re.S)[0]
            else:
                property_dict[item.split('：')[0]] = item.split('：')[1]
        return property_dict

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
