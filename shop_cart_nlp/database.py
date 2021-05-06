import sqlite3

from shop_cart_nlp.objects import Product, Stem


class DBaccess:
    # NOTE :
    #        queries may be static and allocated once !!!
    test_query = "SELECT name FROM sqlite_master WHERE type='table' AND name='products';"

    create_prod = "CREATE TABLE products" \
                  "(prod_id INTEGER PRIMARY KEY AUTOINCREMENT," \
                  "name TEXT NOT NULL UNIQUE," \
                  "description TEXT);"

    create_stem = "CREATE TABLE stems" \
                  "(stem_id INTEGER PRIMARY KEY AUTOINCREMENT," \
                  "value TEXT NOT NULL UNIQUE);"

    create_prod_stem = "CREATE TABLE product_stem" \
                       "(prod_id INTEGER " \
                       "REFERENCES products (prod_id) " \
                       "ON DELETE CASCADE " \
                       "ON UPDATE NO ACTION, " \
                       "stem_id INTEGER " \
                       "REFERENCES stems (stem_id) " \
                       "ON DELETE CASCADE " \
                       "ON UPDATE NO ACTION);"

    # NOTE :
    #        queries may be static and allocated once !!!

    def __init__(self, url='../data/db.sqlite'):
        self.con = sqlite3.connect(url)

    def test_db(self):
        """
        Check if table products exists
        :return: True if exists
        """
        cur = self.con.cursor()
        res = cur.execute(self.test_query)
        cur.close()
        return res.rowcount > 0

    def init_schema(self):
        """
        Initializes schema if not already initialized
        :return: None
        """
        if not self.test_db():
            # one transaction
            cur = self.con.cursor()
            cur.execute(self.create_prod)
            cur.execute(self.create_stem)
            cur.execute(self.create_prod_stem)
            # weird commit in sqlite API
            cur.connection.commit()
            cur.close()
        else:
            raise RuntimeWarning("Database has been already initialized")

    def add_stem(self, stem):
        """
        Insert stem to database if not exists
        :param stem: stem object or string
        :return: None
        """
        val = None
        if isinstance(stem, Stem):
            val = stem.value
        elif isinstance(stem, str):
            val = stem
        else:
            raise RuntimeError("Not a valid stem")

        cur = self.con.cursor()

        cur.execute("INSERT INTO stem(value) "
                    "VALUES (?);",
                    (val,))

        # weird commit in sqlite API
        cur.connection.commit()
        cur.close()

    def add_product(self, product: Product):
        """
        Insert a product if product with same name does not exist
        :param product: Product object to be inserted
        :return: None
        """

        if not isinstance(product, Product):
            raise RuntimeError("Not a valid object")

        cur = self.con.cursor()

        cur.execute("INSERT INTO product(name, description) "
                    "VALUES (?,?);",
                    (product.name, product.description))

        # weird commit in sqlite API
        cur.connection.commit()
        cur.close()

    def add_conn_p_s(self, product, stems: []):
        """
        Adds connection between product and stems from its description
        :param product: Product object
        :param stems: set of stems as strings
        """
        if len(stems) != 0:
            if not isinstance(product, Product):
                raise RuntimeError("Not a valid Product object")

            # NOTE : product.name, stems == stet of strings
            pairs = [(product.name, s) for s in stems]
            cur = self.con.cursor()

            cur.executemany("INSERT INTO product_stem(prod_id, stem_id) VALUES "
                            "(SELECT prod_id FROM products WHERE name = ?,"
                            "SELECT stem_id FROM stems WHERE value = ?);",
                            pairs)

            # weird commit in sqlite API
            cur.connection.commit()
            cur.close()

    def get_products_for_stem(self, stem):
        """
        Get all products referencing certain stem
        :param stem: stem object or string
        :return: list of products
        """
        val = None
        if isinstance(stem, Stem):
            val = stem.value
        elif isinstance(stem, str):
            val = stem
        else:
            raise RuntimeError("Not a valid stem")

        products = []
        cur = self.con.cursor()

        res = cur.execute("SELECT products.prod_id, products.name, products.description "
                          "FROM products "
                          "JOIN product_stem ON products.prod_id = product_stem.prod_id "
                          "WHERE product_stem.stem_id = ("
                          "    SELECT stem_id FROM stems WHERE value = ?"
                          ");",
                          ('ABC',))

        for line in res:
            products.append(Product(prod_id=line[0],
                                    name=line[1],
                                    description=line[2]))

        cur.close()
        return products

    def get_products(self):
        """
        Get all products
        :return: list of products
        """
        products = []
        cur = self.con.cursor()

        res = cur.execute("SELECT prod_id, name, description "
                          "FROM products;")

        for line in res:
            products.append(Product(prod_id=line[0],
                                    name=line[1],
                                    description=line[2]))

        cur.close()
        return products
