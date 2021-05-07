import flask
from flask import Flask, request, abort

from shop_cart_nlp.database import DBaccess
from shop_cart_nlp.objects import Product
from shop_cart_nlp.processor import Processor

app = Flask(__name__)

database = DBaccess()
processor = Processor(database)

processor.create_index(database.get_products())


@app.route("/product", methods=['GET'])
def get_products():
    return {"products": database.get_products()}


@app.route("/product", methods=['POST'])
def add_products():
    products_attr = "products"
    if not request.json \
            or products_attr not in request.json \
            or not isinstance(request.json[products_attr], list):
        abort(400)

    products = []
    try:
        for p in request.json[products_attr]:
            products.append(Product(p['name'], p['description']))
    except KeyError:
        abort(400)

    try:
        database.add_products(products)
    except RuntimeError:
        abort(400)

    return flask.Response(status=200)


@app.route('/product/<prod_id>', methods=['DELETE'])
def delete_product(prod_id):
    database.remove_product(prod_id)
    return flask.Response(status=204)


@app.route("/cart", methods=['POST'])
def complete_cart():
    shopping_list_attr = "shoppingList"

    if not request.json or shopping_list_attr not in request.json:
        abort(400)

    shopping_list = request.json[shopping_list_attr]

    result = processor.get_products_for_shopping_list(shopping_list)

    return {"products": result}


app.run(debug=True)
