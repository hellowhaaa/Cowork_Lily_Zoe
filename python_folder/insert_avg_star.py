import os
from configparser import ConfigParser
import pymysql.cursors
import json
import random

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



with open('/Users/lily_chou/Desktop/co_work/json_csv_folder/lative_id_list.json', 'r', encoding='utf-8') as file:
    lative_id_list = json.load(file)

for lative_id in lative_id_list:
    query_select_product_from_lative = "select id from product where lative_id = %s"
    my_cursor.execute(query_select_product_from_lative, (lative_id))
    product_id = my_cursor.fetchone()
    if product_id:
        product_id = product_id['id']
        total = 0
        query_select_stars = " SELECT star from comment where product_id = %s"
        my_cursor.execute(query_select_stars,(product_id))
        stars_list = my_cursor.fetchall()
        for star in stars_list:
            star = star['star']
            total += star
        avg_star = total/len(stars_list)
        # print(avg_star)
        sold = random.randint(10, 500)
        query_insert_avg_star = "UPDATE product SET avg_star = %s , sold = %s WHERE id = %s"
        my_cursor.execute(query_insert_avg_star,(avg_star, sold, product_id))
        db.commit()
    
    