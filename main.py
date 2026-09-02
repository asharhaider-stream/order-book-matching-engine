from src.order import Order, Side
from src.order_book import OrderBook

book = OrderBook()

# Resting sell orders
book.submit_order(Order("s1", Side.SELL, 99.0, 3))
book.submit_order(Order("s2", Side.SELL, 99.5, 5))
book.submit_order(Order("s3", Side.SELL, 101.0, 10))

print("Best ask before match:", book.best_ask())

# Incoming buy that should eat through s1 and s2
fills = book.submit_order(Order("b1", Side.BUY, 100.0, 10))

print("Fills:", fills)
print("Best ask after match:", book.best_ask())
print("Remaining in b1's book (should be resting 2 @ 100):", book.bids)