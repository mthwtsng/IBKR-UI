# Trading Dashboard

A Python-based trading application for interacting with Interactive Brokers (IBKR) to view real-time market data, technical indicators, position summaries, and place orders for stocks and futures. The application features a modern GUI built with `ttkbootstrap` and interactive candlestick charts powered by `lightweight-charts-python`.

## Features

- **Real-Time Market Data**: Stream bid, ask, and last prices for selected tickers (stocks or futures).
- **Technical Indicators**: Display Simple Moving Average (SMA), Exponential Moving Average (EMA), Volume Weighted Average Price (VWAP), and Relative Strength Index (RSI).
- **Position Summary**: View current positions with quantity and average cost.
- **Order Placement**: Place buy/sell market orders with quantity input and total cost confirmation.
- **Interactive Charts**: View candlestick charts with volume and a 14-period SMA in a separate window, supporting 1-day, 5-day, 1-month, and 3-month time frames.
- **Responsive GUI**: Modern interface with tooltips and error handling, built using `ttkbootstrap`.


## Installation

### Prerequisites
- Python 3.8 or higher
- Interactive Brokers TWS or IB Gateway (for API access)

### Steps
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/trading-dashboard.git
   cd trading-dashboard
   ```

2. **Set Up a Virtual Environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install lightweight-charts pandas numpy ttkbootstrap>=1.10 ib_insync
   ```

4. **Configure Interactive Brokers**:
   - Install TWS or IB Gateway from [Interactive Brokers](https://www.interactivebrokers.com).
   - Enable API access in TWS/Gateway settings (default port: 7497 for paper trading).
   - Ensure your IBKR account is set up and funded (or use a paper trading account).


## Usage

1. **Start TWS or IB Gateway**:
   - Launch TWS/Gateway and log in with your IBKR credentials.
   - Ensure API access is enabled.

2. **Run the Application**:
   ```bash
   python main.py
   ```

3. **Interact with the GUI**:
   - **Main Window**: Enter a ticker symbol (e.g., “AAPL” for stocks, “ES” for futures) and select the ticker type.
   - **Popup Window**:
     - View real-time bid, ask, and last prices.
     - Check technical indicators (SMA, EMA, VWAP, RSI) and refresh as needed.
     - See position details for the selected ticker.
     - Place buy/sell orders by specifying quantity and confirming the total cost.
     - Select a time frame (1D, 5D, 1M, 3M) and click “View Chart” to open a candlestick chart with SMA.

4. **Close the Application**:
   - Click “Close” in the popup or main window to stop market data streaming and close chart windows.

## Dependencies

- `lightweight-charts>=0.3.0`: Interactive candlestick charts.
- `pandas`: Data manipulation for chart data and indicators.
- `ttkbootstrap>=1.10`: Modern `tkinter` styling for GUI.
- `ib_insync`: Interactive Brokers API integration.

Install with:
```bash
pip install lightweight-charts pandas numpy ttkbootstrap>=1.10 ib_insync
```



## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

**Disclaimer**: This application is for educational purposes only. Trading involves financial risk. Ensure you understand the risks and consult a financial advisor before trading.