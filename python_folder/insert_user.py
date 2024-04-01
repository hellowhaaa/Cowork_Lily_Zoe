import os
from configparser import ConfigParser
import pymysql.cursors
import json
# config file ----------------------------
current_directory = os.path.dirname(os.path.abspath(__file__))
#  config.ini 的絕對路徑
parent_directory = os.path.dirname(current_directory)
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

query_insert_user = "  INSERT INTO user (role_id, provider, email, password, name, picture, access_token, access_expired, login_at)\
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
for i in range(4,101):
    my_cursor.execute(query_insert_user, (16, 'provider_name', 'user'+str(i)+'@example.com', 'password_hash', 'user'+str(i), 'picture_url', 'access_token_string', 1616161616161, '2024-03-30 12:00:00'))
    db.commit()