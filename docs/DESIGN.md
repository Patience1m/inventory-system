# Design: routes, inputs, outputs and CLI triggers

## How the pieces connect

```
cli.py  ->  Flask routes (app/controller)  ->  list in app/data.py
                     |
                     +-> app/openfoodfacts.py -> OpenFoodFacts API
```

## Mock database (`app/data.py`)

A list of dicts shaped like OpenFoodFacts data. Every item has a unique `id`.

```json
{"id": 1, "barcode": "3017620422003", "product_name": "Nutella", "brands": "Ferrero",
 "ingredients_text": "Sugar, palm oil, ...", "price": 5.99, "stock": 20}
```

`barcode`, `product_name`, `brands` and `ingredients_text` come from (or mirror) OpenFoodFacts.
`price` and `stock` belong to the shop.

## Routes

Every response looks like `{"success": bool, "message": str, "data": ...}`.

| Route | Input | Output | What it changes | CLI trigger |
|---|---|---|---|---|
| `GET /inventory` | none | 200 list of items | nothing | Menu 1 (View all) |
| `GET /inventory/<id>` | id in URL | 200 item, or 404 | nothing | Menu 2 (View one) |
| `POST /inventory` | JSON: `product_name` (required), optional `barcode`, `brands`, `ingredients_text`, `price`, `stock` | 201 new item, or 422 | appends an item with a new id | Menu 3 (Add) |
| `PATCH /inventory/<id>` | id in URL, JSON with fields to change (not `id`) | 200 updated item, or 404 / 422 | updates that item | Menu 4 (Update price/stock) |
| `DELETE /inventory/<id>` | id in URL | 204, or 404 | removes the item | Menu 5 (Delete) |
| `GET /lookup/barcode/<code>` | barcode in URL | 200 product, or 404 / 502 | nothing | Menu 6, then `b` |
| `GET /lookup/search?name=` | `name` query parameter | 200 list of products, or 422 / 502 | nothing | Menu 6, then `n` |
| `POST /inventory/import/<code>` | barcode in URL, JSON `price` and `stock` | 201 new item, or 404 / 409 / 422 / 502 | fetches from OpenFoodFacts and appends to the list | Menu 6, `b`, then `y` |

## Error handling

- Invalid input (missing name, bad price, negative stock, unknown field, changing `id`): 422 with a message.
- Missing item or unknown product: 404. Barcode already in inventory: 409.
- OpenFoodFacts down or too slow: 502, and the CLI prints a clear message.
- The CLI asks again until numbers are valid, and prints "Could not reach the API" if Flask is not running.