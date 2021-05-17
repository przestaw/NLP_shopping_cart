import sqlite3
from typing import Collection

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
                       "(prod_id INTEGER UNIQUE " \
                       "REFERENCES products (prod_id) " \
                       "ON DELETE CASCADE " \
                       "ON UPDATE NO ACTION, " \
                       "stem_id INTEGER UNIQUE " \
                       "REFERENCES stems (stem_id) " \
                       "ON DELETE CASCADE " \
                       "ON UPDATE NO ACTION, " \
                       "CONSTRAINT PRODUCT_STEM_PK PRIMARY KEY (prod_id, stem_id));"

    # NOTE :
    #        queries may be static and allocated once !!!

    def __init__(self, url='data/db.sqlite'):
        self.url = url

    def test_db(self):
        """
        Check if table products exists
        :return: True if exists
        """
        con = sqlite3.connect(self.url)
        cur = con.cursor()
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
            con = sqlite3.connect(self.url)
            cur = con.cursor()
            cur.execute(self.create_prod)
            cur.execute(self.create_stem)
            cur.execute(self.create_prod_stem)
            # weird commit in sqlite API
            cur.connection.commit()
            cur.close()
        else:
            raise RuntimeWarning("Database has been already initialized")

    def delete_all_data(self):
        """
        Delete all data from database [intended for debugging and "retrain"]
        """
        con = sqlite3.connect(self.url)
        cur = con.cursor()

        cur.execute("DELETE FROM product_stem;")
        cur.execute("DELETE FROM products;")
        cur.execute("DELETE FROM stems;")

        # weird commit in sqlite API
        cur.connection.commit()
        cur.close()

    def add_stem(self, stem):
        """
        Insert stem to database if not exists
        :param stem: stem object or string
        :return: None
        """
        if isinstance(stem, Stem):
            val = stem.value
        elif isinstance(stem, str):
            val = stem
        else:
            raise RuntimeError("Not a valid stem")

        con = sqlite3.connect(self.url)
        cur = con.cursor()

        cur.execute("INSERT OR IGNORE INTO stems (value) "
                    "VALUES (?) ",
                    (val,))

        # weird commit in sqlite API
        cur.connection.commit()
        cur.close()

    def add_stems(self, stems: Collection[str]):
        """
        Insert stem to database if not exists
        :param stems: list of stems as strings
        :return: None
        """
        if not stems:
            return

        query = "INSERT OR IGNORE INTO stems (value) VALUES"
        values = list()
        for s in stems:
            query += "(?),"
            values.append(s)
        query = query[:-1]

        con = sqlite3.connect(self.url)
        cur = con.cursor()

        try:
            cur.execute(query, values)

            # weird commit in sqlite API
            cur.connection.commit()
        except sqlite3.IntegrityError:
            raise RuntimeError
        finally:
            cur.close()

    def add_products(self, products: Collection[Product]):
        """
        Insert new products, ignoring those which already exist
        :param products: Product objects to be inserted
        :return: None
        """
        if not products:
            return

        con = sqlite3.connect(self.url)
        cur = con.cursor()

        query = "INSERT OR IGNORE INTO products (name, description) VALUES"
        values = list()
        for p in products:
            query += "(?,?),"
            values += [p.name, p.description]
        query = query[:-1]

        try:
            # NOTE : add final semicolon
            cur.execute(query, values)

            # weird commit in sqlite API
            cur.connection.commit()
        except sqlite3.IntegrityError:
            raise RuntimeError
        finally:
            cur.close()

    def add_conn_p_s(self, product: Product, stems: Collection[str]):
        """
        Adds connection between product and stems from its description
        :param product: Product object
        :param stems: set of stems as strings
        """
        if not product or not stems:
            return

        con = sqlite3.connect(self.url)
        cur = con.cursor()

        if product.prod_id is None:
            res = cur.execute("SELECT prod_id FROM products WHERE name = ?", [product.name])
            if res.rowcount == 0:
                raise RuntimeError("Can't find product with name " + product.name + " in the database")
            product.prod_id = res.fetchone()[0]
        prod_id = product.prod_id

        query = "INSERT OR IGNORE INTO product_stem (prod_id, stem_id) VALUES"
        values = list()
        for s in stems:
            query += "(?, (SELECT stem_id FROM stems WHERE value = ?)),"
            values += [prod_id, s]
            print(str([prod_id, s]))
        query = query[:-1]

        cur.execute(query, values)

        # weird commit in sqlite API
        cur.connection.commit()
        cur.close()

    def get_products_for_stem(self, stem):
        """
        Get all products referencing certain stem
        :param stem: stem object or string
        :return: list of products
        """
        if isinstance(stem, Stem):
            val = stem.value
        elif isinstance(stem, str):
            val = stem
        else:
            raise RuntimeError("Not a valid stem")

        products = []
        con = sqlite3.connect(self.url)
        cur = con.cursor()

        res = cur.execute("SELECT products.prod_id, products.name, products.description "
                          "FROM products "
                          "JOIN product_stem ON products.prod_id = product_stem.prod_id "
                          "WHERE product_stem.stem_id = ("
                          "    SELECT stem_id FROM stems WHERE value = ?"
                          ");",
                          (val,))

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
        con = sqlite3.connect(self.url)
        cur = con.cursor()

        res = cur.execute("SELECT prod_id, name, description "
                          "FROM products;")

        products = [Product(prod_id=line[0], name=line[1], description=line[2]) for line in res]

        cur.close()
        return products

    def get_product(self, prod_id):
        """
        Get product for id
        :return: product or none
        """
        con = sqlite3.connect(self.url)
        cur = con.cursor()

        res = cur.execute("SELECT prod_id, name, description "
                          "FROM products WHERE prod_id = ?;",
                          (prod_id,))

        if res:
            row = res.fetchone()
            product = Product(prod_id=row[0], name=row[1], description=row[2])
        else:
            product = None

        cur.close()
        return product

    def remove_product(self, prod_id):
        con = sqlite3.connect(self.url)
        cur = con.cursor()

        cur.execute("DELETE FROM products "
                    "WHERE prod_id = ?;", prod_id)
        cur.connection.commit()

        cur.close()
