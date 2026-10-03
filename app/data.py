inventory = []

seed_items = [
    {
        "id": 1,
        "barcode": "3017620422003",
        "product_name": "Nutella",
        "brands": "Ferrero",
        "ingredients_text": "Sugar, palm oil, hazelnuts, skimmed milk powder, cocoa",
        "price": 5.99,
        "stock": 20,
    },
    {
        "id": 2,
        "barcode": "5449000000996",
        "product_name": "Coca-Cola",
        "brands": "Coca-Cola",
        "ingredients_text": "Carbonated water, sugar, colour caramel, phosphoric acid",
        "price": 1.5,
        "stock": 50,
    },
    {
        "id": 3,
        "barcode": "0000000000001",
        "product_name": "Organic Almond Milk",
        "brands": "Silk",
        "ingredients_text": "Filtered water, almonds, cane sugar",
        "price": 3.49,
        "stock": 12,
    },
]

def load_seed_data():
    inventory.clear()
    inventory.extend(dict(item) for item in seed_items)

def find_item(item_id):
    return next((item for item in inventory if item["id"] == item_id), None)

def add_item(item):
    item.id = max((existing["id"] for existing in inventory), default = 0) + 1
    new_item = item.to_dict()
    inventory.append(new_item)
    return new_item