#include "Limit.h"
#include<stdexcept>
#include <iostream>

// Initializes Limit
Limit::Limit(Order *ord) 
    : price(ord->price), lowerPrice(nullptr), higherPrice(nullptr), volumeTotal(ord->quantity), headOrder(ord), tailOrder(ord) {
        if (ord != nullptr) {
            ord->limit = this;
        } else { // change this to a throw error
            std::cout << "Order doesn't exist." << std::endl;
        }
        
}

// Adds order to limit.
void Limit::ladd(Order *ord) {
    if (isEmpty()) { // which conditinal to use?
        headOrder = tailOrder = ord;
    } else {
        tailOrder->nextOrder = ord;
        ord->prevOrder = tailOrder;
        tailOrder = ord;
    }
}

// Removes order from Limit
void Limit::remove(Order *ord) {
    if (isEmpty()){
        throw std::invalid_argument("Limit is empty.");
    }
}

// Checks if Limit is empty
bool Limit::isEmpty() {
    if (headOrder==nullptr) {
        return true;
    } else {
        return false;
    }
}

// Prints values in Limit
void Limit::printLimit() {
    if (isEmpty()) {
        throw std::invalid_argument("Limit is empty");
    } else {
        Order *curr = headOrder;
        while(curr != nullptr) {
            std::cout << std::to_string(curr->price) + " ";
            Order *next = curr->nextOrder;
            curr = next;
        }
    }
}

Limit::~Limit(){
    
}