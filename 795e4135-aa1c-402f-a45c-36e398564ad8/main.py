from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import SMA
from surmount.logging import log

class TradingStrategy(Strategy):
    @property
    def assets(self):
        # Define which assets this strategy will handle
        return ["SPY"]

    @property
    def interval(self):
        # Define the time interval for data collection
        return "1day"
    
    def run(self, data):
        # Get the historical closing prices for SPY
        log(str(data["ohlcv"][0]))
        spy_prices = [i["SPY"]["close"] for i in data["ohlcv"]]
        log(str(len(spy_prices)))
        # Check if there are at least 14 days of data to compute SMA
        if len(spy_prices) >= 14:
            # Calculate the 14-day simple moving average for SPY
            spy_sma_14 = SMA("SPY", data["ohlcv"], 14)[-1]
            
            # Get the most recent closing price for SPY
            current_price = spy_prices[-1]
            
            # Calculate the 5% tolerance thresholds
            upper_bound = spy_sma_14 * 1.01
            lower_bound = spy_sma_14 * 0.99
            log("lower {0}, upper {1}, current {2}".format(lower_bound, upper_bound, current_price))
            # Determine the allocation based on the current price and SMA
            if current_price >= upper_bound:
                # If the current price is at least 5% higher than the SMA, go 100% long on SPY
                allocation = {"SPY": 1.0}
            elif current_price <= lower_bound:
                # If the current price is at least 5% lower than the SMA, short SPY (100%)
                # Note: Ensure the platform supports short selling in strategy formulation
                # For platforms that do not support direct short selling in this manner,
                # you could use an inverse ETF or another method to represent a short position.
                allocation = {"SPY": -1.0}  # Assuming short selling is represented this way
            else:
                # If the current price is within the +/-5% range of SMA, close any position
                allocation = {"SPY": 0.0}
        else:
            # Not enough data to compute SMA, don't allocate
            allocation = {"SPY": 0.0}

        # Log the decision for debugging
        log("SPY Allocation: {}".format(allocation["SPY"]))
        # Return the determined allocation
        return TargetAllocation(allocation)