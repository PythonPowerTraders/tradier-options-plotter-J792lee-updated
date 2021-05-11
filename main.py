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
from bisect import bisect_left

import tp_plot_manager as tpm #formerly pm
import tp_request_manager as trm #formerly sdg
import tp_settings as tps

settings = tps.get_settings()
settings['type'] = 'C'
todays_date = datetime.today().strftime('%Y-%m-%d')
last_price = 0

# Finds strike closest to current price. Used as default value
def findClosestStrike(currPrice, strikeList):
    pos = bisect_left(strikeList, currPrice)
    if pos == 0:
        return strikeList[0]
    if pos == len(strikeList):
        return strikeList[-1]
    before = strikeList[pos - 1]
    after = strikeList[pos]
    if after - currPrice < currPrice - before:
       return after
    else:
       return before

#sets start date to the date corresponding to the selected timeframe
def setStartDate(day, doRefresh = True):
    global start_date
    if day == '1D':
        if datetime.today().weekday() == 5:
            yesterday = datetime.now() - timedelta(1)
            start_date = datetime.strftime(yesterday, '%Y-%m-%d')
        elif datetime.today().weekday() == 6:
            friday = datetime.now() - timedelta(2)
            start_date = datetime.strftime(friday, '%Y-%m-%d')
        else:
            start_date = todays_date
    elif day == "7D":
        start_date = datetime.strftime(datetime.now() - timedelta(7), '%Y-%m-%d')
    elif day == "1M": 
        start_date = datetime.strftime(datetime.now() - timedelta(30), '%Y-%m-%d')
    elif day == "6M": 
        start_date = datetime.strftime(datetime.now() - timedelta(180), '%Y-%m-%d')
    elif day == "YTD": 
        start_date = start_date[0:4] + "-01-01"
        print(start_date)
    else:
        start_date = datetime.strftime(datetime.now() - timedelta(365), '%Y-%m-%d')
    
    if doRefresh:
        refresh()

#updates the ticker, price, and change in the top left of the screen
def updateTicker():
    try:
        lastPrice, perc = trm.getLastandChange(ticker, settings['API_KEY'])
    except:
        print("data could not be obtained")
        return

    tickerPriceAndChange.set("$" + str(round(lastPrice, 2)) + "    " + str(round(perc,2)) + "%")
    if perc > 0:
        percLabel.config(fg = "#62FF96")
    elif perc < 0:
        percLabel.config(fg = "#FF6060")

    global last_price
    last_price = lastPrice

#handles the plot
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

    # Let's get data on the underlying and then match it up and calculate the IV at every point.

    try:
        underlying_data = trm.get_underlying_data(ticker,
                                            start_date, 
                                            settings['downloadBinning'], 
                                            should_use_history_endpoint, 
                                            settings['API_KEY'])
    except:
        print("underlying data could not be obtained")
        return
    
    try:
        trade_data = trm.get_trade_data(option_symbol, 
                                        start_date, 
                                        settings['downloadBinning'], 
                                        should_use_history_endpoint, 
                                        settings['API_KEY'])
    except:
        print("trade data could not be obtained")
        return
    
    fig, ax = tpm.plot_data(trade_data, 
                    underlying_data,
                    should_use_history_endpoint, 
                    data_name, 
                    settings,
                    toGraphDropdownString.get())
    
    canvas = FigureCanvasTkAgg(fig, master=middleFrame)   
    canvas.draw()
    canvas.get_tk_widget().grid(row=0, column=0)

#changes the expiry date dropdown when the user selects a new ticker
def change_expiry_dropdown():
    expiryDropdown.configure(state="normal")
    try:
        optionsDates = get_expiry_dates(ticker, settings["API_KEY"])
    except:
        return

    expiryDropdown['menu'].delete(0, "end")
    for curDate in optionsDates:
        expiryDropdown['menu'].add_command(label=curDate, command=lambda x=curDate: (optionsDropdownString.set(x)
                                                                               , picked_expiry(x)))
    if optionsDropdownString.get() not in optionsDates:
        optionsDropdownString.set(optionsDates[0])

#changes the strike dropdown when the user selects a new ticker
def change_strike_dropdown():
    strikeDropdown.configure(state="normal")
    try:
        options_strikes = get_strike_list(ticker, optionsDropdownString.get(), settings["API_KEY"])
    except:
        return
    closest = findClosestStrike(last_price, options_strikes)
    closestIndex = options_strikes.index(closest)
    if len(options_strikes) > 30:
        options_strikes = options_strikes[max(closestIndex - 15, 0): min(closestIndex + 15, len(options_strikes) - 1)]

    strikeDropdown['menu'].delete(0, "end")
    for curStrike in options_strikes:
        strikeDropdown['menu'].add_command(label=curStrike, command=lambda x=curStrike: (optionsStrikeDropdownString.set(x)
                                                                                        , refresh()))
    closestIndex = options_strikes.index(closest)
    optionsStrikeDropdownString.set(options_strikes[closestIndex])

#changes ticker when the user types a new one in and presses enter
def ticker_return_entry(en):
    global ticker
    ticker = tickerInput.get().upper()
    tickerLabel.set(ticker)
    updateTicker()
    change_expiry_dropdown()
    change_strike_dropdown()

    refresh()

#changes the chart when the user picks a new expiry
def picked_expiry(selection):
    change_strike_dropdown()
    
    refresh()

#refreshes screen
def refresh(x = 0): 
    settings['expiry'] = optionsDropdownString.get()
    settings['strike'] = optionsStrikeDropdownString.get()
    if CallDropdownString.get() == "Call":
        settings['type'] = 'C'
    else:
        settings['type'] = 'P'
    try:
        makePlot()
    except:
        print("could not make plot")

def ask_quit():
    exit()

start_date = todays_date
setStartDate("7D", False)

#main window
window = Tk()
window.title("GUI")
window.geometry("1200x700")
window.configure(background='#121212')

#frame for plot
middleFrame = Frame(window, width=800, height= 580, bg='#161616')
middleFrame.place(x = 360, y = 30)

ticker = ""
tickerLabel = StringVar()
tickerPriceAndChange = StringVar()

#labels
Label(window, text = "Ticker", fg="white", background='#121212', font='Helvetica 14').place(x = 30, y = 150)
Label(window, text = "Expiry", fg="white", background='#121212', font='Helvetica 14').place(x = 30, y = 200)
Label(window, text = "Strike", fg="white", background='#121212', font='Helvetica 14').place(x = 30, y = 250)
Label(window, text = "Type", fg="white",  background='#121212', font='Helvetica 14').place(x = 30, y = 300)
Label(window, text = "Value", fg="white",  background='#121212', font='Helvetica 14').place(x = 30, y = 350)
Label(window, textvariable = tickerLabel, font='Helvetica 18 bold', fg="white",  background='#121212',).place(x = 30, y = 80)
percLabel = Label(window, textvariable = tickerPriceAndChange, font='Helvetica 18 bold', fg="white",  background='#121212',)
percLabel.place(x = 150, y = 80)

#inputs
tickerInput = Entry(window, textvariable=ticker)
tickerInput.place(x = 90, y = 150)
tickerInput.bind('<Return>', ticker_return_entry)
tickerInput.config(bg="#505050", fg="white",)

optionsDropdownString = StringVar(window)
optionsDropdownString.set("YYYY-MM-DD") # default value

expiryDropdown = OptionMenu(window, optionsDropdownString, '')
expiryDropdown.configure(state="disabled")
expiryDropdown['highlightthickness'] = 0
expiryDropdown.config(bg="#505050", fg="white",)
expiryDropdown.place(x = 90, y = 200)

optionsStrikeDropdownString = StringVar(window)
optionsStrikeDropdownString.set("$XXX.XX") # default value

strikeDropdown = OptionMenu(window, optionsStrikeDropdownString, '')
strikeDropdown.configure(state="disabled")
strikeDropdown['highlightthickness'] = 0
strikeDropdown.config(bg="#505050", fg="white",)
strikeDropdown.place(x = 90, y = 250)

CallDropdownString = StringVar(window)
CallDropdownString.set("Call")

callPutDropdown = OptionMenu(window, CallDropdownString, "Call", "Put", command = refresh)
callPutDropdown.place(x = 90, y = 300)
callPutDropdown['highlightthickness'] = 0
callPutDropdown.config(bg="#505050", fg="white",)

toGraphDropdownString = StringVar(window)
toGraphDropdownString.set("Price")

toGraphDropdown = OptionMenu(window, toGraphDropdownString, "Price", "IV", "Delta", "Gamma", "Theta", "Vega", "Rho", command = refresh)
toGraphDropdown.place(x = 90, y = 350)
toGraphDropdown['highlightthickness'] = 0
toGraphDropdown.config(bg="#505050", fg="white",)

Button(window, text ="1D", width = 14, fg="white", background='#121212', command = lambda: setStartDate("1D")).place(x = 360, y = 610)
Button(window, text ="7D", width = 14, fg="white", background='#121212', command = lambda: setStartDate("7D")).place(x = 490, y = 610)
Button(window, text ="1M", width = 14, fg="white", background='#121212', command = lambda: setStartDate("1M")).place(x = 620, y = 610)
Button(window, text ="6M", width = 14, fg="white", background='#121212', command = lambda: setStartDate("6M")).place(x = 750, y = 610)
Button(window, text ="YTD", width = 14, fg="white", background='#121212', command = lambda: setStartDate("YTD")).place(x = 880, y = 610)
Button(window, text ="1Y", width = 15, fg="white", background='#121212', command = lambda: setStartDate("1Y")).place(x = 1010, y = 610)

window.protocol("WM_DELETE_WINDOW", ask_quit)
window.mainloop()