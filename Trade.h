#ifndef TRADE_H
#define TRADE_H

#include<chrono>
#include<atomic>


class Trade {
    public:
        static std::atomic<int> tradeCounter;
        int tradeId;
        int price;
        int quantity;
        std::chrono::time_point<std::chrono::steady_clock> timeStamp;

        Trade(int p, int q);
        ~Trade();

        void display();
};

#endif // TRADE_H