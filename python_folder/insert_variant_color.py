import os
from configparser import ConfigParser
import pymysql.cursors
import json
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



with open('/Users/lily_chou/Desktop/co_work/combine_final2.json', 'r', encoding='utf-8') as file:
    data = json.load(file)
    
    for product in data:
        lative_item_id = product["item_id"]
        category = product["category"],
        title = product["title"]
        description = "NULL",
        price = product['price'],
        place = product['place'],
        texture = product['texture']
        wash = product['wash']
        colors_list = product['colors'],
        note = "NULL",
        story = "NULL",
        sizes_list = product['sizes'],
        main_image = product['main_image'],
        images_list = product['images']
        avg_star = 0.0
        sold = 0
        # print(item_id, category, description, price, place, texture, wash, colors_list, note, story, sizes_list, main_image, images, avg_star)
        
        
        query_select_product_from_lative = "select id from product where lative_id = %s"
        my_cursor.execute(query_select_product_from_lative, (lative_item_id))
        product_id = my_cursor.fetchone()
        if product_id:
            product_id = product_id['id']
        
        # # ? -----  insert_product
        # query_insert_product = "INSERT INTO product (category, title, description, price, texture, wash, place, note, story, main_image, avg_star, sold, lative_id) VALUES \
        # (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        # my_cursor.execute(query_insert_product, (category, title, description, price, texture, wash, place, note, story, main_image, avg_star, sold, lative_item_id))
        # db.commit()
        
        # last_product_id = my_cursor.lastrowid
        
        # ? ----- insert_product_images
        
    
        
        # for image in images_list:
        #     query_insert_product_images = "INSERT INTO product_images (product_id, image) VALUES (%s, %s)"
        #     my_cursor.execute(query_insert_product_images, (last_product_id, image))
        #     db.commit()
        
        # ? ----- insert_colors
            for color in colors_list:
                for _ in color:
                    # code = _['name'].split("#")
                    # name = _['code']
                    query_insert_colors = "INSERT IGNORE INTO color (code, name) values (%s, %s)"
                    my_cursor.execute(query_insert_colors,(_['code'],_['name']))
                    # my_cursor.execute(query_insert_colors,(code, name))
                    
                    db.commit()
                    if my_cursor.rowcount > 0:
                        last_color_id = my_cursor.lastrowid
                    else:
                        # 如果颜色已存在，获取现有颜色的ID
                        query_select_color_id = "SELECT id FROM color WHERE code = %s"
                        my_cursor.execute(query_select_color_id, (_['code']))
                        result = my_cursor.fetchone()
                        last_color_id = result['id']
                
            # # ? ----- insert_colors variants
            query_insert_variants = "INSERT INTO variant(product_id, color_id, size, stock) VALUES (%s, %s, %s, %s)"
            # # --- get color_id
            for size in sizes_list:
                for _ in size:
                    my_cursor.execute(query_insert_variants,(product_id,last_color_id, _, 10))
                    db.commit()
        
        # # # ? ----- insert_colors comment
        # # query_insert_comments = "INSERT INTO comment (user_id, star, product_id) VALUES (%s, %s, %s)"
        # # my_cursor.execute(query_insert_comments,(789, 5, 123))



