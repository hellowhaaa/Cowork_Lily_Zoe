from flask import Flask, render_template, request, url_for, redirect, jsonify, make_response
import random
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

import os
from configparser import ConfigParser
import pymysql.cursors
import json
# config file ----------------------------
current_directory = os.path.dirname(os.path.abspath(__file__))

parent_directory = os.path.dirname(current_directory)
#  config.ini 的絕對路徑
config_file_path = os.path.join(parent_directory, '.config.ini')
print(current_directory)
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


@app.route("/python/recommendation", methods=['GET'])
def recommendation():
    product_id = request.args.get('id')
    print(product_id)
    query_select_re_product_id = """
        select r.re_product_id from recommend_product as r
        join product as p
        on r.product_id = p.id
        where r.product_id = %s
        """
    my_cursor.execute(query_select_re_product_id, (product_id))
    data2 = my_cursor.fetchall()
    return_list = []
    re_product_ids_list = [item['re_product_id'] for item in data2] if data2 else []
    if len(re_product_ids_list) != 0:
        for re_id in re_product_ids_list:
            query_select_recommend_details = "select id, title, price, main_image from product where id = %s"
            my_cursor.execute(query_select_recommend_details, (re_id))
            data3 = my_cursor.fetchall()
            for each_recommend_product in data3:
                each_dic = {}
                id = each_recommend_product['id']
                title = each_recommend_product['title']
                price = each_recommend_product['price']
                main_image = each_recommend_product['main_image']
                each_dic['id'] = id
                each_dic['title'] = title
                each_dic['price'] = price
                each_dic['main_image'] = main_image
                return_list.append(each_dic)
    else:
        each_dic = {}
        return_list.append(each_dic)
    return jsonify({"recommend": return_list})
    
        
if __name__ == "__main__":
    app.run(debug=True)