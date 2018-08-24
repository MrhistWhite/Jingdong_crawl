# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql
import jd_comments_total.settings as settings
import time
import sys

class JdCommentsTotalPipeline(object):

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
        self.get_comment_total_item = 0
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        try:
            sku_id = item['sku_id']
            self.cursor.execute(
                "select sku_id from bas_comment_total where sku_id='{0}'".format(sku_id)
            )
            data = self.cursor.fetchall()
            if len(data) == 0:
                self.cursor.execute(
                    """INSERT INTO bas_comment_total (comment_num, good_comment_rate, good_comment, general_count, poor_count, sku_id,
                    default_comment_num, status, creater, create_time, editor, edit_time, goods_id, source_id)
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s) """,
                    (
                        item['comment_num'], item['good_comment_rate'], item['good_comment'], item['general_count'],
                        item['poor_count'], item['sku_id'],
                        item['default_comment_num'], 1, 'neo', time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                        'neo', time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), 0, 1
                    )
                )
                self.conn.commit()
                print('---------------Successful Comment_total insertion---------------')
                self.get_comment_total_item = self.get_comment_total_item + 1
                print("Comment_total counts " + str(self.get_comment_total_item) + " times")
            else:
                print(str(item['sku_id']) + "数据已存在")

        except Exception as e:
            print('***************************************')
            s = sys.exc_info()
            print(item)
            print("Error '%s' happened on line %d" % (s[1], s[2].tb_lineno))
        return item
