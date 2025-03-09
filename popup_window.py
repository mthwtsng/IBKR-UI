import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from ui_components import request_market_data, confirm_and_place_order  # Ensure these work with IBKRClient

def create_popup_window(parent, ibkr_client, ticker_type, symbol):
    popup = ttk.Toplevel(parent)
    popup.title(f"Market Data & Orders: {symbol} ({ticker_type})")
    popup.geometry("900x700")
    popup.resizable(False, False)
    
    main_frame = ttk.Frame(popup, padding=20)
    main_frame.grid(row=0, column=0, sticky="nsew")
    main_frame.columnconfigure(0, weight=1)
    main_frame.columnconfigure(1, weight=1)
    
    # ** Market Data & Indicators **
    left_frame = ttk.Frame(main_frame, padding=10)
    left_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
    left_frame.columnconfigure(0, weight=1)
    
    # Market Data Section
    market_frame = ttk.Labelframe(left_frame, text="Market Data", bootstyle="info")
    market_frame.grid(row=0, column=0, sticky="ew", pady=10)
    
    bid_label = ttk.Label(market_frame, text="Bid: N/A", font=("Helvetica", 12))
    ask_label = ttk.Label(market_frame, text="Ask: N/A", font=("Helvetica", 12))
    last_label = ttk.Label(market_frame, text="Last: N/A", font=("Helvetica", 12))
    bid_label.grid(row=0, column=0, sticky="w", padx=5, pady=5)
    ask_label.grid(row=1, column=0, sticky="w", padx=5, pady=5)
    last_label.grid(row=2, column=0, sticky="w", padx=5, pady=5)
    
    def refresh_market_data():
        request_market_data(ibkr_client, ticker_type, symbol, bid_label, ask_label, last_label)
        update_total() 
    
    refresh_data_btn = ttk.Button(
        market_frame, 
        text="Refresh Data", 
        command=refresh_market_data,
        bootstyle="primary"
    )
    refresh_data_btn.grid(row=0, column=1, rowspan=2, padx=10, pady=5)
    
    # Technical Indicators 
    indicators_frame = ttk.Labelframe(left_frame, text="Technical Indicators", bootstyle="warning")
    indicators_frame.grid(row=1, column=0, sticky="ew", pady=10)
    
    sma_label = ttk.Label(indicators_frame, text="SMA: N/A", font=("Helvetica", 12))
    ema_label = ttk.Label(indicators_frame, text="EMA: N/A", font=("Helvetica", 12))
    vwap_label = ttk.Label(indicators_frame, text="VWAP: N/A", font=("Helvetica", 12))
    rsi_label = ttk.Label(indicators_frame, text="RSI: N/A", font=("Helvetica", 12))
    sma_label.grid(row=0, column=0, sticky="w", padx=5, pady=5)
    ema_label.grid(row=1, column=0, sticky="w", padx=5, pady=5)
    vwap_label.grid(row=2, column=0, sticky="w", padx=5, pady=5)
    rsi_label.grid(row=3, column=0, sticky="w", padx=5, pady=5)
    
    def update_indicators():
        contract = ibkr_client.get_contract(ticker_type, symbol)
        if contract:
            historical_data = ibkr_client.get_historical_data(contract)
            if historical_data is not None:
                indicators = ibkr_client.calculate_indicators(historical_data)
                if indicators:
                    sma_label.config(text=f"SMA: {indicators.get('SMA', 'N/A'):.2f}")
                    ema_label.config(text=f"EMA: {indicators.get('EMA', 'N/A'):.2f}")
                    vwap_label.config(text=f"VWAP: {indicators.get('VWAP', 'N/A'):.2f}")
                    rsi_label.config(text=f"RSI: {indicators.get('RSI', 'N/A'):.2f}")
    
    refresh_indicators_btn = ttk.Button(
        indicators_frame, 
        text="Refresh Indicators", 
        command=update_indicators, 
        bootstyle="primary"
    )
    refresh_indicators_btn.grid(row=0, column=1, rowspan=2, padx=10, pady=5)
    update_indicators()  
    
    # ** Chart and order placement **
    right_frame = ttk.Frame(main_frame, padding=10)
    right_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
    right_frame.columnconfigure(0, weight=1)
    
    # Chart
    chart_frame = ttk.Labelframe(right_frame, text="Historical Data Chart", bootstyle="success")
    chart_frame.grid(row=0, column=0, sticky="nsew", pady=10)
    
    try:
        contract = ibkr_client.get_contract(ticker_type, symbol)
        if contract:
            historical_data = ibkr_client.get_historical_data(contract)
    except Exception as e:
        historical_data = None
        
    if historical_data is not None and not historical_data.empty:
        fig, ax = plt.subplots(figsize=(5, 3), dpi=100)
        ax.plot(historical_data['date'], historical_data['close'], label="Close Price", color="blue")
        ax.set_xlabel("Time")
        ax.set_ylabel("Price")
        ax.legend()
        fig.autofmt_xdate()
        
        canvas = FigureCanvasTkAgg(fig, master=chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
    else:
        ttk.Label(chart_frame, text="No historical data available", font=("Helvetica", 12)).pack(padx=5, pady=5)
    
    # Order placement
    order_frame = ttk.Labelframe(right_frame, text="Order Placement", bootstyle="danger")
    order_frame.grid(row=1, column=0, sticky="ew", pady=10)
    
    ttk.Label(order_frame, text="Quantity:", font=("Helvetica", 12)).grid(row=0, column=0, padx=5, pady=5, sticky="e")
    qty_entry = ttk.Entry(order_frame, width=10, font=("Helvetica", 12))
    qty_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")
    
    action_var = tk.StringVar(value="BUY")
    buy_radio = ttk.Radiobutton(order_frame, text="BUY", variable=action_var, value="BUY")
    sell_radio = ttk.Radiobutton(order_frame, text="SELL", variable=action_var, value="SELL")
    buy_radio.grid(row=0, column=2, padx=5, pady=5)
    sell_radio.grid(row=0, column=3, padx=5, pady=5)
    
    # Total price 
    total_label = ttk.Label(order_frame, text="Total: N/A", font=("Helvetica", 12))
    total_label.grid(row=1, column=0, columnspan=4, padx=5, pady=5)
    
    # Updates total price of order
    def update_total(event=None):
        try:
            quantity = int(qty_entry.get())
        except ValueError:
            total_label.config(text="Total: N/A")
            return
        last_text = last_label.cget("text")
        parts = last_text.split()
        if len(parts) < 2 or parts[1] == "N/A":
            total_label.config(text="Total: N/A")
            return
        try:
            price = float(parts[1])
        except ValueError:
            total_label.config(text="Total: N/A")
            return
        total = quantity * price
        total_label.config(text=f"Total: ${total:.2f}")
    
    qty_entry.bind("<KeyRelease>", update_total)
    
    def place_order():
        try:
            quantity = int(qty_entry.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid integer for quantity.")
            return
        confirm_and_place_order(ibkr_client, ticker_type, symbol, action_var.get(), quantity)
    
    order_btn = ttk.Button(order_frame, text="Place Order", command=place_order, bootstyle="success")
    order_btn.grid(row=2, column=0, columnspan=4, pady=10)
    
    # Auto refresh
    def auto_refresh():
        refresh_market_data()
        update_indicators()
        popup.after(10000, auto_refresh)
    
    auto_refresh()
    
    # Close button
    close_btn = ttk.Button(main_frame, text="Close", command=popup.destroy, bootstyle="danger")
    close_btn.grid(row=1, column=0, columnspan=2, pady=10)
    
    return popup
