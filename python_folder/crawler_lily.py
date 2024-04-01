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

db = pymysql.connect(host = database['host'],
                    user = database['user'],
                    password = database['password'],
                    database = database['database'],
                    cursorclass=pymysql.cursors.DictCursor,
                    charset="utf8mb4")


my_cursor = db.cursor()
print(my_cursor)


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



def fetch_description(item_id):
    style_no = item_id[0:5]
    url = f"https://www.lativ.com.tw/Product/ProductDesc?styleNo={style_no}&itemNo={item_id}"
    print("URL:", url)
    try:
        r = requests.get(url, headers=HEADERS, cookies=cookies)
        web_content = r.text
        soup = BeautifulSoup(web_content, 'html.parser')
        # print(soup)
        div = soup.find('div', class_="productDesc")
        lis = div.find('ul').find_all('li')
        # print(lis)
        # ? ------ place ------- 小心冒號格式
        place_parsed = lis[0].text.split("：")[1].strip()
        print(place_parsed)
        
        # ? ------ texture ------ 小心冒號格式
        if len(lis) >= 1:
            texture = lis[1].text
            if ":" in texture:
                text_parsed = texture.split(":")[1].strip()
            else:
                text_parsed = texture
        else:
            text_parsed = "NULL"
        print(text_parsed)
        place_div = soup.find('div', class_="productDesc")
        lis2 = div.find_all('ul')[1].find_all('li')
        wash_parsed = lis2[1].text
        print(lis2)
        print(wash_parsed)
        if "色" in wash_parsed:
            wash_parsed = wash_parsed.split('※')[1].split("。")[0].strip()
        else:
            wash_parsed = "NULL"
        print(wash_parsed)
        
        return [place_parsed, text_parsed, wash_parsed]
        
    except Exception as e:
        print("ERROR:", url, e)
        
# fetch_description('64352011')


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


id_dict = read_csv_to_dict(
    '/Users/lily_chou/Desktop/co_work/id_list.csv')

all_data = {}
ls = []
data = {}
def read_id(id_dict):
    all_data = {}  # 存储所有数据的字典

    for category, id_list in id_dict.items():
        ls = []  # 每个类别开始时初始化一个新的列表

        for id in id_list:
            print(id, "--> ")
            three_des_list = fetch_description(id)
            print(three_des_list)

            # 在每次循环开始时创建一个新的字典
            data = {}  # 创建一个新的字典来存储当前项目的信息
            place, texture, wash = three_des_list  # 直接解包，假设fetch_description总是返回三个值

            # 更新data字典
            data["item_id"] = id
            data["place"] = place
            data["texture"] = texture
            data["wash"] = wash

            # 将新的data字典添加到当前类别的列表中
            ls.append(data)

        # 将处理好的类别数据列表添加到总字典中
        all_data[category] = ls

    # 将所有数据写入JSON文件
    with open('data2.json', 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=4)


read_id(id_dict)


    
