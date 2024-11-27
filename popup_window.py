import tkinter as tk
from tkinter import ttk
from ui_components import request_market_data

def create_popup_window(parent, ibkr_client, ticker_type, symbol):
    # Create new pop up window for stock information
    data_popup = tk.Toplevel(parent)
    data_popup.title(f"Market Data and Indicators for {symbol} ({ticker_type})")
    data_popup.geometry("500x400")
    data_popup.resizable(False, False)

    content_frame = ttk.Frame(data_popup, padding="20")
    content_frame.pack(fill="both", expand=True)

    # Title Label
    title_label = ttk.Label(content_frame, text=f"Market Data for {symbol} ({ticker_type})", font=("Helvetica", 14, "bold"))
    title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))

    #  Price labels
    bid_label = ttk.Label(content_frame, text="Bid: N/A", font=("Helvetica", 12))
    ask_label = ttk.Label(content_frame, text="Ask: N/A", font=("Helvetica", 12))
    last_label = ttk.Label(content_frame, text="Last: N/A", font=("Helvetica", 12))
    bid_label.grid(row=1, column=0, sticky="w", padx=10, pady=5)
    ask_label.grid(row=2, column=0, sticky="w", padx=10, pady=5)
    last_label.grid(row=3, column=0, sticky="w", padx=10, pady=5)

    # Indicator labels
    ttk.Separator(content_frame, orient="horizontal").grid(row=4, column=0, columnspan=2, pady=10, sticky="ew")
    indicators_label = ttk.Label(content_frame, text="Technical Indicators", font=("Helvetica", 14, "bold"))
    indicators_label.grid(row=5, column=0, columnspan=2, pady=(0, 10))

    sma_label = ttk.Label(content_frame, text="SMA: N/A", font=("Helvetica", 12))
    ema_label = ttk.Label(content_frame, text="EMA: N/A", font=("Helvetica", 12))
    vwap_label = ttk.Label(content_frame, text="VWAP: N/A", font=("Helvetica", 12))
    rsi_label = ttk.Label(content_frame, text="RSI: N/A", font=("Helvetica", 12))
    sma_label.grid(row=6, column=0, sticky="w", padx=10, pady=5)
    ema_label.grid(row=7, column=0, sticky="w", padx=10, pady=5)
    vwap_label.grid(row=8, column=0, sticky="w", padx=10, pady=5)
    rsi_label.grid(row=9, column=0, sticky="w", padx=10, pady=5)

    # Fetch and update market data
    request_market_data(ibkr_client, ticker_type, symbol, bid_label, ask_label, last_label)

    # Close button
    close_button = ttk.Button(content_frame, text="Close", command=data_popup.destroy)
    close_button.grid(row=10, column=0, columnspan=2, pady=20)
