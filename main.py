# main.py

import tkinter as tk
from tkinter import ttk
from ibkr_client import IBKRClient  # Ensure this import is correct
import ui_components

ibkr = IBKRClient()

root = tk.Tk()
root.title("IBKR Market Data & Order Placement")
root.geometry("600x600")

style = ttk.Style()
style.configure("TLabel", font=("Helvetica", 12))
style.configure("TButton", font=("Helvetica", 10))
style.configure("Header.TLabel", font=("Helvetica", 14, "bold"))

main_frame = ttk.Frame(root, padding="10")
main_frame.pack(fill="both", expand=True)

# Header
header_label = ttk.Label(main_frame, text="IBKR Market Data & Order Placement", style="Header.TLabel")
header_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))

# Ticker Type 
ticker_type_frame = ttk.LabelFrame(main_frame, text="Select Ticker Type", padding="10")
ticker_type_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(5, 10))

ticker_type_var = tk.StringVar(value="Stock")
ttk.Radiobutton(ticker_type_frame, text="Stock", variable=ticker_type_var, value="Stock").grid(row=0, column=0, padx=10)
ttk.Radiobutton(ticker_type_frame, text="Future", variable=ticker_type_var, value="Future").grid(row=0, column=1, padx=10)

# Ticker Symbol Input
symbol_frame = ttk.Frame(main_frame, padding="10")
symbol_frame.grid(row=2, column=0, columnspan=2, sticky="ew")

ttk.Label(symbol_frame, text="Enter Ticker Symbol:").grid(row=0, column=0, sticky="w")
symbol_entry = ttk.Entry(symbol_frame, width=20)
symbol_entry.grid(row=0, column=1, padx=(10, 0), sticky="ew")

# Data Section
market_data_frame = ttk.LabelFrame(main_frame, text="Market Data", padding="10")
market_data_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(5, 10))

bid_label = ttk.Label(market_data_frame, text="Bid: N/A", style="TLabel")
bid_label.grid(row=0, column=0, sticky="w")
ask_label = ttk.Label(market_data_frame, text="Ask: N/A", style="TLabel")
ask_label.grid(row=0, column=1, sticky="w")
last_label = ttk.Label(market_data_frame, text="Last: N/A", style="TLabel")
last_label.grid(row=1, column=0, sticky="w", pady=(5, 0))

# Order Section
order_frame = ttk.LabelFrame(main_frame, text="Place Order", padding="10")
order_frame.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(5, 10))

ttk.Label(order_frame, text="Order Action:").grid(row=0, column=0, sticky="w")
action_var = tk.StringVar(value="BUY")
ttk.Radiobutton(order_frame, text="Buy", variable=action_var, value="BUY").grid(row=0, column=1, padx=5)
ttk.Radiobutton(order_frame, text="Sell", variable=action_var, value="SELL").grid(row=0, column=2, padx=5)

ttk.Label(order_frame, text="Quantity:").grid(row=1, column=0, sticky="w", pady=(10, 0))
quantity_entry = ttk.Entry(order_frame, width=10)
quantity_entry.grid(row=1, column=1, columnspan=2, sticky="w", pady=(10, 0))

# Buttons
button_frame = ttk.Frame(main_frame)
button_frame.grid(row=5, column=0, columnspan=2, pady=(10, 0))

search_button = ttk.Button(button_frame, text="Search", command=lambda: ui_components.request_market_data(ibkr, ticker_type_var.get(), symbol_entry.get(), bid_label, ask_label, last_label))
search_button.grid(row=0, column=0, padx=10)

order_button = ttk.Button(button_frame, text="Place Order", command=lambda: ui_components.confirm_and_place_order(ibkr, action_var.get(), symbol_entry.get(), ticker_type_var.get(), quantity_entry.get()))
order_button.grid(row=0, column=1, padx=10)

# Status Bar
status_label = ttk.Label(root, text="Status: Connected to IBKR", relief="sunken", anchor="w", padding="5")
status_label.pack(fill="x", side="bottom")

# Run the main loop
root.mainloop()

# Disconnect from IBKR on close
ibkr.disconnect()