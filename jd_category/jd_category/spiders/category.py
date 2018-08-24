# -*- coding: utf-8 -*-
import scrapy
import time
from jd_category.items import JdCategoryItem
import re
from jd_category.settings import CAT

class CategorySpider(scrapy.Spider):
    name = 'category'
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
            sku_id = re.findall('\/(\d+).html',i)[0]
            yield scrapy.Request(url, callback=self.category,meta={'sku_id':sku_id})

    def category(self, response):
        status = response.status
        sku_id = response.meta['sku_id']
        if status == 301:
            url = re.sub('.com', '.hk', response.url)
            yield scrapy.Request(url, callback=self.category,meta={'sku_id':sku_id})
        elif status == 302:
            print('-*-*-*- 重定向至其他页面,重新请求 -*-*-*-')
            print('----- 重定向网址为：-----', response.url)
            print(response.text[:1000])
            time.sleep(5)
            yield scrapy.Request(response.url, callback=self.category, meta={'sku_id':sku_id},dont_filter=True)
        else:
            yield from self.cat_content(response)

    def cat_content(self,response):
        print('-------------------Category crawling-------------------')
        print('category 开启时间', time.strftime("%H:%M:%S", time.localtime()))
        starttime = time.time()
        category = JdCategoryItem()
        sku_id=response.meta['sku_id']
        cat_dict = self.get_cat(response)
        for j,i in enumerate(cat_dict.keys()):
            category['name'] = cat_dict[i]
            category['sku_id'] = int(sku_id)
            category['parent_level'] = j + 1
            category['last_cat'] = 0 if j == 0 else list(cat_dict.keys())[j-1]
            category['cat'] = i
            endtime = time.time()
            span = endtime - starttime
            print('category 爬取时长为', span)
            yield category

    #cat
    def get_cat(self,response):
        try:
            cat_raw = re.findall('cat=(\d+,\d+,\d+)', response.text)[0]
            cat_name = response.xpath('//div[@class="crumb fl clearfix"]/div/a/text()').extract()
        except:
            cat_raw = re.findall('cat: \[(.*?)\]', response.text)[0]
            cat_name = list(re.findall('catName: \["(.*?)","(.*?)","(.*?)"\]', response.text)[0])
        cat_list = cat_raw.split(',')
        cat_dict = dict(zip(cat_list,cat_name))
        return cat_dict
