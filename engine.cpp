#include "Order.h"
#include "Limit.h"
#include <iostream>

int main(){
    std::cout << "Trading Engine Starting..." << std::endl;
    Order ord = Order(500, 2, OrderType::Buy);
    Order ord2 = Order(500, 4, OrderType::Buy);
    Limit lim = Limit(&ord);
    lim.ladd(&ord2);
    lim.printLimit();
    return 0;
}

