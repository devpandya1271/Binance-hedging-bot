# Disclaimer:
# The following illustrative examples are for general information and educational purposes only.
# It is neither investment advice nor a recommendation to trade, invest or take whatsoever actions.
# The below code should only be used in combination with the Binance Futures Testnet and NOT with a Live Trading Account.

"""
Hedging Strategy Implementation
==============================

This script implements a grid-based hedging strategy for cryptocurrency futures trading.
The strategy works by:
1. Opening an initial position (LONG or SHORT)
2. When price moves against the position by a certain percentage, opening an opposite position
3. This creates a hedge that can profit from price reversals
4. Positions are closed when price reaches take-profit levels

Key Features:
- Dual-side position mode (can hold both LONG and SHORT positions simultaneously)
- Percentage-based entry/exit levels
- Automatic position management
- Real-time price monitoring via WebSocket
"""

from binance.client import Client
from binance import ThreadedWebsocketManager
import pandas as pd
from datetime import datetime

class Trader(): 
    """
    Main trading class that implements the hedging strategy.
    
    The strategy parameters are defined as percentages of the current price:
    - long_entry_add: Percentage to add to current price for next LONG entry
    - short_entry_deduct: Percentage to subtract from current price for next SHORT entry
    - long_tp_add: Percentage to add to LONG entry price for take-profit
    - long_sl_deduct: Percentage to subtract from LONG entry price for stop-loss
    - short_tp_deduct: Percentage to subtract from SHORT entry price for take-profit
    - short_sl_add: Percentage to add to SHORT entry price for stop-loss
    """
    def __init__(self, symbol, bar_length, units, leverage = 5, side = "LONG",
                 long_entry_add = 0.4/100, short_entry_deduct = 0.4/100,
                 long_tp_add = 0.8/100, long_sl_deduct = 1.2/100,
                 short_tp_deduct = 0.8/100, short_sl_add = 1.2/100): 
        # Trading parameters
        self.symbol = symbol                    # Trading pair (e.g., "BTCUSDT")
        self.bar_length = bar_length           # Timeframe for price data (e.g., "1m")
        self.base_units = units                # Initial position size
        self.int_units = units                 # Current position size (can change during trading)
        self.leverage = leverage               # Leverage for futures trading
        self.cum_profits = 0                  # Cumulative profits (not currently used)
        self.side = side                       # Initial side: "LONG" or "SHORT"
        
        # Current market price
        self.close = 0.0                       # Latest closing price
        
        # Strategy percentage parameters (as decimals)
        self.long_entry_add = long_entry_add           # 0.4% - distance for next LONG entry
        self.short_entry_deduct = short_entry_deduct   # 0.4% - distance for next SHORT entry
        self.long_tp_add = long_tp_add                 # 0.8% - LONG take-profit distance
        self.long_sl_deduct = long_sl_deduct           # 1.2% - LONG stop-loss distance
        self.short_tp_deduct = short_tp_deduct         # 0.8% - SHORT take-profit distance
        self.short_sl_add = short_sl_add               # 1.2% - SHORT stop-loss distance
        
        # Dynamic price levels (calculated during trading)
        self.long_entry = 0.0                  # Current LONG entry price
        self.short_entry = 0.0                 # Current SHORT entry price
        self.long_tp = 0.0                     # LONG take-profit price
        self.long_sl = 0.0                     # LONG stop-loss price
        self.short_tp = 0.0                    # SHORT take-profit price
        self.short_sl = 0.0                    # SHORT stop-loss price
        
        # Position tracking
        self.last_units = 0                    # Current position size: 0=no position, >0=long, <0=short
        self.last_direction = None             # Last trade direction: "LONG" or "SHORT"

    def first_trade(self):
        """
        Executes the initial trade to start the hedging strategy.
        
        If starting with LONG:
        - Opens a LONG position at market price
        - Sets up price levels for next SHORT entry and LONG take-profit/stop-loss
        
        If starting with SHORT:
        - Opens a SHORT position at market price  
        - Sets up price levels for next LONG entry and SHORT take-profit/stop-loss
        """
        try:
            if self.side == "LONG":
                # Open initial LONG position
                order = client.futures_create_order(
                    symbol = self.symbol, 
                    side = "BUY", 
                    type = "MARKET", 
                    quantity = self.int_units,
                    positionSide = "LONG"
                )
                
                # Get current market price and set up all price levels
                ticker = client.futures_symbol_ticker(symbol=self.symbol)
                self.long_entry = float(ticker['price'])
                
                # Calculate next SHORT entry (0.4% below current price)
                self.short_entry = self.long_entry - self.short_entry_deduct * self.long_entry
                
                # Calculate LONG take-profit and stop-loss levels
                self.long_tp = self.long_entry + self.long_tp_add * self.long_entry      # 0.8% above entry
                self.long_sl = self.long_entry - self.long_sl_deduct * self.long_entry   # 1.2% below entry
                
                # Calculate SHORT take-profit and stop-loss levels
                self.short_tp = self.short_entry - self.short_tp_deduct * self.short_entry # 0.8% below entry
                self.short_sl = self.short_entry + self.short_sl_add * self.short_entry   # 1.2% above entry
                
                # Update position tracking
                self.last_units = self.int_units
                self.last_direction = "LONG"
                
                # Report the trade
                self.report_trade(order, "ENTERING LONG at", self.long_entry)
                print(f"long tp: {self.long_tp:,.2f}", f"long sl: {self.long_sl:,.2f}")
                print(f"next short entry: {self.short_entry:,.2f}")
                
                #self.hedging_loop()
            
            elif self.side == "SHORT":
                # Open initial SHORT position
                order = client.futures_create_order(
                    symbol = self.symbol, 
                    side = "SELL", 
                    type = "MARKET", 
                    quantity = self.int_units,
                    positionSide = "SHORT"
                )
                
                # Get current market price and set up all price levels
                ticker = client.futures_symbol_ticker(symbol=self.symbol)
                self.short_entry = float(ticker['price'])
                
                # Calculate next LONG entry (0.4% above current price)
                self.long_entry = self.short_entry + self.long_entry_add * self.short_entry
                
                # Calculate SHORT take-profit and stop-loss levels
                self.short_tp = self.short_entry - self.short_tp_deduct * self.short_entry # 0.8% below entry
                self.short_sl = self.short_entry + self.short_sl_add * self.short_entry   # 1.2% above entry
                
                # Calculate LONG take-profit and stop-loss levels
                self.long_tp = self.long_entry + self.long_tp_add * self.long_entry      # 0.8% above entry
                self.long_sl = self.long_entry - self.long_sl_deduct * self.long_entry   # 1.2% below entry
                
                # Update position tracking
                self.last_units = self.int_units * -1  # Negative for SHORT position
                self.last_direction = "SHORT"
                
                # Report the trade
                self.report_trade(order, "ENTERING SHORT at", self.short_entry)
                print(f"short tp: {self.short_tp:,.2f}", f"short sl: {self.short_sl:,.2f}")
                print(f"next long entry: {self.long_entry:,.2f}")
                #self.hedging_loop()
        except Exception as e:
            print(f"Error in first_trade: {e}")
            raise

    def hedging_loop(self):
        """
        Main hedging logic that runs on every price update.
        
        The strategy works as follows:
        
        If currently LONG:
        - If price drops to SHORT entry level: Open SHORT position (creates hedge)
        - If price rises to LONG take-profit: Close all positions and restart
        
        If currently SHORT:
        - If price rises to LONG entry level: Open LONG position (creates hedge)
        - If price drops to SHORT take-profit: Close all positions and restart
        
        This creates a grid-like trading pattern that can profit from price reversals.
        """
        try:
            #print('Hedging loop started')
            if self.last_direction == "LONG":
                #print('Last direction is Long')
                if self.last_units > 0:  # Currently have a LONG position
                    #print('Last units is greater than 0')
                    
                    # Check if price has dropped to SHORT entry level
                    if self.close <= (self.short_entry):
                        # Price dropped enough to trigger SHORT entry (hedging)
                        # Open SHORT position with double the size of current LONG position
                        order = client.futures_create_order(
                            symbol = self.symbol, 
                            side = "SELL", 
                            type = "MARKET", 
                            quantity = abs(self.last_units*2),  # Double the position size
                            positionSide = "SHORT"
                        )
                        
                        # Update price levels based on new SHORT entry
                        ticker = client.futures_symbol_ticker(symbol=self.symbol)
                        self.short_entry = float(ticker['price'])
                        self.short_tp = self.short_entry - self.short_tp_deduct * self.short_entry
                        self.short_sl = self.short_entry + self.short_sl_add * self.short_entry
                        
                        # Update position tracking (now have both LONG and SHORT)
                        self.last_units = self.last_units*2 * -1  # Negative for SHORT
                        self.last_direction = "SHORT"
                        
                        self.report_trade(order, "ENTERING SHORT at", self.short_entry)
                        print(f"next long entry: {self.long_entry:,.2f}")
                        #self.hedging_loop()

                    # Check if price has risen to LONG take-profit level
                    elif self.close >= self.long_tp:
                        print('Close is equal to long tp')
                        # Take profit reached - close all positions and restart
                        self.close_all_positions()
                        #self.report_trade(order, "All Positions Closed")
                        self.last_units = 0
                        self.last_direction = None
                        self.side = "LONG"
                        print("All positions closed, Side set to Long, Running first trade")
                        self.first_trade()

            elif self.last_direction == "SHORT":
                #print('Last direction is SHORT')
                if self.last_units < 0:  # Currently have a SHORT position
                    #print('Last units is greater than 0')
                    
                    # Check if price has risen to LONG entry level
                    if self.close >= (self.long_entry):
                        print('Close is equal to short entry + 400')
                        # Price rose enough to trigger LONG entry (hedging)
                        # Open LONG position with double the size of current SHORT position
                        order = client.futures_create_order(
                            symbol = self.symbol, 
                            side = "BUY", 
                            type = "MARKET", 
                            quantity = abs(self.last_units*2),  # Double the position size
                            positionSide = "LONG"
                        )
                        
                        # Update price levels based on new LONG entry
                        ticker = client.futures_symbol_ticker(symbol=self.symbol)
                        self.long_entry = float(ticker['price'])   
                        self.long_tp = self.long_entry + self.long_tp_add * self.long_entry
                        self.long_sl = self.long_entry - self.long_sl_deduct * self.long_entry
                        
                        # Update position tracking (now have both SHORT and LONG)
                        self.last_units = self.last_units*2 * -1  # Positive for LONG
                        self.last_direction = "LONG"
                        
                        self.report_trade(order, "ENTERING LONG at", self.long_entry)
                        print(f"next short entry: {self.short_entry:,.2f}")
                        #self.hedging_loop()

                    # Check if price has dropped to SHORT take-profit level
                    elif self.close <= self.short_tp:
                        print('Close is equal to short tp')
                        # Take profit reached - close all positions and restart
                        self.close_all_positions()
                        print('Closing long position')
                        
                        self.last_units = 0
                        self.last_direction = None
                        self.side = "SHORT"
                        print("All positions closed, Side set to Short, Running first trade")
                        self.first_trade()
        except Exception as e:
            print(f"Error in hedging_loop: {e}")
            # Don't raise here to prevent WebSocket from crashing

    def close_all_positions(self):
        """
        Closes all open positions (both LONG and SHORT) at market price.
        
        This function:
        1. Gets current position information from Binance
        2. Identifies which positions are open (LONG and/or SHORT)
        3. Closes each position with the opposite order type
        """
        try:
            # Get current position info from Binance
            positions = client.futures_position_information(symbol=self.symbol)
            
            for pos in positions:
                type = pos["positionSide"]  # "LONG" or "SHORT"
                amt = float(pos["positionAmt"])  # Position size (positive for LONG, negative for SHORT)

                if amt == 0:
                    continue  # Skip if no open position on this side

                qty = abs(amt)  # Absolute quantity to close

                if type == "LONG" and amt > 0:
                    # Close LONG position with SELL order
                    order = client.futures_create_order(
                        symbol=self.symbol,
                        side="SELL",
                        type="MARKET",
                        quantity=qty,
                        positionSide="LONG"
                    )
                    print(f"Closed LONG position of {qty}")

                elif type == "SHORT" and amt < 0:
                    # Close SHORT position with BUY order
                    order = client.futures_create_order(
                        symbol=self.symbol,
                        side="BUY",
                        type="MARKET",
                        quantity=qty,
                        positionSide="SHORT"
                    )
                    print(f"Closed SHORT position of {qty}")
        except Exception as e:
            print(f"Error in close_all_positions: {e}")
            raise


    def report_trade(self, order, direction, price):
        """
        Prints trade information to console.
        
        Args:
            order: The order object returned by Binance API
            direction: String describing the trade direction
            price: The price at which the trade was executed
        """
        print(f"\n{direction} at ${price:,.2f}")
        print(f"Order ID: {order['orderId']}")
        print(f"Quantity: {order['origQty']}")
        #print(f"Current Market Price: ${price:,.2f}")

    def start_trading(self):
        """
        Initializes the trading session and starts the WebSocket connection.
        
        This function:
        1. Sets the leverage for the trading pair
        2. Enables dual-side position mode (required for hedging)
        3. Executes the first trade
        4. Starts the WebSocket connection for real-time price updates
        """
        # Set leverage for the trading pair
        client.futures_change_leverage(symbol = self.symbol, leverage = self.leverage)
        
        # Check current position mode and enable dual-side position mode if needed
        # Dual-side mode allows holding both LONG and SHORT positions simultaneously
        try:
            position_mode = client.futures_get_position_mode()
            if not position_mode['dualSidePosition']:
                client.futures_change_position_mode(dualSidePosition=True)
        except Exception as e:
            print(f"Error checking/setting position mode: {e}")
        
        # Execute first trade to start the strategy
        self.first_trade()
        
        # Start WebSocket connection for real-time price updates
        self.twm = ThreadedWebsocketManager()
        self.twm.start()
        self.twm.start_kline_futures_socket(callback = self.stream_price,
                                    symbol = self.symbol, interval = self.bar_length)
        self.twm.join()
    
    def stream_price(self, msg):
        """
        WebSocket callback function that processes real-time price updates.
        
        This function is called every time a new price update is received.
        It updates the current price and triggers the hedging logic.
        
        Args:
            msg: WebSocket message containing price data
        """
        try:
            # Extract timestamp and closing price from WebSocket message
            event_time = pd.to_datetime(msg["E"], unit = "ms")  # Event time
            close   = float(msg["k"]["c"])  # Closing price
            self.close = close

            # Optional: Display real-time price updates (commented out)
            #sys.stdout.write(f"\rTime: {event_time} | Price: ${close:,.2f}")
            #sys.stdout.flush()
            
            # print out
            #print("\rTime: {} | Price: ${:,.2f}".format(event_time, close), end='', flush=True)

            # Trigger hedging logic on each price update
            self.hedging_loop()
        except Exception as e:
            print(f"Error in stream_price: {e}")
            # Don't raise here to prevent WebSocket from crashing

if __name__ == "__main__": 
    # Load environment variables
    import os
    from dotenv import load_dotenv
    
    # Load .env file
    load_dotenv()
    
    # Binance API credentials (TESTNET - for testing only)
    api_key = os.getenv("BINANCE_API_KEY")
    secret_key = os.getenv("BINANCE_SECRET_KEY")
    
    # Check if API keys are loaded
    if not api_key or not secret_key:
        print("Error: API keys not found in environment variables.")
        print("Please create a .env file with your Binance API credentials:")
        print("BINANCE_API_KEY=your_api_key_here")
        print("BINANCE_SECRET_KEY=your_secret_key_here")
        exit(1)

    # Initialize Binance client with testnet
    client = Client(api_key=api_key, api_secret=secret_key, testnet=True)
    client.FUTURES_URL = 'https://testnet.binancefuture.com'
    
    # Trading parameters
    symbol = "BTCUSDT"                    # Trading pair
    long_entry_add = 0.4/100             # 0.4% - distance for next LONG entry
    short_entry_deduct = 0.4/100         # 0.4% - distance for next SHORT entry
    long_tp_add = 0.8/100                # 0.8% - LONG take-profit distance
    long_sl_deduct = 1.2/100             # 1.2% - LONG stop-loss distance
    short_tp_deduct = 0.8/100            # 0.8% - SHORT take-profit distance
    short_sl_add = 1.2/100               # 1.2% - SHORT stop-loss distance
    bar_length = "1m"                     # 1-minute candles for price updates
    initial_units = 0.3                   # Initial position size (0.3 BTC)
    leverage = 50                         # 50x leverage
    side = "LONG"                         # Start with LONG position
    

    # Create and start the trading bot
    trader = Trader(symbol = symbol, bar_length = bar_length,
                        units = initial_units, leverage = leverage, side = side,
                        long_entry_add = long_entry_add, short_entry_deduct = short_entry_deduct,
                        long_tp_add = long_tp_add, long_sl_deduct = long_sl_deduct,
                        short_tp_deduct = short_tp_deduct, short_sl_add = short_sl_add)

    trader.start_trading()
