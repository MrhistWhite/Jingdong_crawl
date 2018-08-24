# -*- coding: utf-8 -*-
import scrapy
from jd_goods.items import JdGoodsItem
import time
import re
import requests
import json
import random
from jd_goods.settings import CAT
from jd_goods.middlewares import UserAgentMiddleware,MyproxiesSpiderMiddleware

class GoodsSpider(scrapy.Spider):
    name = 'goods'
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
                print('无法获取页码', response.url)
                page = 100
            for i in range(1, page + 1):
                url = response.url + '&page=' + str(i) + '&sort=sort_totalsales15_desc'
                yield scrapy.Request(url, callback=self.get_items_url,meta={'page':i})
        except Exception as e:
            print('---------------------')
            print(e)
            print('---------------------')

    def get_items_url(self, response):
        item_list = response.xpath('//div[@class="p-img"]/a/@href').extract()
        page = response.meta['page']
        for i,j in enumerate(item_list):
            url = 'https:' + j
            pos = (page - 1) * 60 + i + 1
            sku_id = re.findall('\/(\d+).html', url)[0]
            yield scrapy.Request(url, callback=self.get_div_sku, meta={'sku_id': sku_id,'pos':pos})

    def get_div_sku(self, response):
        pre = response.meta['sku_id']
        pos = response.meta['pos']
        status = response.status
        if status == 302:
            print('-*-*-*- 重定向至其他页面,重新请求 -*-*-*-')
            print('----- 重定向网址为：-----', response.url)
            print(response.text[:1000])
            time.sleep(5)
            yield scrapy.Request(response.url, callback=self.get_div_sku, meta={'sku_id':pre,'pos':pos}, dont_filter=True)
        else:
            sku_id_list = self.get_sku_url(response, status)
            for url in sku_id_list:
                sku_id = re.findall('\/(\d+)\.html', url)[0]
                yield scrapy.Request(url, callback=self.goods, meta={'pre_sku_id': pre, 'sku_id':sku_id, 'pos':pos}, dont_filter=True)

    def goods(self, response):
        status = response.status
        pre_sku_id = response.meta['pre_sku_id']
        sku_id = response.meta['sku_id']
        pos = response.meta['pos']
        if status == 302 or status == 301:
            print('-*-*-*- 重定向至其他页面,重新请求 -*-*-*-')
            print('----- 重定向网址为：-----', response.url)
            print(response.text[:1000])
            time.sleep(5)
            yield scrapy.Request(response.url, callback=self.goods, meta={'sku_id':sku_id,'pre_sku_id':pre_sku_id,'pos':pos}, dont_filter=True)
        else:
            yield from self.goods_content(response)

    def goods_content(self,response):
        print('-------------------Goods crawling-------------------')
        print('goods 开启时间', time.strftime("%H:%M:%S", time.localtime()))
        starttime = time.time()
        goods = JdGoodsItem()

        sub = ''.join(response.xpath('//div[@class="package-list"]/p/text()').extract())
        if sub == '':
            sub = ''.join(response.xpath('//div[@class="package-list"]/p/span/text()').extract())
            if sub == '':
                sub = ''.join(re.findall('包装：(.*?)</li>', response.text))
        sku_id = response.meta['sku_id']
        e_name, name = self.get_item_name(response)
        keep_days = ''.join(re.findall('<dt>保质期</dt><dd>(\d+)天</dd>', response.text))
        if keep_days == '':
            keep_days = None
        else:
            keep_days = int(keep_days)
        if 'domain=jd.hk' in response.text:
            cat_raw = re.findall('cat: \[(.*?)\]', response.text)[0]
            cat_name = list(re.findall('catName: \["(.*?)","(.*?)","(.*?)"\]', response.text)[0])[-1]
        else:
            cat_raw = re.findall('cat=(\d+,\d+,\d+)', response.text)[0]
            cat_name = response.xpath('//div[@class="crumb fl clearfix"]/div/a/text()').extract()[-1]
        cat = cat_raw.split(',')[-1]
        pre_sku_id = response.meta['pre_sku_id']
        pos = response.meta['pos']
        sub_title = self.get_sub_title(sku_id,cat_raw)
        title = self.get_title(response)

        goods['packing'] = sub
        goods['base_price'] = self.get_base_price(sku_id, cat_raw)
        goods['sku_id'] = int(sku_id)
        goods['e_name'] = e_name
        goods['spec'] = self.get_spec(response)
        goods['origin'] = self.get_origin(response)
        goods['keep_days'] = keep_days
        goods['unit'] = ''.join(re.findall('包装单位：(.*?)</li>', response.text))
        goods['name'] = name
        goods['end_cat'] = cat
        goods['cat_name'] = cat_name
        goods['pre_sku_id'] = pre_sku_id
        goods['pos'] = pos
        goods['sub_title'] = sub_title
        goods['title'] = title
        endtime = time.time()
        span = endtime - starttime
        print('goods 爬取时长为', span)
        yield goods

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

    #售价
    def get_base_price(self,sku_id,cat):
        url='https://c0.3.cn/stock?skuId='+sku_id+'&area=1_72_4137_0&cat='+cat+'&extraParam={%22originid%22:%221%22}'
        proxies=self.get_proxies()
        headers=self.get_headers()
        response_price = requests.get(url, proxies=proxies,headers=headers)
        price=''
        while price == '':
            price=json.loads(response_price.text)['stock']['jdPrice']['p']
            time.sleep(5)
        return price

    #产地
    def get_origin(self,response):
        origin=''.join(re.findall('商品产地：(.*)</li>', response.text))
        return origin

    #规格
    def get_spec(self,response):
        spec_dict=dict()
        if 'domain=jd.hk' in response.text:
            first = response.xpath('//th[@colspan="2"]/text()').extract()
            for i in first:
                if i != first[-1]:
                    patt1 = '<tr><th class="tdTitle" colspan="2">'+i+'(.*?)<tr><th class="tdTitle" colspan="2">'
                else:
                    patt1 = '<tr><th class="tdTitle" colspan="2">'+i+'(.*?)</table>'
                first_columns_text=re.findall(patt1,response.text,re.S)[0]
                patt2 = '<tr><td class="tdTitle">(.*?)</tr>'
                first_columns = re.findall(patt2, first_columns_text, re.S)
                patt3 = '(.*?)</td><td>(.*?)</td>'
                second_dict=dict()
                for j in first_columns:
                    dict_tuple = re.findall(patt3, j)[0]
                    second_dict[dict_tuple[0]]=dict_tuple[1]
                spec_dict[i] = second_dict

        elif 'Ptable-item' in response.text:
            first=response.xpath('//div[@class="Ptable-item"]/h3/text()').extract()
            for i in first:
                patt='<h3>'+i+'</h3>(.*?)<h3>'
                first_columns=re.findall(patt,response.text,re.S)
                second_dict=dict()
                for j in first_columns:
                    second=re.findall('<dt>(.*?)</dt>',j)
                    third=re.findall('<dd>(.*?)</dd>',j)
                    for k in range(len(second)):
                        second_dict[second[k]]=third[k]
                spec_dict[i]=second_dict
        else:
            spec_dict = ''
            print('该商品无规格 ',response.url)
        spec_dict=str(spec_dict)
        if spec_dict == '{}':
            spec_dict=''
        return spec_dict

    #标题
    def get_title(self, response):
        title_list = response.xpath('//div[@class="sku-name"]/text()').extract()
        title = title_list[-1].strip()
        return title

    #副标题
    def get_sub_title(self, sku_id, cat):
        url = 'https://cd.jd.com/promotion/v2?&skuId={sku_id}&area=1_72_2819_0&cat={cat}'.format(sku_id=sku_id,cat=cat)
        proxies = self.get_proxies()
        headers = self.get_headers()
        req = requests.get(url, proxies=proxies, headers=headers)
        text = req.text
        if re.search('[\u4e00-\u9fa5]+',text) is None:
            req.encoding='gbk'
            text = req.text
        dic = json.loads(text)
        ads = dic['ads'][0]['ad']
        sub_title = re.sub('<a.*?>', '', ads, re.S)
        sub_title = re.sub('</a>', '', sub_title)
        sub_title = re.sub('\n', '', sub_title)
        return sub_title

    def get_proxies(self):
        IP = MyproxiesSpiderMiddleware()
        ip = IP.get_ip()
        while ip == '':
            ip = IP.get_ip()
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
        USER = UserAgentMiddleware()
        user_agent_list = USER.user_agent_list
        ua = random.choice(user_agent_list)
        headers={
            'User-Agent':ua
        }
        return headers

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