import random
import pandas as pd
from .order import Order, Side, OrderType
from .order_book import OrderBook


def split_quantity(total_qty: float, max_orders: int = 3) -> list[float]:
    """Randomly splits one aggregated depth level into N synthetic orders."""
    n = random.randint(1, max_orders)
    cuts = sorted(random.uniform(0, total_qty) for _ in range(n - 1))
    bounds = [0] + cuts + [total_qty]
    return [round(bounds[i + 1] - bounds[i], 8) for i in range(n)]


def replay_snapshot(book: OrderBook, row, order_counter: list) -> None:
    for price, qty in row["bids"]:
        price, qty = float(price), float(qty)
        for size in split_quantity(qty):
            order_counter[0] += 1
            book.submit_order(Order(
                order_id=f"o{order_counter[0]}",
                side=Side.BUY,
                quantity=size,
                price=price,
                order_type=OrderType.LIMIT,
                trader_id=f"synth_{random.randint(1, 20)}",
            ))

    for price, qty in row["asks"]:
        price, qty = float(price), float(qty)
        for size in split_quantity(qty):
            order_counter[0] += 1
            book.submit_order(Order(
                order_id=f"o{order_counter[0]}",
                side=Side.SELL,
                quantity=size,
                price=price,
                order_type=OrderType.LIMIT,
                trader_id=f"synth_{random.randint(1, 20)}",
            ))

if __name__ == "__main__":
    df = pd.read_parquet(r"C:\Users\Syed Musa\Documents\Projects\data_pipeline\data\depth_1788537279.parquet")
    book = OrderBook()
    order_counter = [0]

    for _, row in df.iterrows():  # start small, raise later
        replay_snapshot(book, row, order_counter)

    print("Best bid:", book.best_bid())
    print("Best ask:", book.best_ask())
    print("Total orders submitted:", order_counter[0])