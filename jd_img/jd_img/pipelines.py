# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql
import sys
import hashlib
import time
import jd_img.settings as settings

class JdImgPipeline(object):

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
        self.get_img_item = 0
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        try:
            img_url = item['img_url']
            sku_id = item['sku_id']
            self.cursor.execute(
                "select img_url,sku_id from bas_img where img_url='{0}' and sku_id = {1}".format(img_url,sku_id)
            )
            data = self.cursor.fetchall()
            if len(data) == 0:
                h1 = hashlib.md5()
                h1.update(item['img_url'].encode(encoding='utf-8'))
                token = h1.hexdigest()
                self.cursor.execute(
                    """INSERT INTO bas_img (sku_id, img_url, token, status, source_id,
                     creater, create_time, editor, edit_time,goods_id) VALUES (%s,%s, %s, %s, %s, %s, %s,%s,%s,%s) """,
                    (
                        item['sku_id'], item['img_url'], token,
                        1, 1, 'neo', time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                        'neo', time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), 0
                    )
                )
                self.conn.commit()
                print('---------------Successful Img insertion---------------')
                self.get_img_item = self.get_img_item + 1
                print("Img counts " + str(self.get_img_item) + " times")
            else:
                print(str(item['sku_id']) + "数据已存在")
                print("地址为：" + str(item['img_url']))

        except Exception as e:
            print('***************************************')
            s = sys.exc_info()
            print(item)
            print("Error '%s' happened on line %d" % (s[1], s[2].tb_lineno))
        return item
