# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql
import jd_goods.settings as settings
import sys
import time

class JdGoodsPipeline(object):

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
        self.get_goods_item = 0
        self.get_subtitle_item = 0
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        try:
            sku_id = item['sku_id']
            self.cursor.execute(
                "select sku_id from bas_goods where sku_id='{0}'".format(sku_id)
            )
            data = self.cursor.fetchall()
            if len(data) == 0:
                self.cursor.execute(
                    """INSERT INTO bas_goods ( base_price, sku_id, e_name, spec, origin, packing, keep_days, unit, status,
                     creater, create_time, editor, edit_time, name, end_cat, cat_name, source_id, pre_sku_id, pos, sub_title, title)
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) """,
                    (
                        item['base_price'], item['sku_id'], item['e_name'],
                        str(item['spec']), item['origin'], item['packing'], item['keep_days'], item['unit'],
                        1, 'neo', time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), 'neo',
                        time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), item['name'],
                        item['end_cat'], item['cat_name'], 1, item['pre_sku_id'], item['pos'], item['sub_title'],item['title']
                    )
                )
                self.conn.commit()
                print('---------------Successful Goods insertion---------------')
                self.get_goods_item = self.get_goods_item + 1
                print("Goods counts " + str(self.get_goods_item) + " times")
            else:
                self.cursor.execute(
                    "select sku_id from bas_goods where sku_id='{0}' and title = '{1}'".format(sku_id,item['title'])
                )
                data = self.cursor.fetchall()
                if len(data) == 0:
                    self.cursor.execute(
                        "update bas_goods set sub_title = '{0}', title = '{1}' where sku_id = '{2}'".format(
                            item['sub_title'], item['title'],sku_id
                        )
                    )
                    self.conn.commit()
                    print('---------------Successful subtitle update---------------')
                    self.get_subtitle_item = self.get_subtitle_item + 1
                    print("Subtitle update " + str(self.get_subtitle_item) + " times")
                else:
                    print(str(item['sku_id']) + "数据已存在")

        except Exception as e:
            print('***************************************')
            s = sys.exc_info()
            print(item)
            print("Error '%s' happened on line %d" % (s[1], s[2].tb_lineno))
        return item