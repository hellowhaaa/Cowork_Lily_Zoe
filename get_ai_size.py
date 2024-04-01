import pymysql
import pymysql.cursors
from dotenv import load_dotenv
import os
from flask import jsonify
import scipy.stats as stats

load_dotenv()


# rds_db = pymysql.connect(host=os.getenv('RDS_DB_HOST'),
#                          user=os.getenv('RDS_DB_USER'),
#                          port=int(os.getenv('RDS_DB_PORT')),
#                          password=os.getenv('RDS_DB_PASSWORD'),
#                          database=os.getenv('RDS_DB_DATABASE'),
#                          cursorclass=pymysql.cursors.DictCursor
#                          )
# rds_db = pymysql.connect(host="co-work-database.c3g464ag65bx.us-east-1.rds.amazonaws.com",
#                          user="backend",
#                          port=3306,
#                          password="backend",
#                          database="co_work",
#                          cursorclass=pymysql.cursors.DictCursor
#                          )


def caculate_size(data):
    rds_db = pymysql.connect(host="localhost",
                             user="root",
                             port=3306,
                             password="password",
                             database="co_work",
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

    if len(size_list) == 0:
        return jsonify({"ai_size": 'S'})

    output = {"ai_size": 'S'}
    for i in range(len(size_list)):
        if size_list[i]['waist'] != None and waist > size_list[i]['waist']:
            output["ai_size"] = size_list[i]['size']
        elif size_list[i]['shoulder'] != None and shoulder > size_list[i]['shoulder']:
            output["ai_size"] = size_list[i]['size']
        elif size_list[i]['breast'] != None and breast > size_list[i]['breast']:
            output["ai_size"] = size_list[i]['size']

    return output


data = {
    "user_id": 123,
    "weight": 55,
    "height": 150,
    "shape": 2,
    "product_id": 201902191967
}
output = caculate_size(data)
print(output)
