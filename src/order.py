from dataclasses import dataclass
from enum import Enum
import time

class Side(Enum):
    BUY = "buy"
    SELL = "sell"

class OrderType(Enum):
    LIMIT = "limit"
    MARKET = "market"


@dataclass
class Order:
    order_id: str
    side: Side
    quantity: float
    price: float = None
    order_type: OrderType = OrderType.LIMIT
    timestamp: float = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()
