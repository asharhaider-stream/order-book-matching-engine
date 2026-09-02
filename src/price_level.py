from collections import deque
from src.order import Order


class PriceLevel:
    def __init__(self, price: float):
        self.price = price
        self.orders: deque[Order] = deque()

    def __repr__(self) -> str:
        return f"PriceLevel(price={self.price}, orders={len(self.orders)}, qty={self.total_quantity()})"    

    def add_order(self, order: Order) -> None:
        self.orders.append(order)

    def total_quantity(self) -> float:
        return sum(o.quantity for o in self.orders)

    def is_empty(self) -> bool:
        return len(self.orders) == 0