# -*- coding: utf-8 -*-
import scrapy
from jd_barcode.items import JdBarcodeItem
import time
import json
import requests
import re
import random
from jd_barcode.middlewares import MyproxiesSpiderMiddleware, UserAgentMiddleware
from jd_barcode.settings import CAT

class BarcodeSpider(scrapy.Spider):
    name = 'barcode'
    allowed_domains = ['jd.com','jd.hk']

    def start_requests(self):
        for i in range(len(CAT)):
            url = CAT[i]
            yield scrapy.Request(url, callback=self.parse)

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
                yield scrapy.Request(url, callback=self.barcode, meta={'sku_id': sku_id}, dont_filter=True)

    def barcode(self, response):
        if response.status == 301 or response.status == 302:
            print('-*-*-*- 重定向至其他页面,重新请求 -*-*-*-')
            print('----- 重定向网址为：-----', response.url)
            print(response.text[:1000])
            time.sleep(5)
            yield scrapy.Request(response.url,callback=self.barcode, meta={'sku_id':response.meta['sku_id']},dont_filter=True)
        else:
            yield from self.barcode_content(response)

    def barcode_content(self,response):
        print('-------------------Barcode crawling-------------------')
        print('barcode 开启时间', time.strftime("%H:%M:%S", time.localtime()))
        starttime = time.time()
        barcode = JdBarcodeItem()
        sku_id = re.findall('\/(\d+)\.html',response.url)[0]
        if 'domain=jd.hk' in response.text:
            cat_raw = re.findall('cat: \[(.*?)\]', response.text, re.S)[0]
        else:
            cat_raw = re.findall('cat=(\d+,\d+,\d+)', response.text)[0]
        barcode['price'] = self.get_base_price(sku_id, cat_raw)
        barcode['sku_id'] = sku_id
        endtime = time.time()
        span = endtime - starttime
        print('barcode 爬取时长为', span)
        yield barcode

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

    # 售价
    def get_base_price(self, sku_id, cat):
        url = 'https://c0.3.cn/stock?skuId=' + sku_id + '&area=1_72_4137_0&cat=' + cat + '&extraParam={%22originid%22:%221%22}'
        proxies = self.get_proxies()
        headers = self.get_headers()
        response_price = requests.get(url, proxies=proxies, headers=headers)
        price = ''
        while price == '':
            price = json.loads(response_price.text)['stock']['jdPrice']['p']
            time.sleep(5)
        return price

    def get_proxies(self):
        ip = ''
        while ip == '':
            Proxy = MyproxiesSpiderMiddleware()
            ip = Proxy.get_ip()
            if ip != '':
                print("获取到 ip:" + ip)
            else:
                print("未获取到代理，休眠5秒")
                time.sleep(5)
        proxy = "http://" + ip
        proxies = {
            "http": proxy
        }
        return proxies

    def get_headers(self):
        user_agent_list = UserAgentMiddleware.user_agent_list
        ua = random.choice(user_agent_list)
        headers={
            'User-Agent':ua
        }
        return headers
