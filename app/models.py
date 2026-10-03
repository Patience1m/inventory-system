from dataclasses import dataclass, asdict

@dataclass
class InventoryItem:
    product_name: str = ""
    barcode: str = ""
    brands: str = ""
    ingredients_text: str = ""
    price: float = 0.0
    stock: int = 0
    id: int = 0

    def __post_init__(self):
        if not self.product_name:
            raise ValueError("product_name is required")
        if isinstance(self.price, bool) or not isinstance(self.price, (int, float)) or self.price < 0:
            raise ValueError("price must be a non-negative number")
        if isinstance(self.stock, bool) or not isinstance(self.stock, int) or self.stock < 0:
            raise ValueError("stock must be a non-negative integer")

    def to_dict(self) -> dict:
        return asdict(self)