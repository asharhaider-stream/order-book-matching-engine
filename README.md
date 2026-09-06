# Order Book Matching Engine

A limit order book with price-time priority matching, built from scratch — no external market-data dependency, pure data structures and matching logic.

## What it does

- Maintains bid and ask sides as sorted price levels (`sortedcontainers.SortedDict`), each holding a FIFO queue of orders so earlier orders at the same price fill first
- Matches limit and market orders with price-time priority, handling partial fills on both sides
- Rests unfilled limit orders in the book; discards unfilled market orders
- Prevents self-trades — a resting order from the same trader is skipped and matching falls through to the next eligible order or price level
- Supports order cancellation and modification (cancel-and-resubmit, so a modified order loses its original time priority — same as real exchanges)
- Includes a replay module that feeds real logged Binance depth data through the engine as synthetic orders, as a sanity check against real market shapes

## Setup

```bash
pip install -r requirements.txt
```

## Usage

```python
from src.order_book import OrderBook

book = OrderBook()
book.add_limit_order(trader_id="alice", side="buy", price=100.0, quantity=5)
book.add_limit_order(trader_id="bob", side="sell", price=100.0, quantity=3)
# bob's order matches against alice's resting order; alice has 2 remaining
```

## Testing

```bash
pytest
```

Covers empty book behavior, exact and partial fills, price mismatches, market orders, cancellations, and self-trade prevention.

## Part of a series

This is the second piece of a self-directed trading systems build:

1. [Binance depth data pipeline](https://github.com/asharhaider-stream/binance-data-pipeline) — done
2. [order-book-matching-engine](https://github.com/asharhaider-stream/order-book-matching-engine.git) — done
3. Backtester — in progress
4. Statistical arbitrage strategy — planned
