# mysybil_greeks.py
# Created by: MySybil.com and Justin Lee
# Last Modified: May 8, 2021
# Description: Foundational code for options analysis

import math
from scipy.stats import norm
from trading_calendars import get_calendar 
import OptionsPricing

class OptionAnalysis:
    """
    Object for estimating the implied volatility, calculating theoretical
    option prices and calculating the Greeks.

    Parameters
    ----------
    underlying_price : float
        The price of the stock underlying the option
    strike : float
        The strike price
    time_to_expiry : float
        The time remaining until the option expires in years
    dividend_yield : float
        The dividend yield (as a decimal, not percentage)
    opt_price : float
        The price of the option
    risk_free_rate : float
        The risk-free rate (as a decimal, not percentage)
    is_call : bool
        Whether the option is a call (if False, the option is a put)
    tolerance : float, optional, default: 1E-3
        The tolerance to use for estimating the implied volatility

    Attributes
    ----------
    self.up : float
    self.strike : float
    self.tte : float
    self.dy : float
    self.op : float
    self.rfr : float
    self.is_call : bool
    self.tol : float
    """
        
    def __init__(self, underlying_price, strike, time_to_expiry, dividend_yield,
                 opt_price, risk_free_rate, is_call, tolerance=1E-3):
        self.up = underlying_price
        self.strike = strike
        self.tte = time_to_expiry
        self.dy = dividend_yield
        self.op = opt_price
        self.rfr = risk_free_rate
        self.is_call = is_call
        self.tol = tolerance

    def get_option_value(self, implied_volatility):
        """Calculate the theoretical value of an option."""

        if self.is_call:
            opt_val = OptionsPricing.getCallPrice(implied_volatility, self.up, self.strike, self.rfr, self.tte)
        else:
            opt_val = OptionsPricing.getPutPrice(implied_volatility, self.up, self.strike, self.rfr, self.tte)
        return opt_val

    def get_market_year_fraction(start_date, end_date, adjustment):
        """Calculate the year fraction until the expiry date of an option in trading minutes.
      
        Parameters
        ----------
        start_date : string
            Inclusive start date for the time remaining [MM-DD-YYYY] ie: ('10-18-2020')
        end_date : string
            Inclusive end date for the time remaining [MM-DD-YYYY] ie: ('10-20-2020')
        adjustment : float
            [mins] An adjustment factor for handling intraday calculations 
        """
        mins = 390*len(get_calendar('XNYS').sessions_in_range(start_date, end_date)) + adjustment
        return mins/(252*390)

    def get_implied_volatility(self, max_iter=100):
        """Guess the implied volatility."""
        if self.tte <= 0:
            print(f"Warning: Time to expiry is negative "
                  + f"for strike {self.strike}. Returning NaN...")
            return float('NaN')

        try:
            if self.is_call:
                iv = OptionsPricing.getCallVol(self.op, self.up, self.strike, self.tte, self.rfr)
            else:
                iv = OptionsPricing.getPutVol(self.op, self.up, self.strike, self.tte, self.rfr)

            if math.isnan(iv):
                return 0
        except:
            print("TypeError in IV calculation. Returning NaN")
            return float('NaN')
            #return 0
            
        return iv

    def get_greeks(self, implied_volatility):
        """Compute the Greeks."""
        output = dict()
        output["gamma"] = OptionsPricing.getGamma(implied_volatility, self.up, self.strike, self.tte, self.rfr)
        output["vega"] = OptionsPricing.getVega(implied_volatility, self.up, self.strike, self.tte, self.rfr)

        if self.is_call:
            output["type"] = "call"
            output["delta"] = OptionsPricing.getCallDelta(implied_volatility, self.up, self.strike, self.tte, self.rfr)
            output["theta"] = OptionsPricing.getCallTheta(implied_volatility, self.up, self.strike, self.tte, self.rfr)
            output["rho"] = OptionsPricing.getCallRho(implied_volatility, self.up, self.strike, self.tte, self.rfr)
        else:
            output["type"] = "put"
            output["delta"] = OptionsPricing.getPutDelta(implied_volatility, self.up, self.strike, self.tte, self.rfr)
            output["theta"] = OptionsPricing.getPutTheta(implied_volatility, self.up, self.strike, self.tte, self.rfr)
            output["rho"] = OptionsPricing.getPutRho(implied_volatility, self.up, self.strike, self.tte, self.rfr)

        return output
