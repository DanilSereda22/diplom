# apps/cart/cart.py
from decimal import Decimal
from store.models import Product

class Cart:
    SESSION_KEY = "cart"

    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(self.SESSION_KEY)
        if not cart:
            cart = self.session[self.SESSION_KEY] = {}
        self.cart = cart
        self.request = request

    def add(self, product: Product, quantity=1, override_quantity=False):
        pid = str(product.pk)
        if pid not in self.cart:
            self.cart[pid] = {"quantity": 0, "price": str(product.price)}
        if override_quantity:
            self.cart[pid]["quantity"] = quantity
        else:
            self.cart[pid]["quantity"] += int(quantity)
        self.save()

    def remove(self, product: Product):
        pid = str(product.pk)
        if pid in self.cart:
            del self.cart[pid]
            self.save()

    def save(self):
        self.session[self.SESSION_KEY] = self.cart
        self.session.modified = True

    def __iter__(self):
        pks = self.cart.keys()
        products = Product.objects.filter(pk__in=pks)
        products_map = {str(p.pk): p for p in products}
        for pid, item in self.cart.items():
            product = products_map.get(pid)
            item_data = {
                "product": product,
                "quantity": item["quantity"],
                "price": Decimal(item["price"]),
                "total_price": Decimal(item["price"]) * item["quantity"]
            }
            yield item_data

    def __len__(self):
        return sum(item["quantity"] for item in self.cart.values())

    def get_total_price(self):
        return sum(Decimal(item["price"]) * item["quantity"] for item in self.cart.values())

    def clear(self):
        self.session[self.SESSION_KEY] = {}
        self.session.modified = True

    def is_empty(self):
        return len(self.cart) == 0
