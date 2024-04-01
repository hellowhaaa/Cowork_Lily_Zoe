import json

with open('/Users/lily_chou/Desktop/co_work/product2.json', 'r', encoding='utf-8') as file:
    data1 = json.load(file)

with open('/Users/lily_chou/Desktop/co_work/data.json', 'r', encoding='utf-8') as file:
    data2 = json.load(file)

combined_items = []

for item1 in data1:
    print(item1)
    category = item1["category"].upper()
    matched_items = data2.get(category, [])

    for item2 in matched_items:
        if str(item2["item_id"]) == str(item1["id"]):  # 确保两边的id类型一致
            combined_data = {
                "item_id": item1["id"],
                "category": item1["category"].lower(),
                "title": item1["title"],
                "description": "Null",
                "price": item1["price"],
                "place": item2["place"],
                "texture": item2["texture"],
                "wash": item2["wash"],
                "colors": item1['colors'],
                "sizes": item1["sizes"],
                "main_image": item1["main_image"],
                "images": item1["images"]
            }
            combined_items.append(combined_data)

# 将合并后的项目列表转换成JSON
combined_json = json.dumps(combined_items, ensure_ascii=False, indent=4)

unique_items = []
seen = set()

for item in combined_items:
    identifier = (item["item_id"], item["category"])  
    if identifier not in seen:
        unique_items.append(item)
        seen.add(identifier)


with open('combine_final2.json', 'w', encoding='utf-8') as f:
    json.dump(unique_items, f, ensure_ascii=False, indent=4)  # 使用 unique_items 而不是 combined_json