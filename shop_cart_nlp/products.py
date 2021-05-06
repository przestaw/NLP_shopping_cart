import json
import sys

FILE_NAME = "../data/data.json"


class Products:
    def __init__(self):
        try:
            with open(FILE_NAME) as file:
                self.products = json.loads(file.read())
        except IOError:
            sys.exit("ERROR: Could not open the file '" + FILE_NAME + "'. Aborting.")

    def get(self):
        return self.products
