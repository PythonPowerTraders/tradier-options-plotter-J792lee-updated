"""
tp_request_manager.py
Last Modified: October 11, 2020
Description: This script handles all the data grabbing / formatting for run_sybil_plotter.py 
"""

# TODO: get_underlying_data() should only grab history data up until the option expiry date. 
# TODO: investigate error in grabbing underlying data. See line 146. 
            # I need to validate the data. See line 128

from datetime import datetime
import requests
import time

root_url = 'https://sandbox.tradier.com/v1/markets'

#gets last price and % change
def getLastandChange(ticker, api_key):
    response = requests.get(root_url + '/quotes',
        params={'symbols': ticker, 'greeks': 'false'},
        headers={'Authorization': api_key, 'Accept': 'application/json'}
    )
    return (response.json()["quotes"]["quote"]["last"], response.json()["quotes"]["quote"]["change_percentage"])

# Download a list of all available expiry dates for options for the symbol
def get_expiry_dates(ticker, api_key):
    dates_response = requests.get(root_url + '/options/expirations?',
        params={'symbol': ticker},
        headers={'Authorization': api_key, 'Accept': 'application/json'}
    )
    dates_json = dates_response.json()
    dates_list = dates_json['expirations']['date']
    
    if not (len(dates_list)):
        print("No options available for symbol: " +  ticker + ". Terminating Program.")

    return dates_list

# Download and print a list of all available strikes for the expiry date.
def get_strike_list(ticker, expiry, api_key):
    strike_list_response = requests.get(root_url + '/options/strikes?',
        params={'symbol': ticker, 'expiration': expiry},
        headers={'Authorization': api_key, 'Accept': 'application/json'}
    )
    strikes_json = strike_list_response.json()
    strikeList = strikes_json['strikes']['strike']
    
    return strikeList

# Prompt the user for the earliest date in which they want to get data for, then determine whether to retrieve /history/ or /timesales/ data.
def get_start_date(history_limit, start_date):
    try:
        start_datenum = datetime.strptime(start_date, "%Y-%m-%d")
    except ValueError:
        print("Invalid date format.")

    start_date_seconds = time.mktime(start_datenum.timetuple())
    current_time_seconds = time.mktime(datetime.now().timetuple()) #seconds since the input date

    should_use_history_endpoint = False
    if (current_time_seconds - start_date_seconds > history_limit*24*60*60):
        should_use_history_endpoint = True

    return should_use_history_endpoint

# Get a timeseries of all the trade data.
def get_trade_data(option_symbol, start_date, binning, should_use_history_endpoint, api_key):
    if(should_use_history_endpoint):
        trade_data_response = requests.get(root_url + '/history?',
            params={'symbol': option_symbol, 'start': start_date},
            headers={'Authorization': api_key, 'Accept': 'application/json'}
        )
        trade_data_json = trade_data_response.json()
        try:
            return(trade_data_json['history']['day'])
        except TypeError:
            print(trade_data_json)
            print('TypeError. No options data in tp_request_manager.get_trade_data().')
    else:
        trade_data_response = requests.get(root_url + '/timesales?',
            params={'symbol': option_symbol, 'start': start_date, 'interval':(str(int(binning))+"min")},
            headers={'Authorization': api_key, 'Accept': 'application/json'}
        )
        trade_data_json = trade_data_response.json()
        return (trade_data_json['series']['data'])


def get_underlying_data(symbol, start_date, binning, should_use_history_endpoint, api_key):
    if(should_use_history_endpoint):
        trade_data_response = requests.get(root_url + '/history?',
            params={'symbol': symbol, 'start': start_date},
            headers={'Authorization': api_key, 'Accept': 'application/json'}
        )
        trade_data_json = trade_data_response.json()
        return(trade_data_json['history']['day'])
    else:
        trade_data_response = requests.get(root_url + '/timesales?',
            params={'symbol': symbol, 'start': start_date, 'interval':(str(int(binning))+"min")},
            headers={'Authorization': api_key, 'Accept': 'application/json'}
        )
        trade_data_json = trade_data_response.json()
        return (trade_data_json['series']['data'])

