# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql
import time
import jd_category.settings as settings
import sys

class JdCategoryPipeline(object):
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
        self.get_category_item = 0
        self.cursor = self.conn.cursor()
    def process_item(self, item, spider):
        try:
            sku_id = item['sku_id']
            parent_level = item['parent_level']
            self.cursor.execute(
                "select sku_id, parent_level from bas_category where sku_id='{0}' and parent_level={1}".format(sku_id,
                                                                                                               parent_level)
            )
            data = self.cursor.fetchall()
            if len(data) == 0:
                self.cursor.execute(
                    """INSERT INTO bas_category (sku_id, name, status, creater, create_time, editor, 
                    edit_time, parent_level, level_total, source_id, cat, last_cat) 
                    VALUES (%s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s) """,
                    (
                        item['sku_id'], item['name'], 1, 'neo',
                        time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), 'neo',
                        time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), parent_level, 3, 1, item['cat'],
                        item['last_cat']
                    )
                )
                self.conn.commit()
                print('---------------Successful Category insertion---------------')
                self.get_category_item = self.get_category_item + 1
                print("Category counts " + str(self.get_category_item) + " times")
            else:
                print(str(item['sku_id']) + "数据已存在")

        except Exception as e:
            print('***************************************')
            s = sys.exc_info()
            print(item)
            print("Error '%s' happened on line %d" % (s[1], s[2].tb_lineno))
        return item
