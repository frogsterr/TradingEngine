#include "Order.h"
#include <iostream>

using namespace std;

atomic<int> Order::idCounter{0};

Order::Order(int p, int q, OrderType t)
    : id(idCounter++), price(p), quantity(q), type(t), prevOrder(nullptr), nextOrder(nullptr), limit(nullptr){

    if (p <= 0){
        throw invalid_argument("Price must be greater than 0.");
    }
    if (q <=0){
        throw invalid_argument("Order quantity must be greater than 0.");
    }
    if (t != OrderType::Buy && t != OrderType::Ask){
        throw invalid_argument("Incorrect Order Type");
    } 
}

// Prints ID, Price, and Volume of Order
void Order::info() {
    cout << "ID: " + to_string(id) + " | Price: " + to_string(price) + " | Quantity: " + to_string(quantity) << endl;
}

Order::~Order() {

}