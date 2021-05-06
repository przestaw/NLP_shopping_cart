from flask import Flask, request, abort

from shop_cart_nlp.processor import Processor
from shop_cart_nlp.products import Products

app = Flask(__name__)

products = Products()
processor = Processor()

processor.create_index(products.get())


@app.route("/products", methods=['GET'])
def get_products():
    return {"products": products.get()}


@app.route("/cart", methods=['POST'])
def complete_cart():
    shopping_list_attr = "shoppingList"

    if not request.json or shopping_list_attr not in request.json:
        abort(400)

    shopping_list = request.json[shopping_list_attr]

    result = processor.get_products_for_shopping_list(shopping_list)

    return {"products": result}


app.run(debug=True)
