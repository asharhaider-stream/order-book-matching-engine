import pytest
from src.order import Order, Side, OrderType
from src.order_book import OrderBook


def test_no_match_when_book_empty():
    book = OrderBook()
    fills = book.submit_order(Order("b1", Side.BUY, 10, price=100))
    assert fills == []
    assert book.best_bid() == 100


def test_exact_quantity_match():
    book = OrderBook()
    book.submit_order(Order("s1", Side.SELL, 5, price=99))
    fills = book.submit_order(Order("b1", Side.BUY, 5, price=100))
    assert fills == [("s1", "b1", 99, 5)]
    assert book.best_ask() is None  # fully consumed


def test_partial_fill_leaves_resting_order():
    book = OrderBook()
    book.submit_order(Order("s1", Side.SELL, 3, price=99))
    fills = book.submit_order(Order("b1", Side.BUY, 10, price=100))
    assert fills == [("s1", "b1", 99, 3)]
    assert book.bids[100.0].total_quantity() == 7


def test_price_mismatch_no_trade():
    book = OrderBook()
    book.submit_order(Order("s1", Side.SELL, 5, price=101))
    fills = book.submit_order(Order("b1", Side.BUY, 5, price=100))
    assert fills == []
    assert book.best_bid() == 100
    assert book.best_ask() == 101


def test_market_order_discards_unfilled_remainder():
    book = OrderBook()
    book.submit_order(Order("s1", Side.SELL, 3, price=99))
    fills = book.submit_order(Order("b1", Side.BUY, 10, order_type=OrderType.MARKET))
    assert fills == [("s1", "b1", 99, 3)]
    assert book.best_bid() is None  # leftover 7 units discarded, not resting


def test_cancel_removes_resting_order():
    book = OrderBook()
    book.submit_order(Order("b1", Side.BUY, 5, price=100))
    assert book.cancel_order("b1", Side.BUY, 100)
    assert book.best_bid() is None

def test_self_trade_prevention_skips_own_order():
    book = OrderBook()
    book.submit_order(Order("s1", Side.SELL, 5, price=99, trader_id="alice"))
    fills = book.submit_order(Order("b1", Side.BUY, 5, price=100, trader_id="alice"))
    assert fills == []  # blocked — same trader
    assert book.best_ask() == 99  # s1 untouched


def test_self_trade_prevention_falls_through_to_other_trader():
    book = OrderBook()
    book.submit_order(Order("s1", Side.SELL, 5, price=99, trader_id="alice"))
    book.submit_order(Order("s2", Side.SELL, 5, price=99, trader_id="bob"))
    fills = book.submit_order(Order("b1", Side.BUY, 5, price=100, trader_id="alice"))
    assert fills == [("s2", "b1", 99, 5)]  # skips alice's s1, matches bob's s2    