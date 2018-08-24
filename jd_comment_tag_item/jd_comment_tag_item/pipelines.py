# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql
import sys
import time
import jd_comment_tag_item.settings as settings

class JdCommentTagItemPipeline(object):

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
        self.get_comment_item_item = 0
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        try:
            token = item['token']
            self.cursor.execute(
                "select token from bas_comment_tag_item where token='{0}'".format(token)
            )
            data = self.cursor.fetchall()
            if len(data) == 0:
                self.cursor.execute(
                    """INSERT INTO bas_comment_tag_item (sku_id, comment_context, comment_time, comment_score, status,
                     creater, create_time, editor, edit_time,goods_id,token,referenceName,afterdays,ismobile,
                     mobileVersion,userClientShow,userLevelName,days,recommend,plusAvailable,anonymousFlag,guid,referenceTime,
                     referenceType,referenceTypeId,title,usefulVoteCount,uselessVoteCount,replyCount,replyCount2,userLevelId,
                     userProvince,viewCount,orderId,isReplyGrade,nickname,userClient,userImgFlag,source_id,add_content,tag_name) VALUES 
                     (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                      %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) """,
                    (
                        item['sku_id'], item['comment_context'],
                        item['comment_time'], item['comment_score'], 1, 'neo',
                        time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), 'neo',
                        time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), 0, token,
                        item['referenceName'],
                        item['afterdays'], item['ismobile'], item['mobileVersion'], item['userClientShow'],
                        item['userLevelName'],
                        item['days'], item['recommend'], item['plusAvailable'], item['anonymousFlag'], item['guid'],
                        item['referenceTime'],
                        item['referenceType'], item['referenceTypeId'], item['title'], item['usefulVoteCount'],
                        item['uselessVoteCount'],
                        item['replyCount'], item['replyCount2'], item['userLevelId'], item['userProvince'],
                        item['viewCount'], item['orderId'],
                        item['isReplyGrade'], item['nickname'], item['userClient'], item['userImgFlag'], 1,
                        item['add_content'], item['tag_name']
                    )
                )
                self.conn.commit()
                print('---------------Successful Comment_tag_item insertion---------------')
                self.get_comment_item_item = self.get_comment_item_item + 1
                print("Comment_item counts " + str(self.get_comment_item_item) + " times")
            else:
                print(str(item['sku_id']) + '评论')
                print(item['comment_context'])
                print(str(token) + '已存在')
                print(item['comment_time'])

        except Exception as e:
            print('***************************************')
            s = sys.exc_info()
            print(item)
            print("Error '%s' happened on line %d" % (s[1], s[2].tb_lineno))
        return item
