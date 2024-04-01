import os
from configparser import ConfigParser
import pymysql.cursors
import json
import random
import pymysql
import requests
from bs4 import BeautifulSoup
import threading
from time import sleep
import csv
import ast
# config file ----------------------------
current_directory = os.path.dirname(os.path.abspath(__file__))
#  config.ini 的絕對路徑
config_file_path = os.path.join(current_directory, 'config.ini')
# 建立 ConfigParser 對象
config = ConfigParser()
# 讀取 config.ini 文件
config.read(config_file_path)


database = config['local_DATA_BASE']

db = pymysql.connect(host=database['host'],
                     user=database['user'],
                     password=database['password'],
                     database=database['database'],
                     cursorclass=pymysql.cursors.DictCursor,
                     charset="utf8mb4")

my_cursor = db.cursor()
# print(my_cursor)


with open('/Users/a123/Documents/GitHub/Stylish-Data-Engineering/combine_final2.json', 'r', encoding='utf-8') as file:
    data = json.load(file)
    # data = [{"item_id":65241011}]
    for product in data:
        lative_item_id = product["item_id"]
        query_select_product_from_lative = "select id, title, category from product where lative_id = %s"
        my_cursor.execute(query_select_product_from_lative, (lative_item_id))
        data = my_cursor.fetchone()
        product_id = data['id']
        title = data['title']
        if "（ " in title or "(" in title:
            index = title.rfind("(") - 3  # 找到 "(" 往前三個的位置
            target = title[max(0, index):title.rfind("(")]  # 取得目標字串
        else:
            title_parsed = title[-3:]
        query_select_recommend = "SELECT id, title FROM product WHERE title LIKE %s AND id NOT IN (%s)"
        my_cursor.execute(query_select_recommend,
                          ('%' + title_parsed, product_id,))
        all_recommend_list = my_cursor.fetchmany(4)
        print(all_recommend_list)

        num_all_recommend_list = len(all_recommend_list)
        if num_all_recommend_list < 4:
            category = data['category']
            cur_id_list = [ele['id'] for ele in all_recommend_list]
            cur_id_list.append(product_id)
            print(cur_id_list)
            sql = "SELECT id, title FROM product where category=%s and id not in %s ORDER BY RAND( ) LIMIT %s;"
            my_cursor.execute(
                sql, (category, cur_id_list, 4-num_all_recommend_list))
            addtional_recommend_list = my_cursor.fetchall()
            print(all_recommend_list)
            print(addtional_recommend_list)
            print(type(all_recommend_list))
            print(type(addtional_recommend_list))
            all_recommend_list = list(
                all_recommend_list)+list(addtional_recommend_list)
            print()
            # all_recommend_list += addtional_recommend_list

        for recommend_product in all_recommend_list:
            recommend_product_id = recommend_product['id']
            query_insert_recommend_product = " INSERT INTO recommend_product (product_id, re_product_id) VALUES (%s, %s)"
            my_cursor.execute(query_insert_recommend_product,
                              (product_id, recommend_product_id))
            db.commit()
