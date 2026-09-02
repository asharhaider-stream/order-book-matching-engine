from sortedcontainers import SortedDict
from src.order import Order, OrderType, Side
from src.price_level import PriceLevel


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

        while order.quantity > 0 and opposite_book:
            best_price = self.best_ask() if order.side == Side.BUY else self.best_bid()

            can_match = order.order_type == OrderType.MARKET or \
                    (order.side == Side.BUY and order.price >= best_price) or \
                    (order.side == Side.SELL and order.price <= best_price)

            if not can_match:
                break

            price_level = opposite_book[best_price]
            resting_order = price_level.orders[0]  # FIFO — oldest first

            fill_qty = min(order.quantity, resting_order.quantity)
            fills.append((resting_order.order_id, order.order_id, best_price, fill_qty))

            order.quantity -= fill_qty
            resting_order.quantity -= fill_qty

            if resting_order.quantity == 0:
                price_level.orders.popleft()
                if price_level.is_empty():
                    del opposite_book[best_price]

        if order.quantity > 0:
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