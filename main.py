from datetime import datetime, timedelta
import random
import pandas as pd
import time
from sortedcontainers import SortedDict

class Market:
    def __init__(self) -> None:
        self.intratime = timedelta(milliseconds=1)
        self.base_price = 100  # Starting base price for the simulation

    def set_intratime(self, intratime: str):
        if intratime == 'milli':
            self.intratime = timedelta(milliseconds=1)
        elif intratime == 'micro':
            self.intratime = timedelta(microseconds=1)
        elif intratime == 's':
            self.intratime = timedelta(seconds=1)
        elif intratime == 'min':
            self.intratime = timedelta(minutes=1)
        elif intratime == 'h':
            self.intratime = timedelta(hours=1)
        elif intratime == 'd':
            self.intratime = timedelta(days=1)
        else:
            raise ValueError('Error, valid inputs: milli, micro, s, min, h, d')
        
    def generate_ticker(self, symbol: str = 'Unknown', prevTick: object = None,
                         time=datetime.now(), intratime: str = None):
        if intratime:
            self.set_intratime(intratime)

        symbol = prevTick.symbol if prevTick else symbol
        prev_bp = prevTick.bid_price if prevTick else self.base_price

        # Random walk with mean reversion to the base price
        mean_reversion_factor = 0.01
        random_walk = random.gauss(0, 0.2)  # Gaussian random walk component
        bp = round(prev_bp + mean_reversion_factor * (self.base_price - prev_bp) + random_walk, 2)
        bp = max(bp, 0)  # Ensure the bid price doesn't go negative

        # To simulate spread crossing or narrowing
        spread = random.uniform(0.01, 0.5)
        ap = bp + spread if random.random() > 0.1 else bp  # Occasionally allow bid and ask to match

        # Simulate trading volume patterns
        current_hour = time.hour
        if 9 <= current_hour < 10 or 15 <= current_hour < 16:
            volume_factor = 2  # Higher volume at market open/close
        else:
            volume_factor = 1

        bv = max(int(random.gauss(10, 5) * volume_factor), 0)
        av = max(int(random.gauss(10, 5) * volume_factor), 0)
        ltp = prevTick.last_traded_price if prevTick else None
        ltv = prevTick.last_traded_volume if prevTick else None
        timestamp = prevTick.timestamp + self.intratime if prevTick else time

        return Ticker(sym=symbol, bp=bp, ap=ap, bv=bv, av=av,
                      ltp=ltp, ltv=ltv, time=timestamp)

    #Creates a generator function with a synthetic market feed
    def generate_live_market(self, start: datetime, end: datetime, intratime: str = None):
        if start > end:
            raise ValueError('Error, start after end date.')

        if intratime:
            self.set_intratime(intratime)

        prev = self.generate_ticker('AAPL', time=start)
        yield prev

        while prev.timestamp < end:
            tick = self.generate_ticker(prevTick=prev)
            prev = tick
            yield tick
    
    #Generates a pandas dataframe of synthetic market feed
    def generate_df(self, start: datetime, end: datetime, intratime: str = None):
        if start > end:
            raise ValueError('Error, start after end date.')

        if intratime:
            self.set_intratime(intratime)

        data = []
        for tick in self.generate_live_market(start, end, intratime=intratime):
            data.append({
                'timestamp': tick.timestamp,
                'symbol': tick.symbol,
                'bid_price': tick.bid_price,
                'ask_price': tick.ask_price,
                'last_traded_price': tick.last_traded_price,
                'bid_volume': tick.bid_volume,
                'ask_volume': tick.ask_volume,
                'last_trade_volume': tick.last_traded_volume
            })

        return pd.DataFrame(data)

#Ticker class that measures contains various market information
class Ticker:
    def __init__(self, sym: str, bp: float, ap: float, bv: float,
                 av: float, ltp: float, ltv: float, time: datetime, prevTick: object = None) -> None:
        self.symbol = sym
        self.ask_price = ap
        self.bid_price = bp
        self.bid_volume = bv
        self.ask_volume = av
        self.last_traded_price = ltp if prevTick else None
        self.last_traded_volume = ltv if prevTick else None
        self.timestamp = time
        self.prev = prevTick
    
    def __repr__(self):
        return (f"timestamp={self.timestamp}, symbol={self.symbol}, "
                f"bid_price={self.bid_price}, ask_price={self.ask_price}, "
                f"last_traded_price={self.last_traded_price}, bid_volume={self.bid_volume}, "
                f"ask_volume={self.ask_volume}, last_trade_volume={self.last_traded_volume})")

#Limit node in the order book. Each limit node contains a double linked list of orders aswell as info for FIFO and Pro-rata
class Limit():
    def __init__(self, first_order) -> None:
        self.lower_price = None
        self.higher_price = None
        self.highest_volume_order = first_order
        self.head_order = first_order
        self.tail_order = first_order
        self.price = first_order.price
        self.volumeTotal = first_order.volume
        first_order.limit = self

    # Check if limit list is empty / if there are no orders at limit
    def is_empty(self) -> bool:
        return self.volumeTotal == 0
    
    # Adds order to limit list
    def ladd(self, order: object):
        order.limit = self
        # SHOULD REMOVE THIS EMPTY CHECK ONCE LIMIT GETS AUTO-DELETED WHEN EMPTY
        if self.is_empty():
            self.highest_volume_order = order
            self.head_order = order
            self.tail_order = order
        else:
            self.tail_order.next_order = order
            order.prev_order = self.tail_order
            self.tail_order = order
            if order.volume > self.highest_volume_order.volume:
                self.highest_volume_order = order
            self.volumeTotal += order.volume
        
    # Removes order from limit list, potential memory leaks if attributes aren't cleaned
    def remove(self, order: object):
        if self.is_empty():
            self.highest_volume_order = None
            raise IndexError("Limit is empty.")
        
        if order == self.head_order:
            self.head_order = order.next_order
            if self.head_order:
                self.head_order.prev_order = None
            else:
                # If head becomes None, the list is now empty
                self.tail_order = None
        elif order == self.tail_order:
            self.tail_order = order.prev_order
            if self.tail_order:
                self.tail_order.next_order = None
            else:
                # If tail becomes None, the list is now empty
                self.head_order = None
        else:
            order.prev_order.next_order = order.next_order
            order.next_order.prev_order = order.prev_order
        
        self.volumeTotal -= order.volume
        
        # Clear the order's references
        order.prev_order = None
        order.next_order = None
        
        del order
    
    def clear(self):
        if self.is_empty():
            for key in self.__dict__:
                self.__dict__[key] = None
        else:
            while not self.is_empty():
                self.remove(self.head_order)
            for key in self.__dict__:
                self.__dict__[key] = None

# Order class, contains various information about order such as price, volume, id, etc...
class Order():
    _id_counter = 0

    def __init__(self, price: float, order_type: str, volume: int = 1, time=datetime.now(), prev_order: object = None, next_order: object = None, limit: Limit = None) -> None:
        if volume < 1:
            raise ValueError('Volume less than 1')
        if order_type == 'buy':
            self.order_type = 'buy'
        elif order_type == 'ask':
            self.order_type = 'ask'
        else:
            raise ValueError(f'Unknown order_type: {order_type}')
        self.price = price
        self.volume = volume
        self.id = Order.get_next_id()
        self.prev_order = prev_order
        self.next_order = next_order
        self.limit = limit

    # Creates a semi-random order ID
    @staticmethod
    def get_next_id():
        Order._id_counter += 1
        return  Order._id_counter * random.uniform(1, 230)

# Orderbook which matches trades, adds orders, removes orders, etc. Time Complexities: | Adding Order: Log(n)|  Removing Order: O(1) | Matching Order: O(1) |   
class OrderBook():
    def __init__(self, matching_algo = 'FIFO') -> None:
        self.buy_side = SortedDict()
        self.ask_side = SortedDict()
        self.order_map = {}
    
    def add(self, order: Order):
        if order.id in self.order_map:
            raise ReferenceError('Order already in orderbook')
        else:
            self.order_map[order.id] = order

        if order.order_type == 'buy':
            if order.price in self.buy_side:
                self.buy_side[order.price].ladd(order)
            else:
                self.buy_side[order.price] = Limit(order)
        
        if order.order_type == 'ask':
            if order.price in self.ask_side:
               self.ask_side[order.price].ladd(order)
            else:
                self.ask_side[order.price] = Limit(order)

    
    def remove(self, order: Order):
        if order.id not in self.order_map:
            raise IndexError('Order does not exist')
        else:
            self.order_map[order.id].limit.remove(self.order_map[order.id])
            del self.order_map[order.id]
            if order.limit.is_empty():
                if order.order_type == 'buy':
                    self.buy_side.pop(order.price)
                else:
                    self.ask_side.pop(order.price)

    def update(self, id, price: float = None, volume: int = None):
        if id in self.order_map:
            if volume and volume > 0:
                self.order_map[id].volume = volume
            if price and price > 0:
                self.order_map[id].price = price
        else:
            raise IndexError('Order ID not found in order map')

    #FIX MATCH FOR DICT
    def match(self):
            while len(self.buy_side) > 0 and len(self.ask_side):
                self.fifo()
            print(f"Matching Complete!")
    # FIX FIFO FOR DICT
    def fifo(self):
        if len(self.buy_side) > 0 and len(self.ask_side) > 0:
            highest_buy_limit = self.buy_side.peekitem(-1)[1]
            lowest_ask_limit = self.ask_side.peekitem(0)[1]
            print(f"Buy side size: {len(book.buy_side)} | Ask side size: {len(book.ask_side)}")
            print(f"Match Found! | Bid: {highest_buy_limit.volumeTotal} @ {highest_buy_limit.price} | Ask: {lowest_ask_limit.volumeTotal} @ {lowest_ask_limit.price} |")
            if highest_buy_limit.price >= lowest_ask_limit.price:
                trade_volume = min(lowest_ask_limit.head_order.volume, highest_buy_limit.head_order.volume)

                if lowest_ask_limit.head_order.volume - trade_volume == 0 and highest_buy_limit.head_order.volume - trade_volume == 0:
                    self.remove(lowest_ask_limit.head_order)
                    self.remove(highest_buy_limit.head_order)
                
                elif lowest_ask_limit.head_order.volume - trade_volume == 0:
                    highest_buy_limit.volumeTotal -= trade_volume
                    self.update(id=highest_buy_limit.head_order.id, volume=highest_buy_limit.head_order.volume - trade_volume)
                    self.remove(lowest_ask_limit.head_order)
                
                else:
                    lowest_ask_limit.volumeTotal -= trade_volume
                    self.update(id=lowest_ask_limit.head_order.id, volume=lowest_ask_limit.head_order.volume - trade_volume)
                    self.remove(highest_buy_limit.head_order)

        else:
            raise IndexError("One of the limit lists are empty.")



book = OrderBook()

for x in range(15000):
    randp = random.uniform(701, 702)
    randv = random.randint(1, 3)
    book.add(Order(randp, 'buy', randv))


for x in range(15000):
    randp = random.uniform(700, 701)
    randv = random.randint(1, 3)
    book.add(Order(randp, 'ask', randv))

s = time.time()
book.match()
e = time.time()
print(e - s)