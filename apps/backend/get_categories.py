import requests
import json

response = requests.get(
    'https://vogo.family/wp-json/wc/v3/products/categories',
    auth=(
        'ck_47075e7afebb1ad956d0350ee9ada1c93f3dbbaa',
        'cs_c264cd481899b999ce5cd3cc3b97ff7cb32aab07'
    )
)

categories = response.json()

# Print categories in a readable format
print("Available Categories:")
for category in categories:
    print(f"ID: {category['id']}, Name: {category['name']}, Slug: {category['slug']}")

# Save full response to file
with open('categories_latest.json', 'w') as f:
    json.dump(categories, f, indent=2)
