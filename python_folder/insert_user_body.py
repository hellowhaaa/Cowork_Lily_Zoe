
import os
from configparser import ConfigParser
import pymysql.cursors
import json
import random
# config file ----------------------------
current_directory = os.path.dirname(os.path.abspath(__file__))

parent_directory = os.path.dirname(current_directory)
#  config.ini 的絕對路徑
config_file_path = os.path.join(parent_directory, '.config.ini')
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

def random_height():
    # 身高范围
    heights = list(range(145, 181))
    # 选择与权重数量相同的身高
    num_weights = 35
    heights = random.choices(heights, k=num_weights)
    # 生成50个随机权重
    weights = [random.random() for _ in range(num_weights)]
    total_weight = sum(weights)
    # 根据总权重归一化
    weights = [w / total_weight for w in weights]
    # 使用 random.choices() 函数选择身高，并指定权重
    random_height = random.choices(heights, weights=weights, k=1)[0]
    random_height_m = random.choices(heights, weights=weights, k=1)[0]*0.01
    print("Random height:", random_height_m)
    bmi = 27
    #   bmi = kg/(m*m)    
    kg = bmi * random_height_m * random_height_m
    print(kg)
    shape = 1
    return (kg,random_height,shape)

for i in range(3,34):
    
    tuple = random_height()
    
    query_select_user_id = "select id from user where name = %s"
    my_cursor.execute(query_select_user_id,('user'+str(i)))
    user_id = my_cursor.fetchone()
    user_id = user_id['id']
    product_id = 201902191251
    query_insert_user_body  = "INSERT INTO user_body (user_id, weight, height, shape, product_id)\
    VALUES (%s, %s, %s, %s, %s)"
    my_cursor.execute(query_insert_user_body,(user_id, tuple[0], tuple[1], tuple[2], product_id))
    db.commit()




