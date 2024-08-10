from datetime import datetime, timedelta
import random
import pandas as pd
import time

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
        self.parent_limit = None
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
        
    # Removes order from limit list
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
'''
    # Finds new highest volume order, Time Complexity: O(n), maybe a faster way?
    def _update_highest_volume_order(self):
        if self.head_order:
            current_order = self.head_order
            highest_volume_order = current_order
            while current_order:
                if current_order.volume > highest_volume_order.volume:
                    highest_volume_order = current_order
                current_order = current_order.next_order
            self.highest_volume_order = highest_volume_order
        else:
            self.highest_volume_order = None
'''
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
        self.buy_head = None
        self.ask_head = None
        self.lowest_ask_limit = None
        self.highest_buy_limit = None
        self.order_map = {}
    
    def add(self, order: Order):
        if order.id in self.order_map:
            raise ReferenceError('Order already in orderbook')
        else:
            self.order_map[order.id] = order

        if order.order_type == 'buy':
            if self.buy_head is None:
                self.buy_head = Limit(order)
                self.highest_buy_limit = self.buy_head
            else:
                limit = self.buy_head
                while limit:
                    if order.price > limit.price:
                        if limit.higher_price is not None:
                            limit = limit.higher_price
                        else:
                            new_limit = Limit(order)
                            new_limit.parent_limit = limit
                            limit.higher_price = new_limit
                            if new_limit.price > self.highest_buy_limit.price:
                                self.highest_buy_limit = new_limit
                            return

                    elif order.price < limit.price:
                        if limit.lower_price is not None:
                            limit = limit.lower_price
                        else:
                            new_limit = Limit(order)
                            new_limit.parent_limit = limit
                            limit.lower_price = new_limit
                            return
                    else:
                        limit.ladd(order)
                        return
        
        if order.order_type == 'ask':
            if self.ask_head is None:
                self.ask_head = Limit(order)
                self.lowest_ask_limit = self.ask_head
            else:
                limit = self.ask_head
                while limit:
                    if order.price > limit.price:
                        if limit.higher_price is not None:
                            limit = limit.higher_price
                        else:
                            new_limit = Limit(order)
                            new_limit.parent_limit = limit
                            limit.higher_price = new_limit
                            return

                    elif order.price < limit.price:
                        if limit.lower_price is not None:
                            limit = limit.lower_price
                        else:
                            new_limit = Limit(order)
                            limit.lower_price = new_limit
                            if new_limit.price < self.lowest_ask_limit.price:
                                self.lowest_ask_limit = new_limit
                            return
                    else:
                        limit.ladd(order)
                        return

    
    def remove(self, order: Order):
        if order.id not in self.order_map:
            raise IndexError('Order does not exist')
        else:
            self.order_map[order.id].limit.remove(self.order_map[order.id])
            del self.order_map[order.id]

            if order.limit.is_empty():
                self.remove_limit(order.limit)

    def update(self, id: int, price: float = None, volume: int = None):
        if id in self.order_map:
            if price is not None and price > 0:
                self.order_map[id].price = price
            if volume is not None and volume > 0:
                self.order_map[id].volume = volume
        else:
            raise IndexError('Order ID not found in order map')


    def match(self):
            while self.buy_head and self.ask_head:
                self.fifo()
            print(f"Matching Complete!")

    def fifo(self):
        if self.buy_head and self.ask_head:
            print(f"Match Found! | Bid: {self.highest_buy_limit.volumeTotal} @ {self.highest_buy_limit.price} | Ask: {self.lowest_ask_limit.volumeTotal} @ {self.lowest_ask_limit.price} |")
            if self.highest_buy_limit.price >= self.lowest_ask_limit.price:
                trade_volume = min(self.lowest_ask_limit.head_order.volume, self.highest_buy_limit.head_order.volume)

                if self.lowest_ask_limit.head_order.volume - trade_volume == 0 and self.highest_buy_limit.head_order.volume - trade_volume == 0:
                    self.remove(self.lowest_ask_limit.head_order)
                    self.remove(self.highest_buy_limit.head_order)
                
                elif self.lowest_ask_limit.head_order.volume - trade_volume == 0:
                    self.highest_buy_limit.volumeTotal -= trade_volume
                    self.update(id=self.highest_buy_limit.head_order.id, volume=self.highest_buy_limit.head_order.volume - trade_volume)
                    self.remove(self.lowest_ask_limit.head_order)
                
                else:
                    self.lowest_ask_limit.volumeTotal -= trade_volume
                    self.update(id=self.lowest_ask_limit.head_order.id, volume=self.lowest_ask_limit.head_order.volume - trade_volume)
                    self.remove(self.highest_buy_limit.head_order)

        else:
            raise IndexError("One of the limit lists are empty.")
        
        
    # Removes limit order list from tree, potential memory leak if limit is not empty.
    def remove_limit(self, limit: Limit):

        if limit.lower_price and limit.higher_price:
            sub = limit.lower_price
            while sub.higher_price:
                sub = sub.higher_price
            sub.parent_limit.higher_price = None
            sub.higher_price = limit.higher_price
            sub.lower_price = limit.lower_price

            if limit == self.buy_head:
                self.buy_head = sub
                self.buy_head.parent_limit = None
            elif limit == self.ask_head:
                self.ask_head = sub
                self.ask_head.parent_limit = None
            else:
                if limit == limit.parent_limit.lower_price:
                    limit.parent_limit.lower_price = sub
                else:
                    limit.parent_limit.higher_price = sub

        elif limit.lower_price:
            if limit == self.buy_head:
                self.buy_head = limit.lower_price
                self.buy_head.parent_limit = None
            elif limit == self.ask_head:
                self.ask_head = limit.lower_price
                self.ask_head.parent_limit = None
            
            else:
                limit.parent_limit.lower_price = limit.lower_price
                limit.lower_price.parent_limit = limit.parent_limit
            
            if limit == self.highest_buy_limit:
                    self.highest_buy_limit = limit.lower_price
        
        elif limit.higher_price:
            if limit == self.buy_head:
                self.buy_head = limit.higher_price
                self.buy_head.parent_limit = None
            elif limit == self.ask_head:
                self.ask_head = limit.higher_price
                self.ask_head.parent_limit = None
            else:
                limit.parent_limit.lower_price = limit.higher_price
                limit.higher_price.parent_limit = limit.parent_limit
            
            if limit == self.lowest_ask_limit:
                self.lowest_ask_limit = limit.higher_price
        
        else:
            if limit == self.buy_head:
                self.buy_head = None
                self.highest_buy_limit = None # Node will be greatest bid if head
            elif limit == self.ask_head:
                self.ask_head = None
                self.lowest_ask_limit = None # Node will be lowest ask if head
            
            if limit == self.highest_buy_limit:
                self.highest_buy_limit = limit.parent_limit
                self.highest_buy_limit.higher_price = None
            
            elif limit == self.lowest_ask_limit:
                self.lowest_ask_limit = limit.parent_limit
                self.lowest_ask_limit.lower_price = None


        del limit

        if not self.buy_head and not self.ask_head:
            print("Order book is now empty.")



book = OrderBook()
'''
buy_order = Order(700, 'buy', 8)
buy_order1 = Order(650, 'buy', 2)
buy_order3 = Order(600, 'buy', 4)
buy_order4 = Order(675, 'buy' ,2)
buy_order2 = Order(750, 'buy', 4)

sell_order = Order(500, 'ask', 5)
sell_order2 = Order(600, 'ask', 2)


book.add(buy_order)
book.add(buy_order1)
book.add(buy_order3)
book.add(buy_order4)
book.add(sell_order)
book.add(sell_order2)


'''
for x in range(10):
    randprice = random.randint(700, 710)
    randvol = random.randint(1,4)
    book.add(Order(randprice, 'buy', randvol))

for x in range(10):
    randprice = random.randint(690, 704)
    randvol = random.randint(1,4)
    book.add(Order(randprice, 'ask', randvol))

def exc(func):
    start = time.time()
    func()
    end = time.time()
    return end-start

print(exc(book.match))