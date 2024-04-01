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

    temp_output = [
        {
            "id": 60732011,
            "title": "雪紡印花荷葉襯衫",
            "price": 590,
            "main_image": "https://s.lativ.com.tw/i/60732/60732011/6073201_500.jpg",
        },
        {
            "id": 60700011,
            "title": "嫘縈長袖襯衫",
            "price": 590,
            "main_image": "https://s.lativ.com.tw/i/60700/60700011/6070001_500.jpg",
        },
        {
            "id": 60711021,
            "title": "亞麻混紡寬版V領襯衫",
            "price": 590,
            "main_image": "https://s.lativ.com.tw/i/60711/60711021/6071102_500.jpg",
        },
        {
            "id": 64493011,
            "category": "WOMEN",
            "title": "棉麻七分袖襯衫",
            "price": 590,
            "main_image": "https://s.lativ.com.tw/i/64493/64493011/6449301_500.jpg",
        }
    ]
    return jsonify({"recommend": temp_output})


@app.route("/python/AI", methods=['POST'])
def AI():
    print(request.json)
    if not request.json:
        return jsonify({"Error message": "Wrong json type."}), 403

    temp_output_list = ['S', 'M', 'L', 'XL']
    return jsonify({"ai_size": random.choice(temp_output_list)})


@app.route("/")
def home():
    return "<h1> HOME PAGE </h1>"


if __name__ == "__main__":
    app.run(debug=True)
