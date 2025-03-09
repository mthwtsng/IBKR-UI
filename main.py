import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import tkinter as tk
import pandas as pd
from ibkr_client import IBKRClient
from popup_window import create_popup_window

ibkr = IBKRClient()

app = ttk.Window(themename="flatly")
app.title("IBKR Trading Interface")
app.geometry("800x600")
app.resizable(False, False)

# Create a menu bar with a theme toggle option
def toggle_theme():
    current_theme = app.style.theme.name
    new_theme = "darkly" if current_theme == "flatly" else "flatly"
    app.style.theme_use(new_theme)

menubar = tk.Menu(app)
app.config(menu=menubar)
theme_menu = tk.Menu(menubar, tearoff=0)
theme_menu.add_command(label="Toggle Theme", command=toggle_theme)
menubar.add_cascade(label="Theme", menu=theme_menu)


# ** Search Frame **

search_frame = ttk.Frame(app, padding=20)
search_frame.pack(fill='x')

title_label = ttk.Label(search_frame, text="Search Ticker (Stock or Future)", font=("Helvetica", 16, "bold"))
title_label.grid(row=0, column=0, columnspan=2, pady=10)

# Radio buttons for ticker type
ticker_type = tk.StringVar(value="Stock")
stock_radio = ttk.Radiobutton(search_frame, text="Stock", variable=ticker_type, value="Stock")
future_radio = ttk.Radiobutton(search_frame, text="Future", variable=ticker_type, value="Future")
stock_radio.grid(row=1, column=0, sticky=W, pady=5)
future_radio.grid(row=1, column=1, sticky=W, pady=5)

# Ticker input
ttk.Label(search_frame, text="Enter Ticker Symbol:", font=("Helvetica", 12)).grid(row=2, column=0, sticky=W, pady=5)
symbol_entry = ttk.Entry(search_frame, width=25, font=("Helvetica", 12))
symbol_entry.grid(row=2, column=1, padx=10, sticky='ew')

# Search button to open popup
search_button = ttk.Button(
    search_frame,
    text="Search",
    command=lambda: create_popup_window(app, ibkr, ticker_type.get(), symbol_entry.get())
)
search_button.grid(row=3, column=0, columnspan=2, pady=15)


positions_frame = ttk.Frame(app, padding=20)
positions_frame.pack(fill='both', expand=True)

# columns
columns = ("contract", "quantity", "average_cost", "current_price")
tree = ttk.Treeview(positions_frame, columns=columns, show="headings", bootstyle="table")

for col in columns:
    tree.heading(col, text=col.replace("_", " ").title())
    tree.column(col, anchor='center', width=150)
tree.pack(fill='both', expand=True)

def populate_positions():
    for item in tree.get_children():
        tree.delete(item)

    positions = ibkr.get_positions()
    if isinstance(positions, str):
        label = ttk.Label(positions_frame, text=positions, font=("Helvetica", 12))
        label.pack(pady=10)
    else:
        for _, row in positions.iterrows():
            tree.insert("", "end", values=(
                row["contract"],
                row["quantity"],
                f"${row['average_cost']:.2f}",
                f"${row['current_price']:.2f}"
            ))
            
populate_positions()

refresh_btn = ttk.Button(positions_frame, text="Refresh Positions", command=populate_positions)
refresh_btn.pack(pady=10)

app.mainloop()

ibkr.disconnect()
