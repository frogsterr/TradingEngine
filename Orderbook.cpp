#include <iostream>
#include "Order.h"
#include "Limit.h"
#include "Trade.h"
#include "Orderbook.h"
#include <map>
#include <unordered_map>
#include <string>
#include<stdexcept>
#include<chrono>


Orderbook::Orderbook()
    : buySide(), askSide(), orderMap(){

}

Orderbook::~Orderbook(){

}

void Orderbook::add(Order *ord){
    if (orderMap.contains(ord->id)) {
        throw std::invalid_argument("Order not in book.");
    } else {
            orderMap[ord->id] = ord;
            if (ord->type == OrderType::Buy) {
                if (buySide.contains(ord->price)) {
                    buySide[ord->price]->ladd(ord);
                } else {
                    buySide[ord->price] = new Limit(ord);
                }
            } else {
                    if (askSide.contains(ord->price)){
                        askSide[ord->price]->ladd(ord);
                    } else {
                        askSide[ord->price] = new Limit(ord);
                    }
            }
        }
    }

void Orderbook::remove(Order *ord){
    if (orderMap.contains(ord->id)){
        int price = ord->price;
        OrderType type = ord->type; 
        if (type == OrderType::Buy) {
            Limit *limit = buySide[price];
            limit->remove(ord);
            if (limit->isEmpty()) {
                delete limit;
                buySide.erase(price);
            }
        } else {
            Limit *limit = askSide[price];
            limit->remove(ord);
            if (limit->isEmpty()) {
                delete limit;
                askSide.erase(price);
            }
        }
        orderMap.erase(ord->id);
        delete ord;

    } else {
        throw std::invalid_argument("Order not found.");
    }
}

void Orderbook::update(Order *ord, int p, int q){
    if (orderMap.contains(ord->id)) {
        if (p > 0) {
            if (ord->type == OrderType::Buy) {
                if (buySide.contains(p)) {
                    Limit *old_lim = ord->limit;
                    old_lim->remove(ord);
                    if (old_lim->isEmpty()){
                        delete old_lim;
                        buySide.erase(old_lim->price);
                        
                    }
                    ord->price = p;
                    ord->limit = buySide[p];
                    buySide[p]->ladd(ord);
                } else {
                    ord->limit->remove(ord);
                    ord->price = p;
                    buySide[p] = new Limit(ord);
                }
            } else {
                if (askSide.contains(p)) {
                    Limit *old_lim = ord->limit;
                    old_lim->remove(ord);
                    if (old_lim->isEmpty()){
                        delete old_lim;
                        askSide.erase(old_lim->price);
                    }
                    ord->price = p;
                    ord->limit = askSide[p];
                    askSide[p]->ladd(ord);
                } else {
                    ord->limit->remove(ord);
                    ord->price = p;
                    askSide[p] = new Limit(ord);
                }
            }
        } else {
            throw std::invalid_argument("Price must be greater than 0.");
        }
        if (q >= 0){
            if (q==0){
                remove(ord);
            } else {
                ord->quantity = q;
            }
        } else {
            throw std::invalid_argument("Quantity must be greater than 0.");
        }
    } else {
        throw std::invalid_argument("Order ID not found.");
    }
}


Trade Orderbook::match(matchAlgo m) {
    if (m==matchAlgo::FIFO) {
        if (!buySide.empty() and !askSide.empty()) {
            Order *highestBuyOrder = buySide[buySide.rbegin()->first]->headOrder;
            Order *lowestAskOrder = askSide[askSide.begin()->first]->headOrder;

            if (highestBuyOrder->price >= lowestAskOrder->price) {
                int matchQuant = std::min(highestBuyOrder->quantity,  lowestAskOrder->quantity);
                int price = lowestAskOrder->price;

                highestBuyOrder->quantity -= matchQuant;
                lowestAskOrder->quantity -= matchQuant;
                highestBuyOrder->limit->volumeTotal -= matchQuant;
                lowestAskOrder->limit->volumeTotal -= matchQuant;

                if (highestBuyOrder->quantity == 0) {
                    remove(highestBuyOrder);
                }
                if (lowestAskOrder-> quantity ==0 ){
                    remove(lowestAskOrder);
                }
                return Trade(price, matchQuant);
            }           
        }
    return Trade(0,0); 
    }
}

