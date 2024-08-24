#include "Trade.h"
#include <atomic>
#include<iostream>

std::atomic<int> Trade::tradeCounter{0};
Trade::Trade(int p, int q)
    : tradeId(tradeCounter++), price(p), quantity(q), timeStamp(std::chrono::steady_clock::now()) {

}

Trade::~Trade() {

}

void Trade::display() {
    std::cout << "Trade ID: " << tradeId << ", Price: " << price << ", Quantity: " << quantity << std::endl;
}


