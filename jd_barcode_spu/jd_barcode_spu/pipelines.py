# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import jd_barcode_spu.settings as settings
import pymysql
import sys

class JdBarcodeSpuPipeline(object):
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
        self.get_barcode_spu_item = 0
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        try:
            sku_id = item['sku_id']
            self.cursor.execute(
                "select sku_id from bas_barcode_spu where sku_id='{0}'".format(sku_id)
            )
            data = self.cursor.fetchall()
            if len(data) == 0:
                self.cursor.execute(
                    """INSERT INTO bas_barcode_spu (sku_id, name, source_id) VALUES (%s, %s, %s) """,
                    (
                        item['sku_id'], item['name'], 1
                    )
                )
                self.conn.commit()
                print('---------------Successful Barcode_spu insertion---------------')
                self.get_barcode_spu_item = self.get_barcode_spu_item + 1
                print("Barcode_spu counts " + str(self.get_barcode_spu_item) + " times")
            else:
                print(str(item['sku_id']) + "数据已存在")

        except Exception as e:
            s = sys.exc_info()
            print(item)
            print("Error '%s' happened on line %d" % (s[1], s[2].tb_lineno))
        return item
