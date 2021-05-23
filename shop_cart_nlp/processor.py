from math import ceil
from typing import Collection

from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
from quantulum3 import parser as qparser
from quantulum3.classes import Quantity

from shop_cart_nlp.database import DBaccess
from shop_cart_nlp.objects import Product


class Processor:
    # stoplist is common for all instances
    stoplist = stopwords.words('english') + ['%', ';', '-', '``', '(', ')', ':', ',', '.', '']
    stemmer = PorterStemmer()

    not_scalable_units = [
        "", "watt", "percentage", "yard", "year", "minute", "hour", "second", "byte", "decade", "megayear nanoseconds",
        "furlong", "dollar", "week", "week seconds", "atomic mass unit poise farads", "centavo ounce years", "degree",
        "milliampere nanoseconds", "inch second exaampere metres", "dime watt south african rands", "centavo", "dime watt roentgens",
        "degree celsius"
    ]
    dimensionless = "dimensionless"
    # non-numerical words
    dictionary = {
        "dimensionless": 1,
        "pair": 2,
        "dozen": 12,
        "gross": 144,
        "long hundred": 120,  # in text also as : "Small gross", "Great hundred"
        "great gross": 1728,
    }

    def __init__(self, database: DBaccess):
        """
        Constructor
        :param database: Database connection
        """
        self.database = database
        self.index = []

    @classmethod
    def tokenize(cls, string: str) -> []:
        """
        Interface to tokenizer
        :param string: sentences
        :return: words
        """
        # NOTE : tokenizer may be changed - api stays the same
        return word_tokenize(string)

    @classmethod
    def apply_stop_list(cls, array: Collection[str]) -> []:
        """
        Interface providing stoplist
        :param array: array of words
        :return: array with words not present in stoplist
        """
        # NOTE : we may add our own words to stoplist
        return [w for w in array if w not in cls.stoplist and not (len(w) == 1 and not w.isalnum())]

    @classmethod
    def apply_stemmer(cls, array: Collection[str]) -> []:
        """
        Interface to stemmer
        :param array: array of words
        :return: array of stems
        """
        # NOTE : stemmer is PorterStemmer which is a good stemmer
        return [cls.stemmer.stem(w) for w in array]

    @classmethod
    def split_to_stems(cls, string: str) -> []:
        """
        Pipeline converting description into bag of stems
        :param string: description
        :return: bag of stems
        """
        tmp = cls.tokenize(string)
        tmp = cls.apply_stop_list(tmp)
        tmp = cls.apply_stemmer(tmp)
        return set(tmp)  # only unique

    @classmethod
    def product_to_bag_of_stems(cls, product: Product) -> set:
        """
        Utility function converting prodyct name and description into bag of stems
        :param product: Product instance
        :return: bag of stems
        """
        name = cls.split_to_stems(product.name)
        desc = cls.split_to_stems(product.description)
        return set.union(name, desc)  # both name and desc

    @classmethod
    def find_quantity_for_product(cls, product: Product):
        """
        Utility function finding unit of offered product e. g. pair (=2)
        :param product: Product instance
        :return: pair(count, unit)
        """
        for string in product.name, product.description:
            q = next(iter(q for q in qparser.parse(string) if str(q.unit) not in cls.not_scalable_units), None)
            if q and q.value > 0.01:
                return q.value, str(q.unit)
        return 1, cls.dimensionless

    def create_index(self, products: Collection[Product]):
        """
        Method creating inverse stem index from collection of Products and parse product quantity
        :param products: collection of Products
        """
        self.index = []
        for prod in products:
            amount, unit = self.find_quantity_for_product(prod)
            prod.amount = amount
            prod.unit = unit
            stems = self.product_to_bag_of_stems(prod)
            self.index.append({'product': prod, 'stems': stems})

    def create_index_from_db(self):
        """
        Method creating inverse stem index from Products present in database
        """
        products = self.database.get_products()
        # NOTE : if we "update" index we have no way of knowing which products were processed
        #        hence database will ignore inserts on conflict
        self.create_index(products)

    def save_index_to_db(self):
        """
        Utility method inserting index (present in 'self' state) to database
        """
        # products
        products = [i['product'] for i in self.index]
        # unique stems
        stems = {s for i in self.index for s in i['stems']}

        # save quantities of products
        self.database.save_quantities_of_products(products)

        # add stems - or ignore
        self.database.add_stems(stems)

        # add connections
        for i in self.index:
            self.database.add_conn_p_s(i['product'], i['stems'])  # 'stems' is set

    def learn_from_db(self):
        """
        Method creating and saving index (from & to database)
        """
        self.create_index_from_db()
        self.save_index_to_db()

    def find_best_product(self, stems: Collection):
        """
        Finds best fitting product by performing inverse search
        :param stems: bag of stems from listing
        :return: best fitting product
        """

        def increment_dict(p_dict, value):
            if value in p_dict:
                p_dict[value] = 1 + p_dict[value]
            else:
                p_dict[value] = 1

        products_dict = {}
        for st in stems:
            prod_pivot = self.database.get_products_for_stem(st)
            for prod in prod_pivot:
                increment_dict(products_dict, str(prod.prod_id))

        if products_dict:
            most_prob_prod = max(products_dict, key=products_dict.get)
            return self.database.get_product(most_prob_prod)

        return None

    def find_quantities(self, position):
        """
        Parse quantity of product from position
        :param position: position in shopping list
        :return: quantity in array
        """
        quants = qparser.parse(position)
        # sanity check
        # print(str(quants[0].value) + " unit: " + str(quants[0].unit) if quants else "No quants")
        return quants if quants else [Quantity(1, self.dimensionless)]

    def calculate_count(self, product, quants):
        """
        Calculate how many products is needed
        :param product: Product instance
        :param quants: extracted count with unit
        :return: desired Products count (e.g. 2 pairs)
        """
        # if same as product
        for q in quants:
            if str(q.unit) == product.unit:
                return ceil(q.value / product.amount)

        # not the same unit & not dimensionless
        for q in quants:
            # NOTE : str() conversion to match type
            unit = self.dictionary.get(str(q.unit))
            if unit:
                amount = product.amount * self.dictionary.get(str(product.unit)) \
                    if self.dictionary.get(product.unit) \
                    else product.amount
                return ceil(unit / amount * quants[0].value)

        # not a product unit nor non-numerical word for quantity
        return ceil(quants[0].value)

    def find_products_for_shopping_list(self, shopping_list: Collection[str]):
        """
        From collection of shopping list positions generate best fitting products with count
        :param shopping_list: collection of shopping list positions
        :return: list of products with count
        """
        ret_list = list()

        # NOTE : for each :
        #                   - find counts,
        #                   - find stems [bag of words],
        #                   - inverse search for best product
        #                   - add to ret
        for pos in shopping_list:
            stems = self.split_to_stems(pos)
            product = self.find_best_product(stems)
            if product:
                quants = self.find_quantities(pos)
                count = self.calculate_count(product, quants)
                ret_list.append({'product': product, 'count': count})

        return ret_list
