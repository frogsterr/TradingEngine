#ifndef ORDER_H
#define ORDER_H


#include <atomic>

class Limit;

enum class OrderType {Buy, Ask};
// Order class, orders belong in limit linked-list.
class Order {
    public:
        int id;
        int price;
        int quantity;
        OrderType type;
        Order *prevOrder;
        Order *nextOrder;
        Limit *limit;

        static std::atomic<int> idCounter; // Ensures thread-safe counter
        Order(int p, int q = 1, OrderType t = OrderType::Buy);
        ~Order();

        void info();
};


#endif // ORDER_H