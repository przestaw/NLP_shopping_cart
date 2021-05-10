from collections.abc import Collection

from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize

from shop_cart_nlp.database import DBaccess
from shop_cart_nlp.objects import Product


class Processor:
    # stoplist is common for all instances
    stoplist = stopwords.words('english')
    stemmer = PorterStemmer()

    def __init__(self, database: DBaccess):
        self.database = database
        self.index = []

    @classmethod
    def tokenize(cls, string: str) -> []:
        # NOTE : tokenizer may be changed - api stays the same
        return word_tokenize(string)

    @classmethod
    def apply_stop_list(cls, array: Collection[str]) -> []:
        # NOTE : we may add our own words to stoplist
        return [w for w in array if w not in cls.stoplist]

    @classmethod
    def apply_stemmer(cls, array: Collection[str]) -> []:
        # NOTE : stemmer is PorterStemmer which is a good stemmer
        return [cls.stemmer.stem(w) for w in array]

    @classmethod
    def split_to_stems(cls, string: str) -> []:
        tmp = cls.tokenize(string)
        tmp = cls.apply_stop_list(tmp)
        tmp = cls.apply_stemmer(tmp)
        return set(tmp)  # only unique

    @classmethod
    def product_to_bag_of_stems(cls, product: Product) -> set:
        name = cls.split_to_stems(product.name)
        desc = cls.split_to_stems(product.description)
        return set.union(name, desc)  # both name and desc

    def create_index(self, products: Collection[Product]):
        tmp_index = []
        for prod in products:
            stems = self.product_to_bag_of_stems(prod)
            tmp_index.append({'product': prod, 'stems': stems})

        self.index = self.index + tmp_index
        # FIXME : if we return tmp_index we may train in increments:
        #              1. incrementally insert new products
        #              2. insert stems [ignore on duplicates
        #              3. insert connections/index

    def create_index_from_db(self):
        products = self.database.get_products()
        self.create_index(products)

    def save_index_to_db(self):
        # unique stems
        stems = set()
        for i in self.index:
            stems = stems.union(i['stems'])  # 'stems' is set

        # add stems - or ignore
        self.database.add_stems(stems)

        # add connections
        for i in self.index:
            self.database.add_conn_p_s(i['product'], i['stems'])  # 'stems' is set

    def learn_from_db(self):
        self.create_index_from_db()
        self.save_index_to_db()

    def find_best_product(self, stems: Collection):
        # TODO : count product occurances in queries for stems
        for st in stems:
            prod_pivot = self.database.get_products_for_stem(st)
            # TODO : update or create counters
        # TODO : find most probable product
        return Product(name='', description='')

    def find_products_for_shopping_list(self, shopping_list):
        # TODO : angielski XD
        #          -> wyszukanie liczności [jeśli brak to pewnie zakładamy 1]
        #          -> zapytanie przez zbiory odwrtone [po stemach] każdej linijki "szoping list"
        #          -> zwracamy {"count" : xd, "product" : <ten najczęściej trafiony stemem>

        ret_list = [{'product': None, 'count': 0}]
        # TODO : split list to positions
        positions = []

        # TODO : find counts, find stems [bag of words]
        for pos in positions:
            count = 0
            stems = []
            # TODO : find best product
            product = self.find_best_product(stems)
            ret_list.append({'product': product, 'count': count})

        return ret_list
