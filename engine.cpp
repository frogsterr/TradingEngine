#include "Order.h"
#include "Limit.h"
#include "Orderbook.h"
#include <iostream>

int main(){
    std::cout << "Trading Engine Starting..." << std::endl;
    Orderbook ob = Orderbook();
    Order *ord = new Order(500, 2, OrderType::Buy);
    Order *ord2 = new Order(500, 2, OrderType::Ask);
    ob.add(ord);
    ob.add(ord2);
    Trade t = ob.match();
    t.display();
    return 0;
}

