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
# import crawler

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
    '/Users/a123/Documents/GitHub/Stylish-Data-Engineering/Recommendation/id_list.csv')


item_id = '65285011'


def fetch_size(item_id):
    url = f'https://www.lativ.com.tw/Product/SizeReport?styleNo={
        item_id[:-3]}&itemNo={item_id}'
    try:
        r = requests.get(url, headers=HEADERS, cookies=cookies)
        web_content = r.text
        # Parse the HTML content with BeautifulSoup
        soup = BeautifulSoup(web_content, 'html.parser')

        tbody_tag = soup.find('tbody')

        temp_dict = {}
        # Check if <tbody> tag is found
        if tbody_tag:
            # Crawl down the <tbody> tag
            for tr_tag in tbody_tag.find_all('tr'):
                t_flag = False
                t_name = ''
                for td_tag in tr_tag.find_all('td'):
                    cur_text = td_tag.text
                    if '\u3000' in cur_text:
                        cur_text = cur_text.replace("\u3000", "")

                    if t_flag == False:
                        t_name = cur_text
                        temp_dict[t_name] = []
                        t_flag = True
                    else:
                        temp_dict[t_name].append(cur_text)
                    print(cur_text)  # Print the text content of the cell
            print(temp_dict)
            return {
                "id": int(item_id),
                "size_detail": [temp_dict]
            }
        else:
            print("No <tbody> tag found in the HTML content.")
    except Exception as e:
        print("ERROR:", url, e)


def run_fetch_size_with_queue(item_queue, results_queue):
    while not item_queue.empty():
        sleep(3)
        item = item_queue.get()
        try:
            output = fetch_size(item)
            results_queue.put(output)
        except Exception as e:
            print(f"Error: {e}")


output = fetch_size(item_id)
print(output)


li_w = list(set(id_dict['WOMEN']))
li_m = list(set(id_dict['MEN']))
li_a = list(set(id_dict['ACCESSORIES']))
item_list = li_w+li_m+li_a

num_threads = 8
item_queue = queue.Queue()
result_queue = queue.Queue()
for i in range(len(item_list)):
    item_queue.put(item_list[i])

threads = []
for i in range(num_threads):
    t = threading.Thread(target=run_fetch_size_with_queue,
                         args=(item_queue, result_queue))
    threads.append(t)
    threads[i].start()

output_list = []
for _ in range(item_queue.qsize()):
    result = result_queue.get()
    if result != None:
        output_list.append(result)

f = open('size_detail.json', 'w')
json.dump(output_list, f, ensure_ascii=False)
f.close()

for i in range(num_threads):
    threads[i].join()
