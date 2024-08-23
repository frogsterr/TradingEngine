#ifndef LIMIT_H
#define LIMIT_H

#include "Order.h"

class Limit {
    public:
        int price;
        int *lowerPrice;
        int *higherPrice;
        int volumeTotal;
        Order *headOrder;
        Order *tailOrder;

        Limit(Order *ord);
        ~Limit();

        bool isEmpty(); // Checks if limit list is empty
        void ladd(Order *ord); // Adds order to limit
        void remove(Order *ord); // Removes order from list
        void clear(); // Clears limit of orders.
        void printLimit(); // Prints orders in limit
};






#endif // LIMIT_H
