import nltk
import csv
from shop_cart_nlp.database import DBaccess
from shop_cart_nlp.objects import Product
from shop_cart_nlp.processor import Processor

if __name__ == '__main__':
    nltk.download('popular')
    datasets = ['data/food.csv', 'data/movies.csv', 'data/outdoor.csv']
    products = []
    for i in datasets:
        with open(i) as file:
            reader = csv.reader(file)
            for line in reader:
                products.append(Product(line[0], line[1]))

    database = DBaccess()
    database.init_schema()
    database.add_products(products=products)

    #processor = Processor(database=database)
    #processor.learn_from_db()
