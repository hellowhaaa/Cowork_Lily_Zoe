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
config_file_path = os.path.join(current_directory, '.config.ini')
# 建立 ConfigParser 對象
config = ConfigParser()
# 讀取 config.ini 文件
config.read(config_file_path)


database = config['DATA_BASE']

db = pymysql.connect(host = database['host'],
                    user = database['user'],
                    password = database['password'],
                    database = database['database'],
                    cursorclass=pymysql.cursors.DictCursor,
                    charset="utf8mb4")

my_cursor = db.cursor()
print(my_cursor)
user1_id = 10274
user2_id = 10275



numbers = [1, 2, 3, 4, 5]
weights = [0.05, 0.1, 0.25, 0.35, 0.25]


with open('/Users/lily_chou/Desktop/co_work/json_csv_folder/lative_id_list.json', 'r', encoding='utf-8') as file:
    lative_id_list = json.load(file)

for lative_id in lative_id_list:
    query_select_product_from_lative = "select id from product where lative_id = %s"
    my_cursor.execute(query_select_product_from_lative, (lative_id))
    product_id = my_cursor.fetchone()
    if product_id:
        product_id = product_id['id']
        star = random.choices(numbers, weights, k=1)[0]
        query_insert_comment = " INSERT INTO comment (user_id, star, product_id) VALUES (%s, %s, %s)"
        my_cursor.execute(query_insert_comment, (user2_id, star, product_id))
        db.commit()