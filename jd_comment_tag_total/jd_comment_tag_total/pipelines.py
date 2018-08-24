# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import sys
import pymysql
import jd_comment_tag_total.settings as settings
import time

class JdCommentTagTotalPipeline(object):

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
        self.get_comment_tag_total = 0
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        try:
            sku_id = item['sku_id']
            tag_name = item['tag_name']
            self.cursor.execute(
                "select sku_id from bas_comment_tag_total where sku_id='{0}' and tag_name='{1}'".format(sku_id, tag_name)
            )
            data = self.cursor.fetchall()
            if len(data) == 0:
                self.cursor.execute(
                    """INSERT INTO bas_comment_tag_total (sku_id, goods_id, tag_name, tag_count, tag_num, status, creater, create_time, 
                    editor, edit_time, source_id) VALUES (%s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s) """,
                    (
                        item['sku_id'], 0, item['tag_name'], item['tag_count'], item['tag_num'], 1, 'neo',
                        time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                        'neo', time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), 1
                    )
                )
                self.conn.commit()
                print('---------------Successful Comment_tag_total insertion---------------')
                self.get_comment_tag_total = self.get_comment_tag_total + 1
                print("Comment_tag_total counts " + str(self.get_comment_tag_total) + " times")
            else:
                print(str(sku_id) + ' ' + tag_name + "数据已存在")

        except Exception as e:
            print('***************************************')
            s = sys.exc_info()
            print(item)
            print("Error '%s' happened on line %d" % (s[1], s[2].tb_lineno))
        return item

