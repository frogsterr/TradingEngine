#include "Order.h"
#include "Limit.h"
#include "Trade.h"
#include <map>
#include <unordered_map>
#include <string>
#include <atomic>
#include <chrono>

enum matchAlgo {FIFO, Prorata};

class Orderbook {
    public:
        std::map<int, Limit*> buySide;
        std::map<int, Limit*> askSide;
        std::unordered_map<int, Order*> orderMap;

        Orderbook();
        ~Orderbook();

        void add(Order* ord);
        void remove(Order* ord);
        void update(Order* ord, int p, int q);
        Trade match(matchAlgo m = matchAlgo::FIFO);       
};

