import sqlite3


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
        cur = self.con.cursor()
        res = cur.execute(self.test_query)
        cur.close()
        return res.rowcount > 0

    def init_schema(self):
        if not self.test_db():
            # one transaction
            cur = self.con.cursor()
            cur.execute(self.create_prod)
            cur.execute(self.create_stem)
            cur.execute(self.create_prod_stem)
            # weird commit in sqlite API
            cur.connection.commit()
        else:
            raise RuntimeWarning("Database has been already initialized")

    def add_product(self, product):
        # TODO insert ... on conflict ignore
        pass

    def add_stem(self, product):
        # TODO insert ... on conflict ignore
        pass

    def add_conn_p_s(self, product, stems: []):
        if len(stems) != 0:
            # NOTE : product.name, stems == stet of strings
            pairs = [(product.name, s) for s in stems]
            cur = self.con.cursor()

            cur.executemany("INSERT INTO product_stem(prod_id, stem_id) VALUES "
                            "(SELECT prod_id FROM products WHERE name = ?,"
                            "SELECT stem_id FROM stems WHERE value = ?)",
                            pairs)

            # weird commit in sqlite API
            cur.connection.commit()

    def get_products_for_stem(self, stem):
        products = []
        # TODO : select stem_id from stems where value = <stem>
        # TODO : select * from products join product_stem where stem_id = <id>
        return products

    def get_products(self):
        products = []
        # TODO : select * from products
        return products
