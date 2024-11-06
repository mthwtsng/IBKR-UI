# ui_components.py

import tkinter as tk
from tkinter import ttk, messagebox

def create_market_data_labels(root):
    bid_label = ttk.Label(root, text="Bid: N/A")
    ask_label = ttk.Label(root, text="Ask: N/A")
    last_label = ttk.Label(root, text="Last: N/A")
    return bid_label, ask_label, last_label

def update_market_data_labels(bid_label, ask_label, last_label, data):
    bid_label['text'] = f"Bid: {data['bid']}"
    ask_label['text'] = f"Ask: {data['ask']}"
    last_label['text'] = f"Last: {data['last']}"

def request_market_data(ibkr_client, ticker_type, symbol, bid_label, ask_label, last_label):
    contract = ibkr_client.get_contract(ticker_type, symbol)
    if contract:
        data = ibkr_client.get_market_data(contract)
        update_market_data_labels(bid_label, ask_label, last_label, data)

def confirm_and_place_order(ibkr_client, ticker_type, symbol, action, quantity):
    if not messagebox.askyesno("Confirm Order", f"Place {action} order for {quantity} {symbol}?"):
        return

    contract = ibkr_client.get_contract(ticker_type, symbol)
    if contract:
        trade = ibkr_client.place_order(contract, action, quantity)
        messagebox.showinfo("Order Placed", f"{action} order for {quantity} contracts of {symbol} placed.")
