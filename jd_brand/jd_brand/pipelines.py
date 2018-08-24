# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql
import time
import sys
import jd_brand.settings as settings

class JdBrandPipeline(object):

    def __init__(self):
        self.conn = pymysql.connect(
            host=settings.MYSQL_HOST,
            port=settings.MYSQL_PORT,
            db=settings.MYSQL_DBNAME,
            user=settings.MYSQL_USER,
            passwd=settings.MYSQL_PASSWD,
            charset='utf8',
            use_unicode=True
        )
        self.get_brand_item = 0
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        try:
            sku_id = item['sku_id']
            self.cursor.execute(
                "select sku_id from bas_brand where sku_id='{0}'".format(sku_id)
            )
            data = self.cursor.fetchall()
            if len(data) == 0:
                self.cursor.execute(
                    """INSERT INTO bas_brand (sku_id, name, e_name, status, creater, create_time, editer, edit_time,
                    source_id) VALUES (%s, %s, %s, %s, %s,%s,%s,%s,%s) """,
                    (
                        item['sku_id'], item['name'], item['e_name'], 1, 'neo',
                        time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                        'neo', time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),1
                    )
                )
                self.conn.commit()
                print('---------------Successful Brand insertion---------------')
                self.get_brand_item = self.get_brand_item + 1
                print("Brand counts " + str(self.get_brand_item) + " times")
            else:
                print(str(item['sku_id']) + "数据已存在")

        except Exception as e:
            print('***************************************')
            s = sys.exc_info()
            print(item)
            print("Error '%s' happened on line %d" % (s[1], s[2].tb_lineno))
        return item
