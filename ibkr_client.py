from ib_insync import IB, Stock, Contract, MarketOrder
from tkinter import messagebox
from datetime import date
import pandas as pd
import time
from datetime import datetime



class IBKRClient:
    
    def __init__(self, host='127.0.0.1', port=7497, clientId=1):
        self.ib = IB()
        self.ib.connect(host, port, clientId)
        self.ib.reqMarketDataType(3)

    def _get_next_quarterly_expiration(self, current_date=None, offset=0):
        """
        Calculate the next quarterly expiration month (March, June, Sep, Dec) for ES futures.
        
        Args:
            current_date (datetime, optional): Reference date. Defaults to today.
            offset (int): Number of quarters to skip (0 = next quarter, 1 = quarter after, etc.).
        
        Returns:
            str: YYYYMM format of the expiration month (e.g., '202506').
        """
        if current_date is None:
            current_date = datetime.now()
        
        quarterly_months = [3, 6, 9, 12]
        
        year = current_date.year
        month = current_date.month

        for i in range(len(quarterly_months)):
            if month <= quarterly_months[i]:
                target_month = quarterly_months[i]
                break
        else:
            target_month = quarterly_months[0]
            year += 1
        
        # Skips quarters based on offset
        for _ in range(offset):
            target_month_index = (quarterly_months.index(target_month) + 1) % 4
            target_month = quarterly_months[target_month_index]
            if target_month_index == 0:
                year += 1
        
        return f"{year}{target_month:02d}"
    
    # Retrieve contract
    def get_contract(self, ticker_type, symbol, year_month=None, quarter_offset=0):
        try:
            if ticker_type == "Stock":
                contract = Stock(symbol=symbol, exchange="SMART", currency="USD")
            elif ticker_type == "Future":
                contract = Contract()
                contract.secType = 'FUT'
                contract.symbol = symbol    
                contract.exchange = 'CME'
                contract.currency = 'USD'
                contract.multiplier = ''  
                
                if year_month:
                    contract.lastTradeDateOrContractMonth = year_month
                else:
                    contract.lastTradeDateOrContractMonth = self._get_next_quarterly_expiration(
                        offset=quarter_offset
                    )
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
            sec_type = pos.contract.secType

            if sec_type == "FUT":
                contract = self.get_contract(
                    ticker_type="Future",
                    symbol=pos.contract.symbol
                )
            else:
                contract = self.get_contract(
                    ticker_type="Stock",
                    symbol=pos.contract.symbol
                )

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