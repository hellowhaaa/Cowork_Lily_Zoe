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


with open('/Users/lily_chou/Desktop/co_work/json_csv_folder/lative_id_list.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

@app.route("/python/recommendation", methods=['GET'])
def recommendation():
    item_id = request.args.get('id')
    print(item_id)

    for lative_id in data:
        
        query_select_product_from_lative = "select id from product where lative_id = %s"
        my_cursor.execute(query_select_product_from_lative, (lative_id))
        product_id = my_cursor.fetchone()

        product_id = product_id['id']
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
        






# @app.route("/python/recommendation", methods=['GET'])
# def recommendation():
#     item_id = request.args.get('id')
#     print(item_id)

#     temp_output = [
#         {
#             "id": 60732011,
#             "title": "雪紡印花荷葉襯衫",
#             "price": 590,
#             "main_image": "https://s.lativ.com.tw/i/60732/60732011/6073201_500.jpg",
#         },
#         {
#             "id": 60700011,
#             "title": "嫘縈長袖襯衫",
#             "price": 590,
#             "main_image": "https://s.lativ.com.tw/i/60700/60700011/6070001_500.jpg",
#         },
#         {
#             "id": 60711021,
#             "title": "亞麻混紡寬版V領襯衫",
#             "price": 590,
#             "main_image": "https://s.lativ.com.tw/i/60711/60711021/6071102_500.jpg",
#         },
#         {
#             "id": 64493011,
#             "category": "WOMEN",
#             "title": "棉麻七分袖襯衫",
#             "price": 590,
#             "main_image": "https://s.lativ.com.tw/i/64493/64493011/6449301_500.jpg",
#         }
#     ]
#     return jsonify({"recommend": temp_output})


# @app.route("/python/AI", methods=['POST'])
# def AI():
#     print(request.json)
#     if not request.json:
#         return jsonify({"Error message": "Wrong json type."}), 403

#     temp_output_list = ['S', 'M', 'L', 'XL']
#     return jsonify({"ai_size": random.choice(temp_output_list)})


# @app.route("/")
# def home():
#     return "<h1> HOME PAGE </h1>"


# if __name__ == "__main__":
#     app.run(debug=True)
