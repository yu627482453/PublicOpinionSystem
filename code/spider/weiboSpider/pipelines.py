# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


import pymysql
import configparser


class WeibospiderPipeline(object):

    def open_spider(self, spider):

        self._get_connect()

        self.SQL_INSERT_ARTICLE = \
            "INSERT INTO article " \
            "(id, scheme, create_time, text, text_length, user0) " \
            "VALUES " \
            "(\"{id}\", \"{scheme}\", \"{create_time}\", \"{text}\", {text_length}, \"{user0}\") ; "

        self.SQL_INSERT_USER = \
            "INSERT INTO user " \
            "(id, name, url, description) " \
            "VALUES " \
            "(\"{id}\", \"{name}\", \"{url}\", \"{description}\") ; "

        self.SQL_INSERT_COMMENT = \
            "INSERT INTO comment " \
            "(id, text, user0) " \
            "VALUES " \
            "(\"{id}\", \"{text}\", \"{user0}\") ; "

    def close_spider(self, spider):
        self.connect.close()

    def process_item(self, item, spider):

        if not item["id"]:
            return

        sql = self.SQL_INSERT_ARTICLE.format(
            id=item["id"], scheme=item["scheme"], create_time=item["create_time"],
            text=item["text"], text_length=item["text_length"], user0=item["user0"][0]["id"]
        )
        self._submit_sql(sql=sql)

        user0 = item["user0"][0]
        sql = self.SQL_INSERT_USER.format(
            id=user0["id"], name=user0["name"], url=user0["url"], description=user0["description"]
        )
        self._submit_sql(sql=sql)

        comments = item["comments"]
        for comment in comments:
            sql = self.SQL_INSERT_COMMENT.format(
                id=comment["id"], text=comment["text"], user0=comment["user"]["id"]
            )
            self._submit_sql(sql=sql)
            user0 = comment["user"]
            sql = self.SQL_INSERT_USER.format(
                id=user0["id"], name=user0["name"], url=user0["url"], description=user0["description"]
            )
            self._submit_sql(sql=sql)

    def _get_config(self, name):
        cf = configparser.ConfigParser()
        cf.read("weiboSpider/config/mysql.ini")
        return cf.get("mysql", name)

    def _get_connect(self):
        host = self._get_config("host")
        port = self._get_config("port")
        user = self._get_config("user")
        passwd = self._get_config("passwd")
        db = self._get_config("db")
        charset = self._get_config("charset")
        self.connect = pymysql.connect(host=host, port=int(port), user=user, passwd=passwd, db=db, charset=charset)
        self.cursor = self.connect.cursor()

    def _submit_sql(self, sql):
        try:
            self.cursor.execute(sql)
            # 提交修改
            self.connect.commit()
        except pymysql.MySQLError as e:
            print(sql)
            print(e)
            # 发生错误时回滚
            self.connect.rollback()
