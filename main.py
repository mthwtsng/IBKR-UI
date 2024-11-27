import tkinter as tk
from tkinter import ttk
from popup_window import create_popup_window
from ibkr_client import IBKRClient

ibkr = IBKRClient()

root = tk.Tk()
root.title("Ticker Search")
root.geometry("960x540")
root.resizable(False, False)

style = ttk.Style()
style.theme_use("clam")

search_frame = ttk.Frame(root, padding="20")
search_frame.pack(fill="both", expand=True)

title_label = ttk.Label(search_frame, text="Search Ticker (Stock or Future)", font=("Helvetica", 16, "bold"))
title_label.grid(row=0, column=0, columnspan=2, pady=10)

# Radio buttons for ticker type
ticker_type = tk.StringVar(value="Stock") 
stock_radio = ttk.Radiobutton(search_frame, text="Stock", variable=ticker_type, value="Stock")
future_radio = ttk.Radiobutton(search_frame, text="Future", variable=ticker_type, value="Future")
stock_radio.grid(row=1, column=0, sticky="w", pady=5)
future_radio.grid(row=1, column=1, sticky="w", pady=5)

# Ticker input
ttk.Label(search_frame, text="Enter Ticker Symbol:", font=("Helvetica", 12)).grid(row=2, column=0, sticky="w")
symbol_entry = ttk.Entry(search_frame, width=25, font=("Helvetica", 12))
symbol_entry.grid(row=2, column=1, padx=10, sticky="ew")


search_button = ttk.Button(
    search_frame,
    text="Search",
    command=lambda: create_popup_window(root, ibkr, ticker_type.get(), symbol_entry.get())
)
search_button.grid(row=3, column=0, columnspan=2, pady=15)

# Run the main loop
root.mainloop()

# Disconnect from IBKR on close
ibkr.disconnect()
