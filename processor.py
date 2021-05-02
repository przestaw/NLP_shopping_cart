class Processor:
    def __init__(self):
        self.index = []

    def create_index(self, products):
        self.index = products

    def get_products_for_shopping_list(self, shopping_list):
        return self.index
