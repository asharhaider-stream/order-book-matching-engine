from sortedcontainers import SortedDict
from .order import Order, OrderType, Side
from .price_level import PriceLevel


class OrderBook:
    def __init__(self):
        self.bids = SortedDict()
        self.asks = SortedDict()

    def _book_for(self, side: Side) -> SortedDict:
        return self.bids if side == Side.BUY else self.asks

    def add_resting_order(self, order: Order) -> None:
        book = self._book_for(order.side)
        if order.price not in book:
            book[order.price] = PriceLevel(order.price)
        book[order.price].add_order(order)

    def best_bid(self) -> float | None:
        return self.bids.peekitem(-1)[0] if self.bids else None

    def best_ask(self) -> float | None:
        return self.asks.peekitem(0)[0] if self.asks else None

    def submit_order(self, order: Order) -> list:
        fills = []
        opposite_book = self.asks if order.side == Side.BUY else self.bids
        blocked_prices = set()  # price levels fully exhausted by self-trade check

        while order.quantity > 0:
            price_iter = opposite_book.keys() if order.side == Side.BUY else reversed(opposite_book.keys())
            best_price = next((p for p in price_iter if p not in blocked_prices), None)
            if best_price is None:
                break

            can_match = order.order_type == OrderType.MARKET or \
                (order.side == Side.BUY and order.price >= best_price) or \
                (order.side == Side.SELL and order.price <= best_price)
            if not can_match:
                break

            price_level = opposite_book[best_price]

            resting_order = next(
                (o for o in price_level.orders
                 if order.trader_id is None or o.trader_id != order.trader_id),
                None
            )
            if resting_order is None:
                blocked_prices.add(best_price)  # every order here is a self-trade — skip this level
                continue

            fill_qty = min(order.quantity, resting_order.quantity)
            fills.append((resting_order.order_id, order.order_id, best_price, fill_qty))

            order.quantity -= fill_qty
            resting_order.quantity -= fill_qty

            if resting_order.quantity == 0:
                price_level.orders.remove(resting_order)
                if price_level.is_empty():
                    del opposite_book[best_price]

        if order.quantity > 0 and order.order_type == OrderType.LIMIT:
            self.add_resting_order(order)

        return fills

    def cancel_order(self, order_id: str, side: Side, price: float) -> bool:
        book = self._book_for(side)
        if price not in book:
            return False
        price_level = book[price]
        for o in price_level.orders:
            if o.order_id == order_id:
                price_level.orders.remove(o)
                if price_level.is_empty():
                    del book[price]
                return True
        return False

    def modify_order(self, order_id, side, old_price, new_price, new_quantity) -> list:
        if not self.cancel_order(order_id, side, old_price):
            return []  # nothing was cancelled — don't submit a phantom new order
        new_order = Order(order_id, side, new_quantity, price=new_price)
        return self.submit_order(new_order)