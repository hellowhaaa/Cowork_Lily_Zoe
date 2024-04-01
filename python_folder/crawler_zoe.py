import pymysql
import pymysql.cursors
import requests
from bs4 import BeautifulSoup
from configparser import ConfigParser
import threading
from time import sleep
import os
import csv
import json
import ast
# config file ----------------------------
current_directory = os.path.dirname(os.path.abspath(__file__))
#  config.ini 的絕對路徑
config_file_path = os.path.join(current_directory, '.config.ini')
# 建立 ConfigParser 對象
config = ConfigParser()
# 讀取 config.ini 文件
config.read(config_file_path)


database = config['DATA_BASE']

conn = pymysql.connect(host = database['host'],
                    user = database['user'],
                    password = database['password'],
                    database = database['database'],
                    cursorclass=pymysql.cursors.DictCursor,
                    charset="utf8mb4")

# my_cursor = db.cursor()
# print(my_cursor)

HEADERS = {
    'authority': 'scrapeme.live',
    'dnt': '1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'sec-fetch-site': 'none',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-user': '?1',
    'sec-fetch-dest': 'document',
    'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
}

cookies = {'enwiki_session': '17ab96bd8ffbe8ca58a78657a918558'}


# def get_items():
#     cursor = conn.cursor()
#     cursor.execute(
#         "SELECT DISTINCT(item1_id) AS item_id FROM similarity_model LIMIT 5000, 12"
#     )
#     conn.commit()
#     return cursor.fetchall()


# def get_similar_items(item_id):
#     cursor = conn.cursor()
#     cursor.execute(
#         f"SELECT item2_id AS item_id FROM similarity_model WHERE item1_id = '{
#             item_id}' ORDER BY similarity DESC LIMIT 6"
#     )
#     conn.commit()
#     return cursor.fetchall()


# def insert_product(item_id, title, source, image):
#     cursor = conn.cursor()
#     cursor.execute(
#         "INSERT INTO product (id, title, source, image_base64) VALUES(%s, %s, %s, %s)",
#         (item_id, title, source, image)
#     )
#     conn.commit()


def fetch_data(item_id='64352011'):
    url = f"https://www.lativ.com.tw/Detail/{item_id}"
    print("URL:", url)
    try:
        r = requests.get(url, headers=HEADERS, cookies=cookies)
        web_content = r.text
        soup = BeautifulSoup(web_content, 'html.parser')
        title = soup.find('span', id="productTitle").text.strip()
        image = soup.find(
            'div', id="main-image-container").find('img').get('src').strip()
        insert_product(item_id, title, 'amazon', image)
        print("OK")
    except Exception as e:
        print("ERROR:", url, e)


def get_subcategory(category, dict_category):
    url = f"https://www.lativ.com.tw/{category}/"
    print("URL:", url)
    # output = []
    try:
        r = requests.get(url, headers=HEADERS, cookies=cookies)
        web_content = r.text
        soup = BeautifulSoup(web_content, 'html.parser')
        # Find the div with id "sidenav"
        sidenav_div = soup.find('div', id='sidenav')

        # Check if the div is found
        if sidenav_div:
            # Find all <a> tags within the sidenav_div
            a_tags = sidenav_div.find_all('a')

            # Extract and print the href attributes
            # output_accessories = []
            for a_tag in a_tags:
                href = a_tag.get('href')
                # print(href)
                if 'accessories' in href:
                    dict_category['ACCESSORIES'].append(href)
                else:
                    dict_category[category].append(href)

        else:
            print("Couldn't find the div with id 'sidenav'")

        # print('here')
        return dict_category
    except Exception as e:
        print("ERROR: ", url, e)
        return None


def get_item_id(url):
    output = []
    try:
        r = requests.get(url, headers=HEADERS, cookies=cookies)
        web_content = r.text
        soup = BeautifulSoup(web_content, 'html.parser')
        a_list = soup.find_all("a", class_="imgd")
        for a in a_list:
            href = a.get('href')
            item = href.split('/')[-1]
            print(item)
            output.append(item)
    except Exception as e:
        print("ERROR: ", url, e)
    return output


def write_dict_csv(dict_data, filename):
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=dict_data.keys())

            # Write the header
            writer.writeheader()

            # Write the data rows
            writer.writerow(dict_data)

    except IOError:
        print("I/O error")


def read_csv_to_dict(filename):
    data_dict = {}
    # Open the CSV file for reading
    with open(filename, newline='') as csvfile:
        reader = csv.reader(csvfile)

        # Read the headers
        headers = next(reader)

        # Initialize dictionary keys with empty lists
        for header in headers:
            data_dict[header] = []

        # Read the rows and populate the dictionary
        for row in reader:
            for i, value in enumerate(row):
                if value.startswith("[") and value.endswith("]"):
                    # Convert the string representation to a list
                    value = ast.literal_eval(value)
                data_dict[headers[i]] += value

    return data_dict


# GET SUBCATEGORY

# subcategory = {}
# subcategory['WOMEN'] = []
# subcategory['MEN'] = []
# subcategory['ACCESSORIES'] = []
# get_subcategory('WOMEN', subcategory)
# get_subcategory('MEN', subcategory)
# write_dict_csv(subcategory, 'subcategory.csv')

# GET ID_LIST

# id_dict = {}
# id_dict['WOMEN'] = []
# id_dict['MEN'] = []
# id_dict['ACCESSORIES'] = []
# for ele in subcategory:
#     for url in subcategory[ele]:
#         if 'OnSale' not in url:
#             id_dict[ele] += get_item_id('https://www.lativ.com.tw/'+url)
#             sleep(2)
# write_dict_csv(id_dict, 'id_list.csv')

id_dict = read_csv_to_dict(
    '/Users/a123/Documents/GitHub/Stylish-Data-Engineering/Recommendation/id_list.csv')

print(id_dict)


# fetch_data()

# items = get_items()
# for item in items:
#     item_id = item['item_id']
#     t = threading.Thread(target=fetch_data, args=(item_id,))
#     t.start()
#     sleep(1)
#     fetch_data(item_id)
#     similar_items = get_similar_items(item_id)
#     for similar_item in similar_items:
#         t = threading.Thread(
#             target=fetch_data, args=(similar_item['item_id'],))
#         t.start()
#         sleep(1)
