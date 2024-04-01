import csv
import json
with open('/Users/lily_chou/Desktop/co_work/json_csv_folder/combine_final2.json', 'r', encoding='utf-8') as file:
    data = json.load(file)
    lative_id_lis = []
    for line in data:
        lative_id = line["item_id"]
        lative_id_lis.append(lative_id)
    print(lative_id_lis)

with open('/Users/lily_chou/Desktop/co_work/json_csv_folder/lative_id_list.json', 'w', encoding='utf-8') as f:
    json.dump(lative_id_lis, f, ensure_ascii=False, indent=4)  # 使用 unique_items 而不是 combined_json