#include "Limit.h"
#include<stdexcept>
#include <iostream>

// Initializes Limit
Limit::Limit(Order *ord) 
    : price(ord->price), lowerPrice(nullptr), higherPrice(nullptr), volumeTotal(ord->quantity), headOrder(ord), tailOrder(ord) {
    if (ord == nullptr) {
        throw std::invalid_argument("Cannot create Limit with null Order.");
    }
    ord->limit = this;
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
    volumeTotal += ord->quantity;
}

// Removes order from Limit
void Limit::remove(Order *ord) {
    if (isEmpty()){
        throw std::invalid_argument("Limit is empty.");
    }
    if (ord == headOrder){
        headOrder = headOrder->nextOrder;
        if (headOrder) {
            headOrder->prevOrder = nullptr;
        } else {
            tailOrder = nullptr;
        }
    } else if (ord == tailOrder) {
        tailOrder = tailOrder->prevOrder;
        if (tailOrder) {
            tailOrder->nextOrder = nullptr;
        } else {
            headOrder = nullptr;
        }
    } else {
        if (ord->prevOrder) {
            ord->prevOrder->nextOrder = ord->nextOrder;
        }
        if (ord->nextOrder) {
            ord->nextOrder->prevOrder = ord->prevOrder;
        }
    }
    ord->limit = nullptr;
    ord->prevOrder = nullptr;
    ord->nextOrder = nullptr;
    volumeTotal -= ord->quantity;
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