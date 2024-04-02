import pymysql
import pymysql.cursors
from flask import jsonify
import os
from configparser import ConfigParser
import scipy.stats as stats
import json
import ipdb

current_directory = os.path.dirname(os.path.abspath(__file__))

config_file_path = os.path.join(current_directory, 'config.ini')
print(config_file_path)
config = ConfigParser()
config.read(config_file_path)


database = config['DATA_BASE']


def caculate_size(data):
    rds_db = pymysql.connect(host=database['host'],
                             user=database['user'],
                             port=3306,
                             password=database['password'],
                             database=database['database'],
                             cursorclass=pymysql.cursors.DictCursor
                             )

    rds_cursor = rds_db.cursor()

    sql = "select * from ratio order by id desc limit 1; "
    rds_cursor.execute(sql)
    ratio = rds_cursor.fetchone()
    print(ratio)

    weight = data["weight"]
    shape = data["shape"]
    waist = ratio["weight_waist_intercept"] + \
        weight*ratio["weight_waist_slope"]
    breast = ratio["weight_breast_intercept"] + \
        weight*ratio["weight_breast_slope"]
    shoulder = ratio["weight_shoulder_intercept"] + \
        weight*ratio["weight_shoulder_slope"]

    waist = waist/2
    breast = breast/2
    print(f"waist: {waist}, breast: {breast}, shoulder: {shoulder}")
    # ipdb.set_trace()
    sql = "select count(*) from website_body;"
    rds_cursor.execute(sql)
    num = rds_cursor.fetchone()['count(*)']
    alpha = 0.5  # Significance level
    t_critical = stats.t.ppf(1 - alpha/2, num-2)

    print(t_critical)
    if shape == 0:
        # waist = waist-ratio["weight_waist_rse"]*t_critical
        waist -= 1
        breast -= 1
        shoulder -= 1
    elif shape == 2:
        waist += 1
        breast += 1
        shoulder += 1
    else:
        pass
    print(f"waist: {waist}, breast: {breast}, shoulder: {shoulder}")

    sql = "select size, breast, waist, shoulder from lative_size where product_id = %s;"
    rds_cursor.execute(sql, (data["product_id"]))
    size_list = rds_cursor.fetchall()
    print(size_list)
    output = {'ai_size': 'S'}

    if len(size_list) == 0:
        return output

    for i in range(len(size_list)):
        if size_list[i]['waist'] != None and waist > size_list[i]['waist']:
            output["ai_size"] = size_list[i]['size']
        elif size_list[i]['shoulder'] != None and shoulder > size_list[i]['shoulder']:
            output["ai_size"] = size_list[i]['size']
        elif size_list[i]['breast'] != None and breast > size_list[i]['breast']:
            output["ai_size"] = size_list[i]['size']
    y = json.dumps(output)
    return output


# data = {
#     "user_id": 123,
#     "weight": 55,
#     "height": 150,
#     "shape": 2,
#     "product_id": 201902191967
# }

data = {'user_id': '111', 'weight': 168.0, 'height': 77.0,
        'shape': 0.0, 'product_id': '201902192273'}
output = caculate_size(data)
print(output)
