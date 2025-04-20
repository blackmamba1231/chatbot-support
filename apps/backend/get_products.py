import requests
import json

response = requests.get(
    'https://vogo.family/wp-json/wc/v3/products',
    auth=(
        'ck_47075e7afebb1ad956d0350ee9ada1c93f3dbbaa',
        'cs_c264cd481899b999ce5cd3cc3b97ff7cb32aab07'
    )
)

products = response.json()
with open('products_latest.json', 'w') as f:
    json.dump(products, f, indent=2)
