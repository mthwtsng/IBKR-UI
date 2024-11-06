# main.py

import tkinter as tk
from tkinter import ttk
from ibkr_client import IBKRClient  # Ensure this import is correct
import ui_components

# Initialize IBKR client
ibkr_client = IBKRClient()

# Setup the main Tkinter window
root = tk.Tk()
root.title("IBKR Market Data and Order Placement")
root.geometry("400x400")

# Ticker type selection
ticker_type_var = tk.StringVar(value="Stock")
ttk.Label(root, text="Select Ticker Type:").pack(pady=5)
ttk.Radiobutton(root, text="Stock", variable=ticker_type_var, value="Stock").pack()
ttk.Radiobutton(root, text="Future", variable=ticker_type_var, value="Future").pack()

# Ticker symbol entry
ttk.Label(root, text="Enter Ticker Symbol:").pack(pady=5)
symbol_entry = ttk.Entry(root)
symbol_entry.pack(pady=5)

# Order action and quantity
action_var = tk.StringVar(value="BUY")
ttk.Label(root, text="Order Action:").pack(pady=5)
ttk.Radiobutton(root, text="Buy", variable=action_var, value="BUY").pack()
ttk.Radiobutton(root, text="Sell", variable=action_var, value="SELL").pack()

ttk.Label(root, text="Quantity:").pack(pady=5)
quantity_entry = ttk.Entry(root)
quantity_entry.pack(pady=5)

# Create labels to display market data
bid_label, ask_label, last_label = ui_components.create_market_data_labels(root)
bid_label.pack(pady=2)
ask_label.pack(pady=2)
last_label.pack(pady=2)

# Button to request market data
def on_request_market_data():
    ticker_type = ticker_type_var.get()
    symbol = symbol_entry.get().upper()
    ui_components.request_market_data(ibkr_client, ticker_type, symbol, bid_label, ask_label, last_label)

search_button = ttk.Button(root, text="Search", command=on_request_market_data)
search_button.pack(pady=10)

# Button to place order
def on_place_order():
    ticker_type = ticker_type_var.get()
    symbol = symbol_entry.get().upper()
    action = action_var.get()
    quantity = int(quantity_entry.get())
    ui_components.confirm_and_place_order(ibkr_client, ticker_type, symbol, action, quantity)

order_button = ttk.Button(root, text="Place Order", command=on_place_order)
order_button.pack(pady=10)

# Start the main Tkinter loop
root.protocol("WM_DELETE_WINDOW", lambda: (ibkr_client.disconnect(), root.destroy()))
root.mainloop()
