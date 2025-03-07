from ib_insync import IB, Stock, Contract, MarketOrder
from tkinter import messagebox
import pandas as pd
import time

class IBKRClient:
    def __init__(self, host='127.0.0.1', port=7497, clientId=1):
        self.ib = IB()
        self.ib.connect(host, port, clientId)
        self.ib.reqMarketDataType(3)

    # Retrieve contract
    def get_contract(self, ticker_type, symbol):
        try:
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
                raise ValueError("Invalid ticker type")

            if not self.ib.qualifyContracts(contract):
                raise Exception(f"Failed to qualify contract for {symbol}")

            return contract
        except Exception as e:
            messagebox.showerror("Contract Error", f"An error occurred: {str(e)}")
            return None

    # Retrieves stock price data
    def get_market_data(self, contract, retries=3, delay=1):
        for attempt in range(retries):
            try:
                ticker = self.ib.reqMktData(contract, genericTickList='')
                self.ib.sleep(1)
                if not ticker.bid or not ticker.ask or not ticker.last:
                    raise ValueError("Incomplete market data")
                return {
                    "bid": ticker.bid,
                    "ask": ticker.ask,
                    "last": ticker.last
                }
            except Exception as e:
                if attempt == retries - 1:
                    messagebox.showerror("Market Data Error", f"Failed to fetch market data: {str(e)}")
                    return None
                time.sleep(delay * (2 ** attempt))

    # Sends order placing request
    def place_order(self, contract, action, quantity):
        try:
            if not isinstance(quantity, int) or quantity <= 0:
                raise ValueError("Invalid quantity")
            if action not in ["BUY", "SELL"]:
                raise ValueError("Invalid action")

            order = MarketOrder(action, quantity)
            trade = self.ib.placeOrder(contract, order)
            return trade
        except Exception as e:
            messagebox.showerror("Order Error", f"Failed to place order: {str(e)}")
            return None
    
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
            if df.empty or 'close' not in df.columns or 'volume' not in df.columns:
                raise ValueError("Historical data is incomplete or invalid")
            return df
        except Exception as e:
            messagebox.showerror("Historical Data Error", f"An error occurred: {str(e)}")
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