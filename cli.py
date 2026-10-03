import requests

API = "http://127.0.0.1:5000"

def prompt_float(label):
    while True:
        try:
            value = float(input(label).strip())
            if value >= 0:
                return value
        except ValueError:
            pass
        print("Please enter a valid non-negative number.")

def prompt_int(label):
    while True:
        try:
            value = int(input(label).strip())
            if value >= 0:
                return value
        except ValueError:
            pass
        print("Please enter a valid non-negative whole number.")

def call_api(method, path, **kwargs):
    try:
        response = getattr(requests, method)(f"{API}{path}", timeout = 15, **kwargs)
        return response.status_code, (response.json() if response.content else None)
    except requests.RequestException as error:
        print(f"Could not reach the API: {error}")
    except ValueError:
        print("The API returned an invalid response.")
    return None, None

def show(item):
    print(f'#{item["id"]} {item["product_name"]} | brand: {item["brands"]} '
          f'| barcode: {item["barcode"]} | ${item["price"]} | stock: {item["stock"]}')

def report_error(status, body):
    print(f"Error ({status}): {body.get('message') if body else 'unknown error'}")

def view_all():
    status, body = call_api("get", "/inventory")
    if status == 200:
        if not body["data"]:
            print("Inventory is empty.")
        for item in body["data"]:
            show(item)
    elif status:
        report_error(status, body)

def view_one():
    item_id = prompt_int("Item ID: ")
    status, body = call_api("get", f"/inventory/{item_id}")
    if status == 200:
        show(body["data"])
        print("Ingredients:", body["data"]["ingredients_text"] or "n/a")
    elif status:
        report_error(status, body)

def add_item():
    name = input("Product name: ").strip()
    if not name:
        print("Product name cannot be empty.")
        return
    payload = {
        "product_name": name,
        "brands": input("Brand: ").strip(),
        "barcode": input("Barcode (optional): ").strip(),
        "price": prompt_float("Price: "),
        "stock": prompt_int("Stock: "),
    }
    status, body = call_api("post", "/inventory", json = payload)
    if status == 201:
        print("Added:")
        show(body["data"])
    elif status:
        report_error(status, body)

def update_item():
    item_id = prompt_int("Item ID to update: ")
    price = input("New price (blank to skip): ").strip()
    stock = input("New stock (blank to skip): ").strip()
    payload = {}
    try:
        if price:
            payload["price"] = float(price)
        if stock:
            payload["stock"] = int(stock)
    except ValueError:
        print("Invalid number entered. Nothing was changed.")
        return
    if not payload:
        print("Nothing to update.")
        return
    status, body = call_api("patch", f"/inventory/{item_id}", json = payload)
    if status == 200:
        print("Updated:")
        show(body["data"])
    elif status:
        report_error(status, body)

def delete_item():
    item_id = prompt_int("Item ID to delete: ")
    status, body = call_api("delete", f"/inventory/{item_id}")
    if status == 204:
        print(f"Item {item_id} deleted.")
    elif status:
        report_error(status, body)

def import_from_api(code):
    payload = {"price": prompt_float("Price: "), "stock": prompt_int("Stock: ")}
    status, body = call_api("post", f"/inventory/import/{code}", json = payload)
    if status == 201:
        print("Imported:")
        show(body["data"])
    elif status:
        report_error(status, body)

def find_on_api():
    mode = input("Search by (b)arcode or (n)ame? ").strip().lower()
    if mode == "b":
        code = input("Barcode: ").strip()
        status, body = call_api("get", f"/lookup/barcode/{code}")
        if status == 200:
            print(f'Found: {body["data"]["product_name"]} ({body["data"]["brands"]})')
            if input("Add to inventory? (y/n): ").strip().lower() == "y":
                import_from_api(code)
        elif status:
            report_error(status, body)
    elif mode == "n":
        name = input("Product name: ").strip()
        status, body = call_api("get", "/lookup/search", params = {"name": name})
        if status == 200:
            if not body["data"]:
                print("No results.")
            for product in body["data"]:
                print(f'- {product["product_name"]} ({product["brands"]}) barcode: {product["barcode"]}')
        elif status:
            report_error(status, body)
    else:
        print("Please choose 'b' or 'n'.")

MENU = """
1) View all   2) View one   3) Add   4) Update price/stock
5) Delete     6) Find on OpenFoodFacts   0) Quit"""

ACTIONS = {
    "1": view_all,
    "2": view_one,
    "3": add_item,
    "4": update_item,
    "5": delete_item,
    "6": find_on_api,
}

def main():
    while True:
        print(MENU)
        choice = input("Choose: ").strip()
        if choice == "0":
            print("Goodbye!")
            break
        action = ACTIONS.get(choice)
        if action:
            action()
        else:
            print("Invalid choice, try again.")

if __name__ == "__main__":
    main()