# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import jd_spu.settings as settings
import pymysql
import sys
import time

class JdSpuPipeline(object):
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
        self.get_spu_item = 0
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        try:
            value = item['spu_name']
            sku_id = item['sku_id']
            self.cursor.execute(
                "select sku_id, value from bas_spu where value='{0}' and sku_id='{1}'".format(value, sku_id)
            )
            data = self.cursor.fetchall()
            if len(data) == 0:
                self.cursor.execute(
                    """INSERT INTO bas_spu (goods_name, end_cat, cat_name, sku_id, spu_name, 
                    status, creater, create_time, editor, edit_time, value, pre_sku_id, source_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) """,
                    (
                        item['goods_name'], item['end_cat'], item['cat_name'], item['sku_id'], item['spu_name'], 1,
                        'neo', time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                        'neo', time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), item['value'], item['pre_sku_id'], 1
                    )
                )
                self.conn.commit()
                print('---------------Successful Spu insertion---------------')
                self.get_spu_item = self.get_spu_item + 1
                print("Spu counts " + str(self.get_spu_item) + " times")
            else:
                print(str(item['sku_id']) + " 属性 " + item['spu_name'] + ' ' + item['value'] + " 已存在")

        except Exception as e:
            print('***************************************')
            s = sys.exc_info()
            print(item)
            print("Error '%s' happened on line %d" % (s[1], s[2].tb_lineno))
        return item
