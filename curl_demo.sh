#!/bin/bash

echo '# get project info'
curl -s -X GET localhost:5000/info | jq .

sleep 0.2

echo '# product with id 175'
curl -s -X GET localhost:5000/product/175 | jq .

for cart in \
  '["10 Sweet sweet butter", "Some fresh green peas", "five sweet brownie"]' \
  '["Two clean cotton sweatshirts", "One regular fit blue cotton denim jeans"]'\
  '["A dozen organic eggs", "1.5l of skimmed milk", "3 kg of flour"]'\
  '["La La Land on dvd", "That movie about kidnapped girls trying to escape", "some popcorn", "Guardians of the galaxy the movie"]'\
  '["a half dozen Quesadillas with chicken and vegetables", "3 packs of almond cereal"]'\
  '["Some pancakes", "World According to Bikers - cotton shirt", "Big trucker hat"]'
do
  echo "# Current shopping list :"
  echo -e "\t $cart"
  echo "# Press any key to send request"
  read -r -n1 key

  echo "# prediction for list : $cart"
  curl -s --header "Content-Type: application/json" \
    --request POST  \
    --data "{\"shoppingList\": $cart }" \
    http://localhost:5000/cart | jq .
done