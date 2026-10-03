# Inventory Management System
A small retail admin tool: a **Flask REST API** that manages inventory, a **command-line app** to use it, and a link to the **OpenFoodFacts** food database to fill in product details by barcode.
Built by Patience (GitHub: Patience1m) for the Flask REST API summative lab.

## What it can do
- Add, view, update and delete inventory items through a REST API
- Look up a product on OpenFoodFacts by barcode (or search by name)
- Import a looked-up product straight into the inventory with your own price and stock
- Do all of the above from a terminal menu
- Reject bad input with clear error messages
- Run 43 automated tests that need no internet

## Built with
Python 3, Flask, requests, pytest, pipenv.

## Getting started
git clone https://github.com/Patience1m/inventory-system.git
cd inventory-system
pipenv install --dev
pipenv shell

Start the API in one terminal:
python run.py

Start the menu in a second terminal (run `pipenv shell` there too):
python cli.py

The API runs at `http://127.0.0.1:5000` in Flask debug mode. Opening `/` in a browser shows "Not Found" because the API has no home page. Try `http://127.0.0.1:5000/inventory` instead.

## Using the menu
| Choice | What it does |
|---|---|
| 1 | Show every item |
| 2 | Show one item and its ingredients |
| 3 | Add a new item |
| 4 | Change an item's price and/or stock (leave a field blank to keep it) |
| 5 | Delete an item |
| 6 | Search OpenFoodFacts by barcode or name, then optionally add the result to the inventory |
| 0 | Quit |

Try it: choose `6`, type `b`, enter `3017620422003`, answer `y`, then give a price and a stock.

## API reference

Every reply has the form `{"success": true, "message": "...", "data": ...}`.

| Method | Route | What it does | Success | Errors |
|---|---|---|---|---|
| GET | `/inventory` | List all items | 200 | |
| GET | `/inventory/<id>` | Get one item | 200 | 404 |
| POST | `/inventory` | Create an item (`product_name` required) | 201 | 422 |
| PATCH | `/inventory/<id>` | Change fields such as `price` or `stock` | 200 | 404, 422 |
| DELETE | `/inventory/<id>` | Delete an item | 204 | 404 |
| GET | `/lookup/barcode/<code>` | Find a product on OpenFoodFacts | 200 | 404, 502 |
| GET | `/lookup/search?name=` | Search OpenFoodFacts by name | 200 | 422, 502 |
| POST | `/inventory/import/<code>` | Fetch by barcode and add to the inventory (body: `price`, `stock`) | 201 | 404, 409, 422, 502 |

Example:

```bash
curl -X POST http://127.0.0.1:5000/inventory \
     -H "Content-Type: application/json" \
     -d '{"product_name": "Milk", "price": 1.2, "stock": 30}'
```

```json
{
  "success": true,
  "message": "Item successfully created",
  "data": {"id": 4, "product_name": "Milk", "barcode": "", "brands": "",
           "ingredients_text": "", "price": 1.2, "stock": 30}
}
```

Error codes: 404 not found, 409 barcode already in inventory, 422 invalid input, 502 OpenFoodFacts could not be reached.

More detail on each route (inputs, outputs, what it changes, which menu option triggers it) is in [docs/DESIGN.md](docs/DESIGN.md).

## Project layout

```
run.py                  starts the API
config.py               development / testing / production settings
cli.py                  the terminal menu
app/
  __init__.py           builds the Flask app
  data.py               the inventory list (the "database") and helpers
  models.py             InventoryItem and its validation
  responses.py          standard JSON replies
  openfoodfacts.py      calls to OpenFoodFacts
  controller/           the routes (inventory + lookup)
tests/                  automated tests
docs/DESIGN.md          route design
```

## Running the tests

```bash
pytest -v
```

43 tests cover every route, the OpenFoodFacts code and every menu command. Web calls are replaced with fakes using `unittest.mock`, so the tests run offline.

## How the work was organised in Git

Each feature was built on its own branch, merged through a pull request, and the branch deleted:

1. `feature/crud-routes`: the Flask app, validation and the CRUD routes
2. `feature/external-api`: OpenFoodFacts functions and the lookup/import routes
3. `feature/cli`: the terminal menu
4. `fix/name-search`: name search moved to Search-a-licious, brands shown as text, controller update, README and design notes

## Good to know

- Data is stored in memory only. Restarting the API resets it to the three sample products.
- OpenFoodFacts' search service is sometimes unavailable. When that happens the API replies with a clear 502 error instead of crashing, and barcode lookups still work.
- OpenFoodFacts asks apps to identify themselves, so put your own email in the `User-Agent` in `app/openfoodfacts.py`.