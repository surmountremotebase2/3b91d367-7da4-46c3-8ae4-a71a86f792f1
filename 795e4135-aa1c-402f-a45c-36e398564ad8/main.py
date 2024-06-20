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
        return "1hour"
    
    def run(self, data):
        open_time = "09:30:00"
        close_time = "15:30:00"
        d = data["ohlcv"]
        current_date, current_time = d[-1]["SPY"]["date"].split(" ")
        log("{0}, {1} aa".format(current_date, current_time))

        # Get the daily openings
        daily_opens = [i["SPY"]["open"] for i in d if open_time in i["SPY"]["date"]]
        #log(str(daily_opens))
        prior_daily_opens = daily_opens[-15:-1]
        current_daily_open = daily_opens[-1]

        # Get the prices from the same time as now in prior days
        same_time_prices = [i["SPY"]["close"] for i in d if current_time in i["SPY"]["date"]]
        #log(str(same_time_prices))
        prior_same_time_prices = same_time_prices[-15:-1]
        current_price = same_time_prices[-1]

        # Get the closing prices from prior days
        closing_prices = [i["SPY"]["close"] for i in d if close_time in i["SPY"]["date"]]
        #log(str([i["SPY"] for i in d[-10:]]))
        prior_closing_prices = closing_prices[-15:-1]
        current_closing_price = closing_prices[-1]

        if current_time == open_time: 
            log("Beginning of day, close any positions")
            allocation = {"SPY": 0.0}
        
        elif current_time == close_time: 
            log("End of day, close any positions")
            allocation = {"SPY": 0.0}

        elif len(prior_daily_opens) != 14 or len(prior_same_time_prices) != 14:
            log("Not enough data to lookback")
            allocation = {"SPY": 0.0}
        
        else:
            # Calculate the daily movement in prior day's from respective opening prices
            prior_relative_prices = [abs((i / j) - 1) for i, j in zip(prior_same_time_prices, prior_daily_opens)]
            avg_relative_price = sum(prior_relative_prices) / len(prior_relative_prices)

            # Define lower and upper bounds for initiating position
            upper_bound = max(current_daily_open, current_closing_price) * (1 + avg_relative_price)
            lower_bound = min(current_daily_open, current_closing_price) * (1 - avg_relative_price)
            log("lower {0}, upper {1}, current {2}".format(lower_bound, upper_bound, current_price))

            # Open position if we're outside of bounds, otherwise close position
            if current_price >= upper_bound:
                log("Upper bound breached")
                allocation = {"SPY": 1.0}
            elif current_price <= lower_bound:
                log("Lower bound breached")
                allocation = {"SPY": -1.0}
            else:
                allocation = {"SPY": 0.0}

        # Get the historical closing prices for SPY
        """log(str(d[0]))
        spy_prices = [i["SPY"]["close"] for i in d]
        
        log(str(len(spy_prices)))
        # Check if there are at least 14 days of data to compute SMA
        if len(spy_prices) >= 14:
            # Calculate the 14-day simple moving average for SPY
            spy_sma_14 = SMA("SPY", d, 14)[-1]
            
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
        """
        # Log the decision for debugging
        log("SPY Allocation: {}".format(allocation["SPY"]))
        # Return the determined allocation
        return TargetAllocation(allocation)