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

    # Метод, которого не хватало
    def is_empty(self):
        return len(self.cart) == 0

    def add(self, product, quantity=1, override_quantity=False):
        pid = str(product.pk)
        
        # Берем цену с учетом скидки, если она есть у модели
        actual_price = product.final_price if hasattr(product, 'final_price') else product.price

        if pid not in self.cart:
            self.cart[pid] = {"quantity": 0, "price": str(actual_price)}
        
        if override_quantity:
            self.cart[pid]["quantity"] = quantity
        else:
            self.cart[pid]["quantity"] += int(quantity)
        
        # Обновляем цену, чтобы скидка применилась сразу
        self.cart[pid]["price"] = str(actual_price)
        self.save()

    def __iter__(self):
        pks = self.cart.keys()
        products = Product.objects.filter(pk__in=pks)
        products_map = {str(p.pk): p for p in products}
        
        for pid, item in self.cart.items():
            product = products_map.get(pid)
            if not product:
                continue

            price = Decimal(item["price"])
            yield {
                "product": product,
                "quantity": item["quantity"],
                "price": price,
                "total_price": price * item["quantity"]
            }

    def get_total_price(self):
        return sum(Decimal(item["price"]) * item["quantity"] for item in self.cart.values())

    def save(self):
        self.session.modified = True

    def remove(self, product):
        pid = str(product.pk)
        if pid in self.cart:
            del self.cart[pid]
            self.save()

    def clear(self):
        self.session[self.SESSION_KEY] = {}
        self.save()

    def __len__(self):
        return sum(item["quantity"] for item in self.cart.values())

    def get_product_quantity(self, product):
        item = self.cart.get(str(product.id))
        return item["quantity"] if item else 0