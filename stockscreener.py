import tkinter as tk
from tkinter import ttk, messagebox
from ib_insync import IB, Stock, Contract, MarketOrder

# Initialize the IB connection
ib = IB()
ib.connect('127.0.0.1', 7497, clientId=1)
ib.reqMarketDataType(3)

# Function to request market data based on user input
def request_market_data():
    ticker_type = ticker_type_var.get()
    symbol = symbol_entry.get().upper()

    if not symbol:
        messagebox.showerror("Input Error", "Please enter a ticker symbol.")
        return

    # Define contract based on ticker type
    if ticker_type == "Stock":
        contract = Stock(symbol=symbol, exchange="SMART", currency="USD")
    elif ticker_type == "Future":
        # For futures, create the contract in the format you provided
        contract = Contract()
        contract.secType = 'FUT'
        contract.symbol = symbol  # Symbol like 'ES' or 'MNQ'
        contract.exchange = 'CME'
        contract.currency = 'USD'
        contract.lastTradeDateOrContractMonth = "202412"
    else:
        messagebox.showerror("Selection Error", "Please select a valid ticker type.")
        return

    # Qualify the contract
    if not ib.qualifyContracts(contract):
        messagebox.showerror("Contract Error", "Failed to qualify contract.")
        return
    
    # Request real-time market data
    ticker = ib.reqMktData(contract, genericTickList='')
    ib.sleep(1)  # Allow time for data to update

    # Update the labels with the requested data
    bid_label['text'] = f"Bid: {ticker.bid or 'N/A'}"
    ask_label['text'] = f"Ask: {ticker.ask or 'N/A'}"
    last_label['text'] = f"Last: {ticker.last or 'N/A'}"

    # Schedule next update in 1 second to keep data live
    root.after(5000, request_market_data)

# Function to place a market order
def place_order():
    action = action_var.get()  # Buy or Sell
    quantity = int(quantity_entry.get())
    
    # Define contract based on ticker type and symbol
    symbol = symbol_entry.get().upper()
    ticker_type = ticker_type_var.get()
    
    if ticker_type == "Stock":
        contract = Stock(symbol=symbol, exchange="SMART", currency="USD")
    elif ticker_type == "Future":
        contract = Contract()
        contract.secType = 'FUT'
        contract.symbol = symbol
        contract.exchange = 'CME'
        contract.currency = 'USD'
        contract.lastTradeDateOrContractMonth = "202412"

    # Qualify the contract and place the order
    if not ib.qualifyContracts(contract):
        messagebox.showerror("Contract Error", "Failed to qualify contract.")
        return

    order = MarketOrder(action, quantity)
    trade = ib.placeOrder(contract, order)
    messagebox.showinfo("Order Placed", f"{action} order for {quantity} contracts of {symbol} placed.")

# Setup the GUI
root = tk.Tk()
root.title("IBKR Market Data")
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
ttk.Label(root, text="Order Action:").pack(pady=5)
action_var = tk.StringVar(value="BUY")
ttk.Radiobutton(root, text="Buy", variable=action_var, value="BUY").pack()
ttk.Radiobutton(root, text="Sell", variable=action_var, value="SELL").pack()

ttk.Label(root, text="Quantity:").pack(pady=5)
quantity_entry = ttk.Entry(root)
quantity_entry.pack(pady=5)

# Search and Order buttons
search_button = ttk.Button(root, text="Search", command=request_market_data)
search_button.pack(pady=10)

order_button = ttk.Button(root, text="Place Order", command=place_order)
order_button.pack(pady=10)

# Labels for displaying live data
bid_label = ttk.Label(root, text="Bid: N/A")
bid_label.pack(pady=2)
ask_label = ttk.Label(root, text="Ask: N/A")
ask_label.pack(pady=2)
last_label = ttk.Label(root, text="Last: N/A")
last_label.pack(pady=2)

# Start the GUI event loop
root.mainloop()

# Disconnect from IBKR when GUI is closed
ib.disconnect()
