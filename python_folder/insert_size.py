import os
from configparser import ConfigParser
import pymysql.cursors
import json
import random
import pymysql
import pymysql.cursors

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



with open('/Users/lily_chou/Desktop/co_work/size_detail.json', 'r', encoding='utf-8') as file:
    data = json.load(file)
    
    for dic in data:
        lative_id = dic.get('id')  # Use get to avoid KeyError
        size_details = dic.get('size_detail', [{}])[0]  # Use get with default [{}]
        sizes = ['S', 'M', 'L', 'XL', 'XXL']
        
        # Make sure '尺碼' key exists
        if '尺碼' not in size_details:
            print(f"'尺碼' key is missing in the data for lative_id {lative_id}. Skipping this record.")
            continue
        
        size_index_map = {name: index for index, name in enumerate(size_details['尺碼'])}

        for size in sizes:
            if size not in size_details:
                print(f"Size {size} not found for lative_id {lative_id}. Skipping this size.")
                continue

            measurements = size_details.get(size)
            
            # Extract the measurements safely
            shoulder = measurements[size_index_map.get('肩寬')] if '肩寬' in size_index_map else None
            breast = measurements[size_index_map.get('胸寬')] if '胸寬' in size_index_map else None
            cloth_length = measurements[size_index_map.get('衣長')] if '衣長' in size_index_map else None
            waist = measurements[size_index_map.get('腰圍')] if '腰圍' in size_index_map else None
            hip = measurements[size_index_map.get('臀圍')] if '臀圍' in size_index_map else None

            # Prepare the data for insertion, converting to the correct types
            try:
                shoulder = float(shoulder) if shoulder is not None else None
                breast = float(breast) if breast is not None else None
                cloth_length = float(cloth_length) if cloth_length is not None else None
                waist = float(waist) if waist is not None else None
                hip = float(hip) if hip is not None else None
            except ValueError as e:
                print(f"Error converting sizes to float for lative_id {lative_id} size {size}: {e}")
                continue
            
            # Use parameterized queries for safety and avoid SQL injection
            sql = """
            INSERT INTO recommend_size (product_id, size, shoulder, breast, cloth_length, waist, hip) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """

            # Fetch the product_id from the database
            try:
                my_cursor.execute("SELECT id FROM product WHERE lative_id = %s", (lative_id,))
                product_id_result = my_cursor.fetchone()
                product_id = product_id_result['id'] if product_id_result else None
                
                if product_id is None:
                    print(f"Product ID not found for lative_id {lative_id}. Skipping insert.")
                    continue

                # Insert the data into the database
                my_cursor.execute(sql, (product_id, size, shoulder, breast, cloth_length, waist, hip))
                db.commit()
                
            except pymysql.MySQLError as e:
                print(f"Error inserting data for lative_id {lative_id} size {size}: {e}")
                db.rollback()

