import tkinter as tk
from tkinter import ttk
from popup_window import create_popup_window
from ibkr_client import IBKRClient

ibkr = IBKRClient()

def populate_positions_list(frame, ibkr):

    for widget in frame.winfo_children():
        widget.destroy()

    positions = ibkr.get_positions()
    if isinstance(positions, str):
        label = tk.Label(frame, text=positions, font=("Helvetica", 12))
        label.pack()
        return
    headers = ["Contract", "Quantity", "Average Cost", "Current Price", "Actions"]
    for col, header in enumerate(headers):
        label = tk.Label(frame, text=header, font=("Helvetica", 12, "bold"), bg="#f0f0f0")
        label.grid(row=0, column=col, padx=10, pady=5, sticky="ew")

    for i, row in positions.iterrows():
        tk.Label(frame, text=row['contract'], font=("Helvetica", 12)).grid(row=i + 1, column=0, padx=10, pady=5)
        tk.Label(frame, text=row['quantity'], font=("Helvetica", 12)).grid(row=i + 1, column=1, padx=10, pady=5)
        tk.Label(frame, text=f"${row['average_cost']:.2f}", font=("Helvetica", 12)).grid(row=i + 1, column=2, padx=10, pady=5)
        tk.Label(frame, text=f"${row['current_price']:.2f}", font=("Helvetica", 12)).grid(row=i + 1, column=3, padx=10, pady=5)

        ticker = row['contract'].split(' ')[0]
        button = tk.Button(
            frame,
            text="Details",
            font=("Helvetica", 10),
            bg="#0078d4",
            fg="white",
            command=lambda t=ticker: create_popup_window(frame.master, ibkr, "Stock", t)
        )
        button.grid(row=i + 1, column=4, padx=10, pady=5)

# Main application window
root = tk.Tk()
root.title("Ticker Search and Positions")
root.geometry("800x600")
root.configure(bg="#ffffff")

# Styling
style = ttk.Style()
style.theme_use("clam")
style.configure("TFrame", background="#ffffff")
style.configure("TLabel", background="#ffffff", font=("Helvetica", 12))
style.configure("TButton", font=("Helvetica", 12), padding=5)

# Search frame
search_frame = ttk.Frame(root, padding="20")
search_frame.pack(fill="x")

title_label = ttk.Label(search_frame, text="Search Ticker (Stock or Future)", font=("Helvetica", 16, "bold"))
title_label.grid(row=0, column=0, columnspan=2, pady=10)

# Radio buttons for ticker type
ticker_type = tk.StringVar(value="Stock")
stock_radio = ttk.Radiobutton(search_frame, text="Stock", variable=ticker_type, value="Stock")
future_radio = ttk.Radiobutton(search_frame, text="Future", variable=ticker_type, value="Future")
stock_radio.grid(row=1, column=0, sticky="w", pady=5)
future_radio.grid(row=1, column=1, sticky="w", pady=5)

# Ticker input
symbol_label = ttk.Label(search_frame, text="Enter Ticker Symbol:", font=("Helvetica", 12))
symbol_label.grid(row=2, column=0, sticky="w")
symbol_entry = ttk.Entry(search_frame, width=25, font=("Helvetica", 12))
symbol_entry.grid(row=2, column=1, padx=10, sticky="ew")

search_button = ttk.Button(
    search_frame,
    text="Search",
    command=lambda: create_popup_window(root, ibkr, ticker_type.get(), symbol_entry.get())
)
search_button.grid(row=3, column=0, columnspan=2, pady=15)

# Positions frame
positions_frame = ttk.Frame(root, padding="20")
positions_frame.pack(fill="both", expand=True)

populate_positions_list(positions_frame, ibkr)

root.mainloop()

# Disconnect from IBKR on close
ibkr.disconnect()