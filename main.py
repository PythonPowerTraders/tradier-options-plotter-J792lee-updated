from tkinter import *
from tp_request_manager import get_expiry_dates, get_strike_list
import mplfinance as mpf
from matplotlib.figure import Figure
import pandas as pd
import matplotlib as matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime, timedelta
from math import floor, ceil

import tp_plot_manager as tpm #formerly pm
import tp_request_manager as trm #formerly sdg
import tp_settings as tps
import tp_ui_manager as tpu # formerly sui

settings = tps.get_settings()
settings['type'] = 'C'
todays_date = datetime.today().strftime('%Y-%m-%d')

if datetime.today().weekday() == 5:
    yesterday = datetime.now() - timedelta(1)
    start_date = datetime.strftime(yesterday, '%Y-%m-%d')
elif datetime.today().weekday() == 6:
    friday = datetime.now() - timedelta(2)
    start_date = datetime.strftime(friday, '%Y-%m-%d')
else:
    start_date = todays_date

def makePlot():
    format_date = settings['expiry'].replace("-", "")[2:len(settings['expiry'].replace("-", ""))]
    # Format the date string for Tradier's API formatting (strip dashes then strip 20 off the front of 2021)

    selected_price = '{0:08d}'.format(int(float(settings['strike'])*1000)) 
    # Format the price string for Tradier

    should_use_history_endpoint = trm.get_start_date(int(settings['historyLimit']), start_date)
    # Prompt user for date range and figure out which data type they're looking for.

    option_symbol = ticker + format_date + settings['type'] + selected_price 
    # Full Tradier-formatted symbol for the option

    data_name = ticker + " $" + str(float(selected_price)/1000) + settings['type'] + " (" + settings['expiry'] + ")"
    # Plot title

    print("Now downloading trade data for: " + data_name)
    try:
        trade_data = trm.get_trade_data(option_symbol, 
                                        start_date, 
                                        settings['downloadBinning'], 
                                        should_use_history_endpoint, 
                                        settings['API_KEY'])
    except:
        print("trade data could not be obtained")
        return

    # Let's get data on the underlying and then match it up and calculate the IV at every point.
    try:
        underlying_data = trm.get_underlying_data(ticker,
                                            start_date, 
                                            settings['downloadBinning'], 
                                            should_use_history_endpoint, 
                                            settings['API_KEY'])
    except:
        print("underlying data could not be obtained")

    
    fig, ax = tpm.plot_data(trade_data, 
                    underlying_data,
                    should_use_history_endpoint, 
                    data_name, 
                    settings)

    canvas = FigureCanvasTkAgg(fig, master=middleFrame)   
    canvas.draw()
    canvas.get_tk_widget().grid(row=0, column=0)

def ticker_return_entry(en):
    global ticker
    ticker = tickerInput.get().upper()
    expiryDropdown.configure(state="normal")
    optionsDates = get_expiry_dates(ticker, settings["API_KEY"])

    expiryDropdown['menu'].delete(0, "end")
    for curDate in optionsDates:
        expiryDropdown['menu'].add_command(label=curDate, command=lambda x=curDate: (optionsDropdownString.set(x)
                                                                               , picked_expiry(x)))
    if optionsDropdownString.get() not in optionsDates:
        optionsDropdownString.set(optionsDates[0])

    strikeDropdown.configure(state="normal")
    options_strikes = get_strike_list(ticker, optionsDropdownString.get(), settings["API_KEY"])
    if len(options_strikes) > 20:
        options_strikes = options_strikes[floor((len(options_strikes)-20)/2): ceil(-(len(options_strikes)-20)/2)]

    strikeDropdown['menu'].delete(0, "end")
    for curStrike in options_strikes:
        strikeDropdown['menu'].add_command(label=curStrike, command=lambda x=curStrike: optionsStrikeDropdownString.set(x))

    if optionsStrikeDropdownString.get() == "$XXX.XX" or float(optionsStrikeDropdownString.get()) not in options_strikes:
        optionsStrikeDropdownString.set(options_strikes[0])

    settings['expiry'] = optionsDropdownString.get()
    settings['strike'] = optionsStrikeDropdownString.get()
    if CallDropdownString.get() == "Call":
        settings['type'] = 'C'
    else:
        settings['type'] = 'P'
    makePlot()

def picked_expiry(selection):
    strikeDropdown.configure(state="normal")
    options_strikes = get_strike_list(ticker, selection, settings["API_KEY"])
    if len(options_strikes) > 20:
        options_strikes = options_strikes[floor((len(options_strikes)-20)/2): - ceil((len(options_strikes)-20)/2)]
    strikeDropdown['menu'].delete(0, "end")
    for strike in options_strikes:
        strikeDropdown['menu'].add_command(label=strike, command=lambda x=strike: optionsStrikeDropdownString.set(x))

    print(optionsStrikeDropdownString.get())
    if optionsStrikeDropdownString.get() == "$XXX.XX" or float(optionsStrikeDropdownString.get()) not in options_strikes:
        optionsStrikeDropdownString.set(options_strikes[0])
    
    settings['expiry'] = optionsDropdownString.get()
    settings['strike'] = optionsStrikeDropdownString.get()
    if CallDropdownString.get() == "Call":
        settings['type'] = 'C'
    else:
        settings['type'] = 'P'
    makePlot()

def ask_quit():
    exit()

window = Tk()
window.title("GUI")
window.geometry("1400x800")

middleFrame = Frame(window, width=800, height= 580, bg='white')
middleFrame.grid(row = 5, column=3, padx=10, pady=5, rowspan = 50)


ticker = ""
date = ""
strike = ""
Label(window, text = "Ticker").grid(row = 8)
Label(window, text = "Expiry").grid(row = 9)
Label(window, text = "Strike").grid(row = 10)
Label(window, text = "Type").grid(row = 11)

tickerInput = Entry(window, textvariable=ticker)
tickerInput.grid(row = 8, column = 1)
tickerInput.bind('<Return>', ticker_return_entry)

optionsDropdownString = StringVar(window)
optionsDropdownString.set("YYYY-MM-DD") # default value

expiryDropdown = OptionMenu(window, optionsDropdownString, '')
expiryDropdown.configure(state="disabled")
expiryDropdown.grid(row = 9, column = 1)

optionsStrikeDropdownString = StringVar(window)
optionsStrikeDropdownString.set("$XXX.XX") # default value

strikeDropdown = OptionMenu(window, optionsStrikeDropdownString, '')
strikeDropdown.configure(state="disabled")
strikeDropdown.grid(row = 10, column = 1)

CallDropdownString = StringVar(window)
CallDropdownString.set("Call")
callPutDropdown = OptionMenu(window, CallDropdownString, "Call", "Put")
callPutDropdown.grid(row = 11, column = 1)



window.columnconfigure(3, weight = 3)
window.protocol("WM_DELETE_WINDOW", ask_quit)
window.mainloop()