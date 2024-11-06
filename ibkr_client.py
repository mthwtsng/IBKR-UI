# ibkr_client.py

from ib_insync import IB, Stock, Contract, MarketOrder
from tkinter import messagebox

class IBKRClient:
    def __init__(self, host='127.0.0.1', port=7497, clientId=1):
        self.ib = IB()
        self.ib.connect(host, port, clientId)
        self.ib.reqMarketDataType(3)

    def get_contract(self, ticker_type, symbol):
        if ticker_type == "Stock":
            contract = Stock(symbol=symbol, exchange="SMART", currency="USD")
        elif ticker_type == "Future":
            contract = Contract()
            contract.secType = 'FUT'
            contract.symbol = symbol
            contract.exchange = 'CME'
            contract.currency = 'USD'
            contract.lastTradeDateOrContractMonth = "202412"
        else:
            return None

        # Qualify the contract to ensure it exists
        if not self.ib.qualifyContracts(contract):
            messagebox.showerror("Contract Error", f"Failed to qualify contract for {symbol}.")
            return None
        return contract

    def get_market_data(self, contract):
        ticker = self.ib.reqMktData(contract, genericTickList='')
        self.ib.sleep(1)
        return {
            "bid": ticker.bid or "N/A",
            "ask": ticker.ask or "N/A",
            "last": ticker.last or "N/A"
        }

    def place_order(self, contract, action, quantity):
        order = MarketOrder(action, quantity)
        trade = self.ib.placeOrder(contract, order)
        return trade

    def disconnect(self):
        self.ib.disconnect()
