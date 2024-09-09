#include "Order.h"
#include "Limit.h"
#include "Orderbook.h"
#include <iostream>
#include <random>
#include <chrono>



int main() {
    try {
        std::cout << "Trading Engine Starting..." << std::endl;
        
        Orderbook ob;
        for (int x = 0; x < 10; x++) {
            int ap = rand() % 100;
            int bp = ap + rand() % 5;
            int av = rand() % 10;
            int bv = rand() % 10;
            Order *buyOrder = new Order(bp, bv, OrderType::Buy);
            Order *askOrder = new Order(ap, av, OrderType::Ask);
            
            try {
                ob.add(buyOrder);
                ob.add(askOrder);
            } catch (const std::exception& e) {
                std::cerr << "Error adding order: " << e.what() << std::endl;
                delete buyOrder;
                delete askOrder;
            }
        }

        std::cout << "Orders added successfully. Attempting to match..." << std::endl;
        
        Trade t = ob.match(matchAlgo::FIFO);
        while (t.quantity > 0) {
            t.display();
            t = ob.match(matchAlgo::FIFO);
        }

    } catch (const std::exception& e) {
        std::cerr << "An error occurred: " << e.what() << std::endl;
        return 1;
    } catch (...) {
        std::cerr << "An unknown error occurred." << std::endl;
        return 1;
    }

    std::cout << "Trading Engine Shutting Down..." << std::endl;
    return 0;
}