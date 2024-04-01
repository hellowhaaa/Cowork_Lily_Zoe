from flask import Flask, render_template, request, url_for, redirect, jsonify, make_response
import random
import get_ai_size
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route("/python/recommendation", methods=['GET'])
def recommendation():
    item_id = request.args.get('id')
    print(item_id)

    temp_output = [
        {
            "id": 201902191811,
            "title": "雪紡印花荷葉襯衫",
            "price": 590,
            "main_image": "https://s.lativ.com.tw/i/60732/60732011/6073201_500.jpg",
        },
        {
            "id": 201902191812,
            "title": "嫘縈長袖襯衫",
            "price": 590,
            "main_image": "https://s.lativ.com.tw/i/60700/60700011/6070001_500.jpg",
        },
        {
            "id": 201902191817,
            "title": "亞麻混紡寬版V領襯衫",
            "price": 590,
            "main_image": "https://s.lativ.com.tw/i/60711/60711021/6071102_500.jpg",
        },
        {
            "id": 201902191548,
            "category": "WOMEN",
            "title": "棉麻七分袖襯衫",
            "price": 590,
            "main_image": "https://s.lativ.com.tw/i/64493/64493011/6449301_500.jpg",
        }
    ]
    return jsonify({"recommend": temp_output})


@app.route("/python/AI", methods=['POST'])
def AI():
    if not request.json:
        return jsonify({"Error message": "Wrong json type."}), 403
    data = request.json
    if "weight" not in data:
        return jsonify({"Error message": "Wrong json type. Doesn't contain weight."}), 403
    output = get_ai_size.caculate_size(data)

    return jsonify(output)


@app.route("/")
def home():
    return "<h1> HOME PAGE </h1>"


if __name__ == "__main__":
    app.run(debug=True)
