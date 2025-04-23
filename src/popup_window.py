import ttkbootstrap as ttk
from ttkbootstrap.tooltip import ToolTip
from ttkbootstrap.constants import *
import tkinter as tk
from tkinter import messagebox
from lightweight_charts import Chart
from src import request_market_data, confirm_and_place_order
from datetime import datetime
import pandas as pd

def create_popup_window(parent, ibkr_client, ticker_type, symbol):
    """Create a popup window for market data, indicators, and order placement.

    Args:
        parent (tk.Widget): Parent widget (typically the main application window).
        ibkr_client (IBKRClient): Instance of IBKRClient for API interactions.
        ticker_type (str): Type of ticker ('Stock' or 'Future').
        symbol (str): Ticker symbol (e.g., 'AAPL', 'ES').

    Returns:
        ttk.Toplevel: The popup window.
    """
    popup = ttk.Toplevel(parent)
    popup.title(f"Market Data & Orders: {symbol} ({ticker_type})")
    popup.geometry("900x700")
    popup.resizable(False, False)
    
    main_frame = ttk.Frame(popup, padding=20)
    main_frame.grid(row=0, column=0, sticky="nsew")
    main_frame.columnconfigure(0, weight=1)
    main_frame.columnconfigure(1, weight=1)
    popup.rowconfigure(0, weight=1)
    
    contract = ibkr_client.get_contract(ticker_type, symbol)
    if not contract:
        messagebox.showerror("Error", f"Failed to retrieve contract for {symbol}")
        popup.destroy()
        return popup

    right_frame = ttk.Frame(main_frame, padding=10)
    right_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
    right_frame.columnconfigure(0, weight=1)
    

    chart_button_frame = ttk.Labelframe(right_frame, text="Chart", bootstyle="success")
    chart_button_frame.grid(row=0, column=0, sticky="nsew", pady=10)
    
    # Time frame selection
    time_frame_var = tk.StringVar(value="1 D")
    time_frame_frame = ttk.Frame(chart_button_frame)
    time_frame_frame.pack(fill="x", padx=5, pady=5)
    ttk.Label(time_frame_frame, text="Time Frame:", font=("Helvetica", 10)).pack(side="left")
    time_frame_combobox = ttk.Combobox(
        time_frame_frame,
        textvariable=time_frame_var,
        values=["1 D", "5 D", "1 M", "3 M"],
        state="readonly",
        width=10
    )
    time_frame_combobox.pack(side="left", padx=5)
    
    chart = None
    chart_window = None
    
    def calculate_sma(df, period=14):
        """Calculate Simple Moving Average for the given period."""
        return pd.DataFrame({
            'time': df['time'],
            f'SMA {period}': df['close'].rolling(window=period).mean()
        }).dropna()
    
    def show_chart():
        """Open a chart window with historical data and SMA."""
        nonlocal chart, chart_window
        historical_data = ibkr_client.get_historical_data(contract, duration=time_frame_var.get())
        if historical_data is None or historical_data.empty:
            messagebox.showerror("Error", "No historical data available")
            return
        
        chart_data = historical_data[['date', 'open', 'high', 'low', 'close', 'volume']].copy()
        chart_data = chart_data.rename(columns={'date': 'time'})
        chart_data['time'] = chart_data['time'].astype(str)
        
        # Destroy existing chart if present
        if chart:
            chart.exit()
            chart_window = None
        
        # Create new chart
        try:
            chart = Chart(title=f"{symbol} ({time_frame_var.get()})", width=800, height=600)
            chart.layout(background_color='#000008', text_color='#000000', font_size=12, font_family='Helvetica')
            chart.candle_style(up_color='#00ff55', down_color='#ed4807')
            chart.volume_config(up_color='#00ff55', down_color='#ed4807')
            chart.watermark(f'{symbol} {time_frame_var.get()}', color='rgba(0, 0, 0, 0.3)')
            chart.crosshair(mode='normal', vert_color='#000000', horz_color='#000000')
            chart.legend(visible=True)
            
            # Set historical data
            chart.set(chart_data)
            
            # Add SMA indicator
            sma_data = calculate_sma(chart_data, period=14)
            sma_line = chart.create_line('SMA 14')
            sma_line.set(sma_data)
            
            # Show chart in separate window
            chart.show(block=False)
            chart_window = chart
        except Exception as e:
            messagebox.showerror("Chart Error", f"Failed to create chart: {str(e)}\nEnsure WebView2 is installed.")
            chart = None
            chart_window = None
    
    # Button to view chart
    view_chart_btn = ttk.Button(
        chart_button_frame,
        text="View Chart",
        command=show_chart,
        bootstyle="primary"
    )
    view_chart_btn.pack(pady=5)
    ToolTip(view_chart_btn, text="Open chart in a separate window")
    
    # Order Placement
    order_frame = ttk.Labelframe(right_frame, text="Order Placement", bootstyle="danger")
    order_frame.grid(row=1, column=0, sticky="ew", pady=10)
    
    ttk.Label(order_frame, text="Quantity:", font=("Helvetica", 12)).grid(row=0, column=0, padx=5, pady=5, sticky="e")
    qty_entry = ttk.Entry(order_frame, width=10, font=("Helvetica", 12))
    qty_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")
    ToolTip(qty_entry, text="Enter the number of shares or contracts")
    
    action_var = tk.StringVar(value="BUY")
    buy_radio = ttk.Radiobutton(order_frame, text="BUY", variable=action_var, value="BUY")
    sell_radio = ttk.Radiobutton(order_frame, text="SELL", variable=action_var, value="SELL")
    buy_radio.grid(row=0, column=2, padx=5, pady=5)
    sell_radio.grid(row=0, column=3, padx=5, pady=5)
    
    total_label = ttk.Label(order_frame, text="Total: N/A", font=("Helvetica", 12))
    total_label.grid(row=1, column=0, columnspan=4, padx=5, pady=5)
    
    def update_total(event=None):
        """Update the total price based on quantity and last price."""
        try:
            quantity = int(qty_entry.get())
            if quantity <= 0:
                raise ValueError("Quantity must be positive")
            last_text = last_label.cget("text")
            parts = last_text.split()
            if len(parts) < 2 or parts[1] == "N/A":
                total_label.config(text="Total: N/A")
                order_btn.config(state="disabled")
                return
            price = float(parts[1])
            total = quantity * price
            total_label.config(text=f"Total: ${total:.2f}")
            order_btn.config(state="normal")
        except ValueError:
            total_label.config(text="Total: N/A")
            order_btn.config(state="disabled")
    
    qty_entry.bind("<KeyRelease>", update_total)
    
    def place_order():
        """Place an order after showing a confirmation dialog."""
        try:
            quantity = int(qty_entry.get())
            if quantity <= 0:
                raise ValueError("Quantity must be positive")
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid positive integer for quantity.")
            return
        
        total_text = total_label.cget("text")
        if total_text == "Total: N/A":
            messagebox.showerror("Error", "Cannot place order: Market data unavailable.")
            return
        
        total_cost = float(total_text.split("$")[1]) if total_text != "Total: N/A" else None
        
        try:
            trade = confirm_and_place_order(ibkr_client, ticker_type, symbol, action_var.get(), quantity, total_cost)
            if trade:
                status = trade.orderStatus.status if trade.orderStatus else "Unknown"
                messagebox.showinfo("Order Placed", f"Order submitted: {status}")
            else:
                messagebox.showerror("Error", "Failed to place order.")
        except Exception as e:
            messagebox.showerror("Error", f"Order placement failed: {str(e)}")
    
    order_btn = ttk.Button(order_frame, text="Place Order", command=place_order, bootstyle="success", state="disabled")
    order_btn.grid(row=2, column=0, columnspan=4, pady=10)
    
    # ** Left Frame (Market Data & Indicators) **
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
    
    # Add tooltips
    ToolTip(bid_label, text="Current highest bid price")
    ToolTip(ask_label, text="Current lowest ask price")
    ToolTip(last_label, text="Most recent trade price")
    
    # Real-time market data streaming
    ticker = ibkr_client.ib.reqMktData(contract, genericTickList='', snapshot=False)
    
    def update_market_data(ticker):
        """Update market data labels and chart with streaming ticker data."""
        bid = ticker.bid if ticker.bid is not None else "N/A"
        ask = ticker.ask if ticker.ask is not None else "N/A"
        last = ticker.last if ticker.last is not None else "N/A"
        bid_label.config(text=f"Bid: {bid:.2f}" if isinstance(bid, float) else f"Bid: {bid}")
        ask_label.config(text=f"Ask: {ask:.2f}" if isinstance(ask, float) else f"Ask: {ask}")
        last_label.config(text=f"Last: {last:.2f}" if isinstance(last, float) else f"Last: {last}")
        update_total()
        
        # Update chart with tick data (1D time frame only)
        if chart and time_frame_var.get() == "1 D" and isinstance(last, float):
            tick_data = pd.Series({
                'time': datetime.now().isoformat(),
                'price': last
            })
            chart.update_from_tick(tick_data)
    
    ticker.updateEvent += update_market_data
    update_market_data(ticker)  # Initial update
    
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
    
    # Add tooltips
    ToolTip(sma_label, text="Simple Moving Average (14-period)")
    ToolTip(ema_label, text="Exponential Moving Average (14-period)")
    ToolTip(vwap_label, text="Volume Weighted Average Price")
    ToolTip(rsi_label, text="Relative Strength Index (14-period)")
    
    def update_indicators():
        """Update technical indicators based on historical data."""
        historical_data = ibkr_client.get_historical_data(contract)
        if historical_data is not None:
            indicators = ibkr_client.calculate_indicators(historical_data)
            sma_label.config(text=f"SMA: {indicators.get('SMA', 'N/A'):.2f}")
            ema_label.config(text=f"EMA: {indicators.get('EMA', 'N/A'):.2f}")
            vwap_label.config(text=f"VWAP: {indicators.get('VWAP', 'N/A'):.2f}")
            rsi_label.config(text=f"RSI: {indicators.get('RSI', 'N/A'):.2f}")
        else:
            messagebox.showerror("Error", "Failed to retrieve historical data")
    
    refresh_indicators_btn = ttk.Button(
        indicators_frame,
        text="Refresh Indicators",
        command=update_indicators,
        bootstyle="primary"
    )
    refresh_indicators_btn.grid(row=0, column=1, rowspan=2, padx=10, pady=5)
    update_indicators()  # Initial update
    
    # Position Summary
    position_frame = ttk.Labelframe(left_frame, text="Position Summary", bootstyle="secondary")
    position_frame.grid(row=2, column=0, sticky="ew", pady=10)
    
    position_label = ttk.Label(position_frame, text="No position held", font=("Helvetica", 12))
    position_label.grid(row=0, column=0, sticky="w", padx=5, pady=5)
    
    def update_position():
        """Update position summary for the ticker."""
        positions = ibkr_client.get_positions()
        if isinstance(positions, str):
            position_label.config(text="No positions held")
            return
        for _, row in positions.iterrows():
            if row["contract"].startswith(f"{symbol} "):
                position_label.config(text=f"Quantity: {row['quantity']}, Avg Cost: ${row['average_cost']:.2f}")
                return
        position_label.config(text="No position held")
    
    ttk.Button(
        position_frame,
        text="Refresh Position",
        command=update_position,
        bootstyle="primary"
    ).grid(row=0, column=1, padx=10, pady=5)
    update_position()  # Initial update
    
    # Clean up on close
    def on_close():
        ibkr_client.ib.cancelMktData(contract)
        if chart:
            chart.exit()
        popup.destroy()
    
    popup.protocol("WM_DELETE_WINDOW", on_close)
    
    # Auto-refresh indicators and position
    def auto_refresh():
        update_indicators()
        update_position()
        popup.after(30000, auto_refresh)
    
    auto_refresh()
    
    # Close button
    close_btn = ttk.Button(main_frame, text="Close", command=on_close, bootstyle="danger")
    close_btn.grid(row=1, column=0, columnspan=2, pady=10)
    
    return popup