from shop_cart_nlp.database import DBaccess
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer


class Processor:
    # kind of a singleton - we need only one
    database = DBaccess()
    # stoplist is common for all instances
    stoplist = stopwords.words('english')
    stemmer = PorterStemmer()

    def __init__(self):
        self.index = []

    @classmethod
    def tokenize(cls, string: str) -> []:
        # NOTE : tokenizer may be changed - api i the same
        return word_tokenize(string)

    @classmethod
    def apply_stop_list(cls, array: []) -> []:
        # NOTE : we may add our own words to stoplist
        return [w for w in array if w not in cls.stoplist]

    @classmethod
    def apply_stemmer(cls, array: []) -> []:
        # NOTE : stemmer is PorterStemmer which is a good stemmer
        return [cls.stemmer.stem(w) for w in array]

    @classmethod
    def split_to_stems(cls, string: str) -> []:
        tmp = cls.tokenize(string)
        tmp = cls.apply_stop_list(tmp)
        tmp = cls.apply_stemmer(tmp)
        return set(tmp)  # only unique

    @classmethod
    def product_to_bag_of_stems(cls, product) -> set:
        title = cls.split_to_stems(product.title)
        desc = cls.split_to_stems(product.desc)
        return set.union(title, desc)  # both name and desc

    def create_index(self, products):
        for prod in products:
            stems = self.product_to_bag_of_stems(prod)
            self.index.append({'product': prod, 'stems': stems})

    def get_products_for_shopping_list(self, shopping_list):
        # TODO : angielski
        #          -> wyszukanie liczności [jeśli brak to pewnie zakładamy 1]
        #          -> zapytanie przez zbiory odwrtone [po stemach] każdej linijki "szoping list"
        #          -> zwracamy {"count" : xd, "product" : <ten najczęściej trafiony stemem>

        return self.index
