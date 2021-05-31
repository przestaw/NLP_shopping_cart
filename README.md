# Shopping list - NLP

Filling a cart based on a descriptive shopping list. Using NLP methods to find best matching products in a database.

## Description

Project goal was to develop NLP algorithm that will fill basket. To accomplish this goal we used NLTK implementation of tokenizer, porter stemmer and stoplist. We also used Quantulum3 model to detect units and quantities of products in listings and requests.

Algorithm is based on inverted files search algorithm witch some adjustments and additional quantity match step

## Usage

- *initialisation* :
  
    Project comes with filled database. There is a script `./feed_database.py` that you could use to fill up database with data from `./data/*.csv` and create index
- *running* :
    `./app.py` contains API specification using *flask*, API can be used to access, create and delete products (index is updated automatically)
  
- *demo*:
    `./curl_demo.sh` contains shell script that will demonstrate our API using *curl* for requests and *jq* for pretty JSON printing 


#### Examples:

- for list : 
  ```yaml
  [
    "A dozen organic eggs", 
    "1.5l of skimmed milk", 
    "3 kg of flour"
  ]
  ```
- result is :
  ```yaml
  {
    "products": [
     {
        "count": 2, 
        "product": {
          "amount": 6.0, 
          "description": "6-pack of fresh organic eggs", 
          "name": "6 EGGS", 
          "prod_id": 221, 
          "unit": "set"
        }
      }, 
      {
        "count": 3, 
        "product": {
          "amount": 0.5, 
          "description": "Tasty skimmed milk 0.5l", 
          "name": "SKIMMED MILK 2%", 
          "prod_id": 222, 
          "unit": "cubic decimetre"
        }
      }, 
      {
        "count": 6, 
        "product": {
          "amount": 0.5, 
          "description": "Baking flour 0.5 kg type 400", 
          "name": "FLOUR - 0.5kg", 
          "prod_id": 224, 
          "unit": "kilogram"
        }
      }
    ]
  }  
  ```

- for list : 
  ```yaml
  [
    "La La Land on dvd", 
    "That movie about kidnapped girls trying to escape", 
    "some popcorn",
    "a half dozen Quesadillas with chicken and vegetables"
  ]
  ```
- result is :
  ```yaml
  {
    "products": [
      {
        "count": 1, 
        "product": {
          "amount": 1.0, 
          "description": "A jazz pianist falls for an aspiring actress in Los Angeles.", 
          "name": "DVD movie: La La Land (2016)", 
          "prod_id": 232, 
          "unit": "dimensionless"
        }
      }, 
      {
        "count": 1, 
        "product": {
          "amount": 1.0, 
          "description": "Three girls are kidnapped by a man with a diagnosed 23 distinct personalities. They must try to escape before the apparent emergence of a frightful new 24th.", 
          "name": "DVD movie: Split (2016)", 
          "prod_id": 228, 
          "unit": "dimensionless"
        }
      }, 
      {
        "count": 1, 
        "product": {
          "amount": 1.0, 
          "description": "Salty corn snack for any movie - popcorn bucket - Tasty Brand", 
          "name": "Great POPCORN movie bucket", 
          "prod_id": 225, 
          "unit": "dimensionless"
        }
      },
      {
        "count": 6,
        "product": {
          "amount": 1,
          "description": "Southwest Chicken Quesadillas With Seasoned Vegetables - The Letter Company",
          "name": "SOUTHWEST CHICKEN QUESADILLAS WITH SEASONED VEGETABLES",
          "prod_id": 171,
          "unit": "dimensionless"
        }
      }
    ]
  }
  ```
