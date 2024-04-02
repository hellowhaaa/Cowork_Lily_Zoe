from flask import Flask, render_template, request, url_for, redirect, jsonify, make_response, Response
import random
import get_ai_size
from flask_cors import CORS
import os
from configparser import ConfigParser
import pymysql.cursors
import json
import ipdb

app = Flask(__name__)
CORS(app)
current_directory = os.path.dirname(os.path.abspath(__file__))

parent_directory = os.path.dirname(current_directory)
config_file_path = os.path.join(current_directory, 'config.ini')
print(current_directory)
config = ConfigParser()
config.read(config_file_path)


database = config['DATA_BASE']

db = pymysql.connect(host=database['host'],
                     user=database['user'],
                     password=database['password'],
                     database=database['database'],
                     cursorclass=pymysql.cursors.DictCursor,
                     charset="utf8mb4")

my_cursor = db.cursor()
print(my_cursor)


@app.route("/python/recommendation", methods=['GET'])
def recommendation():
    db = pymysql.connect(host=database['host'],
                         user=database['user'],
                         password=database['password'],
                         database=database['database'],
                         cursorclass=pymysql.cursors.DictCursor,
                         charset="utf8mb4")

    my_cursor = db.cursor()
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
    re_product_ids_list = [item['re_product_id']
                           for item in data2] if data2 else []
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


@app.route("/python/AI", methods=['POST'])
def AI():
    # ipdb.set_trace()
    if not request.json:
        return jsonify({"Error message": "Wrong json type."}), 403
    data = request.get_json()
    print(data)
    # data = json.loads(json_data)
    print(type(data))
    # data = json.loads(dj)
    print(data)
    if "weight" not in data:
        return jsonify({"Error message": "Wrong json type. Doesn't contain weight."}), 403
    if "product_id" not in data:
        return jsonify({"Error message": "Wrong json type. Doesn't contain product id."}), 403
    data["weight"] = float(data["weight"])
    data["height"] = float(data["height"])
    data["shape"] = float(data["shape"])
    output = get_ai_size.caculate_size(data)
    print(type(output))
    # response = Response(response=output,
    #                     status=200, mimetype='application/json')
    print(output)
    # print(response.data)

    return jsonify(output)


@app.route("/")
def home():
    return "<h1> HOME PAGE </h1>"


if __name__ == "__main__":
    app.run(debug=True)
