import nltk
import flask
from flask import Flask, request, abort

from shop_cart_nlp.database import DBaccess
from shop_cart_nlp.objects import Product
from shop_cart_nlp.processor import Processor

app = Flask(__name__)


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

    try:
        database.add_products(
            [Product(p["name"], p["description"]) for p in request.json[products_attr]]
        )
    except KeyError as e:
        return "Invalid JSON object. The following key was not found: " + str(e), 400
    except RuntimeError as e:
        return "Failed to add products. Details: " + str(e), 400

    try:
        processor.learn_from_db()
    except Exception as e:
        print("ERROR updating index. Exception: " + str(e))

    return flask.Response(status=200)


@app.route('/product/<prod_id>', methods=['DELETE'])
def delete_product(prod_id):
    database.remove_product(prod_id)
    return flask.Response(status=204)


@app.route("/cart", methods=['POST'])
def complete_cart():
    shopping_list_attr = "shoppingList"
    if not request.json \
            or shopping_list_attr not in request.json:
        abort(400)

    products = processor.find_products_for_shopping_list(
        request.json[shopping_list_attr]
    )

    return {"products": products}


if __name__ == '__main__':
    nltk.download('stopwords')  # if downloaded it will skip
    nltk.download('punkt')
    # NOTE : global scope
    database = DBaccess()
    processor = Processor(database)

    # TODO : any init steps
    processor.learn_from_db()

    app.run(debug=True)
