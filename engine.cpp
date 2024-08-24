#include "Order.h"
#include "Limit.h"
#include "Orderbook.h"
#include <iostream>

int main(){
    std::cout << "Trading Engine Starting..." << std::endl;
    Orderbook ob = Orderbook();
    Order *ord = new Order(500, 2, OrderType::Buy);
    ob.add(ord);
    ob.remove(ord);
    return 0;
}

