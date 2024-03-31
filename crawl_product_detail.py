import queue
import botocore
from botocore.exceptions import ClientError
import boto3
import base64
import pymysql
import pymysql.cursors
import requests
from bs4 import BeautifulSoup
import threading
from time import sleep
import os
from dotenv import load_dotenv
import csv
import json
import ast

load_dotenv(verbose=True)

# db_host = os.environ.get('DB_HOST')
# db_user = os.environ.get('DB_USERNAME')
# db_password = os.environ.get('DB_PASSWORD')
# db_database = os.environ.get('DB_DATABASE')

# conn = pymysql.connect(
#     host=db_host,
#     user=db_user,
#     password=db_password,
#     database=db_database,
#     cursorclass=pymysql.cursors.DictCursor
# )

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


def get_items():
    cursor = conn.cursor()
    cursor.execute(
        "SELECT DISTINCT(item1_id) AS item_id FROM similarity_model LIMIT 5000, 12"
    )
    conn.commit()
    return cursor.fetchall()


def get_similar_items(item_id):
    cursor = conn.cursor()
    cursor.execute(
        f"SELECT item2_id AS item_id FROM similarity_model WHERE item1_id = '{
            item_id}' ORDER BY similarity DESC LIMIT 6"
    )
    conn.commit()
    return cursor.fetchall()


def insert_product(item_id, title, source, image):
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO product (id, title, source, image_base64) VALUES(%s, %s, %s, %s)",
        (item_id, title, source, image)
    )
    conn.commit()


def check_fetch_not_equal(url, item_id):
    try:
        r = requests.get(url, headers=HEADERS, cookies=cookies)
        web_content = r.text
        soup = BeautifulSoup(web_content, 'html.parser')
        title_id = soup.find('span', id="isn").text
        # print(f"title2: {title_id}")
        if title_id == item_id:
            return False, ''

        cur_color = soup.find('span', id="icolor").text
        return True, cur_color
    except Exception as e:
        print("ERROR:", url, e)


def image_to_base64(url):
    # Fetch the image from the URL
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Encode the image content into base64
        base64_image = base64.b64encode(response.content).decode('utf-8')
        return base64_image
    else:
        print("Failed to fetch the image")
        return None


s3 = boto3.client(
    "s3",
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
)


def upload_file_to_s3(upload_file, bucket=os.getenv('AWS_BUCKET_NAME'), upload_file_s3_name=None):
    if upload_file_s3_name is None:
        upload_file_s3_name = os.path.basename(upload_file)
    try:
        s3.upload_file(upload_file, bucket, upload_file_s3_name)
    except ClientError as e:
        print(f"upload error: ", e)
        return False
    return True


def size_int_to_string(size_int_list):
    output = []
    for ele in size_int_list:
        if ele == 1:
            output.append('S')
        if ele == 2:
            output.append('M')
        if ele == 3:
            output.append('L')
        if ele == 4:
            output.append('XL')
        if ele == 5:
            output.append('XXL')

    return output


def match_color_code(color_name):
    if '藍' or '青' in color_name:
        return '#0000FF'
    if '紅' in color_name:
        return '#FF0000'
    if '橘' or '橙' in color_name:
        return '#FFA500'
    if '黃' in color_name:
        return '#FFFF00'
    if '綠' in color_name:
        return '#00FF00'
    if '紫' in color_name:
        return '#B399FF'
    if '灰' in color_name:
        return '#808080'
    return '#FFFFFF'


def fetch_data(item_id, category):
    url = f"https://www.lativ.com.tw/Detail/{item_id}"
    print("URL:", url)
    try:
        r = requests.get(url, headers=HEADERS, cookies=cookies)
        web_content = r.text
        soup = BeautifulSoup(web_content, 'html.parser')

        title = soup.find('span', class_="title1").text.split('-')[0]
        print(f"title: {title}")

        price = soup.find('span', id='price').text
        print(f"price: {price}")

        colors = []
        cur_color = soup.find('span', id="icolor").text
        print(f"cur_color: {cur_color}")
        colors.append({"code": match_color_code(cur_color), "name": cur_color})

        size_int_list = []
        size_int_list.append(int(item_id) % 10)

        # use url to get colors and sizes
        for i in range(1, 5):
            test_color = str(int(item_id)+10*i)
            test_size = str(int(item_id)+1*i)
            test_color_url = f"https://www.lativ.com.tw/Detail/{test_color}"
            test_size_url = f"https://www.lativ.com.tw/Detail/{test_size}"
            flag_c, ad_color = check_fetch_not_equal(test_color_url, item_id)
            flag_s, temp_s = check_fetch_not_equal(test_size_url, item_id)
            if flag_c == True:
                # color_names.append(ad_color)
                # color_code.append(match_color_code(ad_color))
                colors.append(
                    {"code": match_color_code(ad_color), "name": ad_color})
            if flag_s == True:
                size_int_list.append(int(test_size) % 10)
        size_list = size_int_to_string(size_int_list)

        # IMAGE
        main_img = soup.find('img', id="productImg").get('src').strip()
        img_list = []
        img_div = soup.find('div', class_="oldPic show")
        if img_div:
            img_source = img_div.find_all('img')
            for img in img_source:
                img_temp = img.get('data-original')
                if img_temp != None:
                    img_list.append(img_temp)

        output_json = {
            "id": int(item_id),
            "category": category,
            "title": title,
            "price": int(price),
            "colors": colors,
            "sizes": size_list,
            "main_image": main_img,
            "images": img_list
        }
        print("OK")
        return output_json
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


def run_fetch_data_with_queue(item_queue, result_queue, category):
    while not item_queue.empty():
        sleep(3)
        item = item_queue.get()
        try:
            output = fetch_data(item, category)
            result_queue.put(output)
        except Exception as e:
            print(f"Error: {e}")

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

li_w = list(set(id_dict['WOMEN']))
li_m = list(set(id_dict['MEN']))
li_a = list(set(id_dict['ACCESSORIES']))


num_threads = 8
result_queue = queue.Queue()


liw_queue = queue.Queue()
for i in range(len(li_w)):
    liw_queue.put(li_w[i])

liw_threads = []
for i in range(num_threads):
    tliw = threading.Thread(target=run_fetch_data_with_queue,
                            args=(liw_queue, result_queue, 'WOMEN'))
    liw_threads.append(tliw)
    liw_threads[i].start()

lim_queue = queue.Queue()
for i in range(len(li_m)):
    liw_queue.put(li_m[i])

lim_threads = []
for i in range(num_threads):
    tlim = threading.Thread(target=run_fetch_data_with_queue,
                            args=(lim_queue, result_queue, 'MEN'))
    lim_threads.append(tlim)
    lim_threads[i].start()

lia_queue = queue.Queue()
for i in range(len(li_a)):
    lia_queue.put(li_a[i])

lia_threads = []
for i in range(num_threads):
    tlia = threading.Thread(target=run_fetch_data_with_queue,
                            args=(lia_queue, result_queue, 'ACCESSORIES'))
    lia_threads.append(tlia)
    lia_threads[i].start()


output_list = []
for _ in range(result_queue.qsize()):
    result = result_queue.get()
    if result != None:
        output_list.append(result)

f = open('product.json', 'w')
json.dump(output_list, f, ensure_ascii=False)
f.close()

for i in range(num_threads):
    liw_threads[i].join()
    lim_threads[i].join()
    lia_threads[i].join()

# START FETCHING DATA


# product = []

# for item in id_dict['WOMEN']:
#     output_temp = fetch_data(item, 'WOMEN')
#     product.append(output_temp)
#     sleep(1)

# for item in id_dict['MEN']:
#     output_temp = fetch_data(item, 'MEN')
#     product.append(output_temp)
#     sleep(1)

# for item in id_dict['ACCESSORIES']:
#     output_temp = fetch_data(item, 'ACCESSORIES')
#     product.append(output_temp)
#     sleep(1)
