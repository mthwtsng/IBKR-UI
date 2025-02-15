# ibkr_client.py
from ib_insync import IB, Stock, Contract, MarketOrder
from tkinter import messagebox
import pandas as pd

class IBKRClient:
    def __init__(self, host='127.0.0.1', port=7497, clientId=1):
        self.ib = IB()
        self.ib.connect(host, port, clientId)
        self.ib.reqMarketDataType(3)

    # Retrieve contract
    def get_contract(self, ticker_type, symbol):
        if ticker_type == "Stock":
            contract = Stock(symbol=symbol, exchange="SMART", currency="USD")
        elif ticker_type == "Future":
            contract = Contract()
            contract.secType = 'FUT'
            contract.symbol = symbol
            contract.exchange = 'CME'
            contract.currency = 'USD'
            contract.lastTradeDateOrContractMonth = "202501"
        else:
            return None
        if not self.ib.qualifyContracts(contract):
            messagebox.showerror("Contract Error", f"Failed to qualify contract for {symbol}.")
            return None
        return contract

    # Retrieves stock price data
    def get_market_data(self, contract):
        ticker = self.ib.reqMktData(contract, genericTickList='')
        self.ib.sleep(1)
        return {
            "bid": ticker.bid or "N/A",
            "ask": ticker.ask or "N/A",
            "last": ticker.last or "N/A"
        }

    # Sends order placing request
    def place_order(self, contract, action, quantity):
        if not self.ib.qualifyContracts(contract):
            messagebox.showerror("Contract Error", "Failed to qualify contract.")
            return
        order = MarketOrder(action, quantity)
        trade = self.ib.placeOrder(contract, order)
        return trade

    def disconnect(self):
        self.ib.disconnect()
    
    # Retrieves historical data of a stock
    def get_historical_data(self, contract, duration="1 D", barSize="1 min"):
        try:
            bars = self.ib.reqHistoricalData(
                contract,
                endDateTime='',
                durationStr=duration,
                barSizeSetting=barSize,
                whatToShow='MIDPOINT',
                useRTH=True
            )
            self.ib.sleep(1)
            df = pd.DataFrame(bars)
            if not df.empty:
                df['date'] = pd.to_datetime(df['date'])
                if 'close' not in df.columns or 'volume' not in df.columns:
                    messagebox.showerror("Error", "Historical data is missing required columns.")
                    return None
                return df
            return None
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            return None

    def get_positions(self):
        positions = self.ib.positions()
        if not positions:
            return "No positions currently held."
        
        positions_summary = []
        for pos in positions:
            contract = self.get_contract(ticker_type="Stock", symbol=pos.contract.symbol)
            if contract is None:
                continue
            market_data = self.get_market_data(contract)

            positions_summary.append({
                "contract": f"{pos.contract.localSymbol} ({pos.contract.secType})",
                "quantity": pos.position,
                "average_cost": pos.avgCost,
                "current_price": market_data["last"]  
            })

        return pd.DataFrame(positions_summary)




    def calculate_indicators(self, df):
        if df is None or df.empty or 'close' not in df.columns or 'volume' not in df.columns:
            return {}

        # Simple Moving Average (SMA)
        df['SMA'] = df['close'].rolling(window=14, min_periods=1).mean()

        # Exponential Moving Average (EMA)
        df['EMA'] = df['close'].ewm(span=14, adjust=False).mean()

        # VWAP Calculation
        df['VWAP'] = (df['close'] * df['volume']).cumsum() / df['volume'].cumsum()

        # RSI Calculation
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14, min_periods=1).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14, min_periods=1).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))

        return df.iloc[-1][['SMA', 'EMA', 'VWAP', 'RSI']].to_dict()