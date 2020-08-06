# closed_option_driver.py
# Last Modified: August 5, 2020
# Description: This script is the sister script to run_sybil_plotter.py and works for options that have already expired. The catch is that you need to already know all the info about the options since we can't fetch a list of past expiry dates or strikes available on a given date.

import sybil_data_ui_helper as sui
import sybil_data_grab as sdg
import sybil_data_plot_master as pm
import sybil_data_settings

# TODO: Support for stocks the don't trade anymore. (ie: YHOO). gets caught in the background_info call

sui.intro_screen(); # just some printing / instructions to introduce the program
settings = sybil_data_settings.get_settings()
symbol = input("Enter a symbol to proceed: ").upper()

description = sdg.background_info(symbol, settings['API_KEY']) # Display some info about the underlying
option_type = sdg.option_type(symbol)

# Prompt the user to pick one of the expiry dates (no list display due to prior expiry)
date = input("Input the expiry date of the options in YYYY-mm-dd: ")

# Format the date string for Tradier's API formatting (strip dashes then strip 20 off the front of 2021)
format_date = date.replace("-", "")[2:len(date.replace("-", ""))]

selected_price = input("Input the strike price of the option: ")

# Format the price string for Tradier
selected_price = '{0:08d}'.format(int(float(selected_price)*1000)) 
# Prompt user for date range
start_date, should_use_history_endpoint = sdg.get_start_date(int(settings['historyLimit']))
# Full Tradier-formatted symbol for the option
option_symbol = symbol + format_date + option_type + selected_price 
# Plot title
data_name = symbol + " $" + str(float(selected_price)/1000) + option_type + " (" + date + ")"

# Download the trade data and plot it
print("Now downloading trade data for: " + data_name)
trade_data = sdg.get_trade_data(option_symbol, 
                                start_date, 
                                settings['downloadBinning'], 
                                should_use_history_endpoint, 
                                settings['API_KEY'])

pm.plot_data(trade_data, 
            should_use_history_endpoint, 
            data_name, 
            settings)
    
print("Program Reached End Of Execution.")