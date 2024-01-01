import pandas as pd
import ast
import MetaTrader5 as mt5
import talib
import datetime
from dateutil.relativedelta import relativedelta

def start_mt5(settings):
    
    password = settings['mt5']['password']
    username = int(settings["mt5"]["username"])  
    server = settings['mt5']['server']
    mt5_pathway = settings['mt5']['mt5_pathway']

    mt5_init = False

    try:
        mt5_init = mt5.initialize(
            login=username,
            password=password,
            server=server,
            path=mt5_pathway
        )
    except Exception as e:
        print("there was an error initializing MetaTrader 5 for account {0} with error {1}".format(username,e))
        mt5_init = False

    mt5_login = False
    if mt5_init:
        try:
            mt5_login=mt5.login(
                login=username,
                password=password,
                server=server
            )
        except Exception as e:
            print("unable to login to MetaTrader 5 for account {0} with an error {1}".format(username,e))
            mt5_login = False
       
    if mt5_login:
        return True
    return False

def initialize_symbol(symbol):
    
    all_symbols = mt5.symbols_get()
    symbol_names = []

    for sym in all_symbols:
        symbol_names.append(sym.name)

    if symbol in symbol_names:
        try:
            mt5.symbol_select(symbol, True)
            return True 
        except Exception as e:
            print(f"error enabling symbol {symbol} with error {e}")
            return False 
    else:
        print(f"symbol {symbol} does not exist in the list of available symbols from broker")
        return False
    
# Function to query mt5 for the data
def get_candles_data(symbol, timeframe, number_of_candles):
    # check if there are no more than 50000 candles sticks
    if number_of_candles > 50000:

        raise ValueError("no more than 50000 candles can be retrieved")
    
    mt5_timeframe = set_query_timeframe(timeframe)
    candles = mt5.copy_rates_from_pos(symbol, mt5_timeframe, 1, number_of_candles)
    df = pd.DataFrame(candles)
    return df

def set_query_timeframe(timeframe):
    custom_timeframes = ['M1','M2','M3','M4','M5','M6','M10','M12','M15','M20','M30','H1','H2','H3','H4','H6','H8','H12','D1','W1','MN1']
    # try:
    #     if timeframe in custom_timeframes:
    #         tmp = ast.literal_eval("TIMEFRAME_"+timeframe)
    #         print(f"transformed var is: {tmp}")
    #         mt5_time_fmt = mt5.TIMEFRAME_+timeframe
    #         return mt5_time_fmt
    # except Exception as e:
    #     raise TypeError(f"timeframe is not the correct format. Error {e}")
    if timeframe == 'M1':
        return mt5.TIMEFRAME_M1
    elif timeframe == 'M2':
        return mt5.TIMEFRAME_M2
    elif timeframe == 'M3':
        return mt5.TIMEFRAME_M3
    elif timeframe == 'M4':
        return mt5.TIMEFRAME_M4
    elif timeframe == 'M5':
        return mt5.TIMEFRAME_M5
    elif timeframe == 'M6':
        return mt5.TIMEFRAME_M6
    elif timeframe == 'M10':
        return mt5.TIMEFRAME_M10
    elif timeframe == 'M12':
        return mt5.TIMEFRAME_M12
    elif timeframe == 'M15':
        return mt5.TIMEFRAME_M15
    elif timeframe == 'M20':
        return mt5.TIMEFRAME_M20
    elif timeframe == 'M30':
        return mt5.TIMEFRAME_M30
    elif timeframe == 'H1':
        return mt5.TIMEFRAME_H1
    elif timeframe == 'H2':
        return mt5.TIMEFRAME_H2
    elif timeframe == 'H3':
        return mt5.TIMEFRAME_H3
    elif timeframe == 'H4':
        return mt5.TIMEFRAME_H4
    elif timeframe == 'H6':
        return mt5.TIMEFRAME_H6
    elif timeframe == 'H8':
        return mt5.TIMEFRAME_H8
    elif timeframe == 'H12':
        return mt5.TIMEFRAME_H12
    elif timeframe == 'D1':
        return mt5.TIMEFRAME_D1
    elif timeframe == 'W1':
        return mt5.TIMEFRAME_W1
    elif timeframe == 'MN1':
        return mt5.TIMEFRAME_MN1
    else:
        raise ValueError("the time frame is not supported by the broker")

# Function to place an order on MetaTrader 5
def place_order(order_type, symbol, volume, stop_loss, take_profit, comment, stop_price, direct = False):
    """
    Function to place an order on MetaTrader 5. Function checks the order first then places trade if order check returns true
    :param order_type: string and options are SELL_STOP and BUY_STOP
    :param symbol: string of the symbol to be traded
    :param volume: string or float of the volume to be traded
    :param stop_loss: string or float of stop loss
    :param take_profit: string or float of take profit
    :param comment: comments which is a string
    :param stop_price: string or float of stop price
    :param direct: boolean, it is False by default, when True it will bypass order check
    :return:trade outcome
    """
    #   make sure volume, stop_loss, take_profit, stop_price are correct format
    volume = float(volume)
    # volume can only be two decimal places
    volume = round(volume, 2)

    stop_loss = float(stop_loss)
    stop_loss = round(stop_loss, 4)
    take_profit = float(take_profit)
    take_profit = round(take_profit, 4)
    stop_price = float(stop_price)
    stop_price = round(stop_price, 4)

    request = {
        "symbol": symbol,
        "volume": volume,
        "sl": stop_loss,
        "tp": take_profit,
        "type_time": mt5.ORDER_TIME_GTC,
        "comment": comment
    }

    #create the order type based on values
    if order_type == "SELL_STOP":
        request['type'] = mt5.ORDER_TYPE_SELL_STOP
        request['action'] = mt5.TRADE_ACTION_PENDING
        request['type_filling'] = mt5.ORDER_FILLING_RETURN
        if stop_price <= 0:
            raise ValueError("stop price cannot be less than or equal to 0")
        else:
            request['price'] = stop_price
    elif order_type == "BUY_STOP":
        request['type'] = mt5.ORDER_TYPE_BUY_STOP
        request['action'] = mt5.TRADE_ACTION_PENDING
        request['type_filling'] = mt5.ORDER_FILLING_RETURN
        if stop_price <= 0:
            raise ValueError("stop price cannot be less than or equal to zero")
        else:
            request['price'] = stop_price
    else:
        raise ValueError(f"unsupported order type {order_type} provided")

    if direct:
        order_result = mt5.order_send(request)
        if order_result[0] == 10009:
            print(f"order for {symbol} has been successful")
            return order_result[2]
        elif order_result[0] == 10027:
            print("turn off algo trading in mt5 ")
            raise Exception("turn off algo trading in mt5 terminal")
        elif order_result[0] == 10015:
            print(f"invalid price for {symbol}. Price {stop_price}")
        elif order_result[0] == 10016:
            print(f"invalid stops for {symbol}. stop loss: {stop_loss}")
        elif order_result[0] == 10014:
            print(f"invalid volume for {symbol}. volume: {volume}")
        else:
            print(f"Error lodging order for {symbol}. Error code: {order_result[0]}")
            raise Exception(f"unknown error lodging error for {symbol}")
    else:
        result = mt5.order_check(request)
        if result[0] == 0:
            print(f"order for {symbol} is successful")
            place_order(order_type=order_type,
                        symbol=symbol,
                        volume=volume,
                        stop_loss=stop_loss,
                        take_profit=take_profit,
                        comment=comment,
                        stop_price=stop_price,
                        direct=True)
        elif result[0] == 10015:
            print(f"invalid price for {symbol}. Price {stop_price}")
        else:
            print(f"order check failed. Details {result}")

def cancel_order(order_number):
    """
    Function to cancel an order identified by an order number
    :param order_number: int of the order number
    :return: Boolean. True means cancelled, False means not cancelled.
    """
    # Create the request
    request = {
        "action": mt5.TRADE_ACTION_REMOVE,
        "order": order_number,
        "comment": "order removed"
    }

    # Attempt to send the order to MT5
    try:
        order_result = mt5.order_send(request)
        if order_result[0] == 10009:
            return True
        else:
            return False
    except Exception as e:
        print(f"Error cancelling order {order_number}. {e}")
        # More advanced error handling is covered in later videos
        return False

# Function to cancel a list of open orders
def cancel_all_orders(order_list):
    """
    Function to cancel all open orders in a list
    :param symbol_list: list of orders
    :return: Boolean. True if all are cancelled
    """
    # Iterate through the list of order numbers
    for order_number in order_list:
        # Cancel each one
        cancel = cancel_order(order_number)
        # If an order is not cancelled, exit the function
        if cancel is False:
            return False
    # If no exit event, return True
    return True

# Function to retrieve all open orders from MT5
def get_all_open_orders():
    """
    Function to retrieve all open orders from MetaTrader 5
    :return: list of orders
    """
    return mt5.orders_get()

# Function to retrieve a filtered list of open orders from MT5
def get_filtered_list_of_orders(symbol, comment):
    """
    Function to retrieve a filtered list of open orders from MT5. In this case, filtering is done by
    symbol and comment
    :param symbol: string of the symbol
    :param comment: string of the comment
    :return: list of orders
    """
    # Retrieve open orders, filter by symbol
    open_orders_by_symbol = mt5.orders_get(symbol)
    # Check if any orders were retrieved (there might be none)
    if open_orders_by_symbol is None:
        return []
    # Convert the returned orders into a dataframe
    open_orders_dataframe = pd.DataFrame(list(open_orders_by_symbol), columns=open_orders_by_symbol[0]._asdict().keys())
    # From the open orders dataframe, filter orders by comment
    open_orders_dataframe = open_orders_dataframe[open_orders_dataframe['comment'] == comment]
    # Create a list to store the open order numbers
    open_orders = []
    # Iterate through the dataframe and add order numbers to the list
    for order in open_orders_dataframe['ticket']:
        open_orders.append(order)
    # Return the open order numbers
    return open_orders

# Function to query historic candlestick data from MT5
def query_historic_data(symbol, timeframe, number_of_candles):
    """
    Function to query historic data from MetaTrader 5
    :param symbol: string of the symbol to query
    :param timeframe: string of the timeframe to query
    :param number_of_candles: Number of candles to query. Limited to 50,000
    :return: dataframe of the queried data
    """
    # Check the number of candles less than 50000
    # Note that MT5 can return far more than 50,000 candles, but this is beyond this tutorial
    if number_of_candles > 50000:
        raise ValueError("Select less than 50,000 candles")
    # Convert the timeframe into MT5 friendly format
    mt5_timeframe = set_query_timeframe(timeframe=timeframe)
    # Retrieve the data
    rates = mt5.copy_rates_from_pos(symbol, mt5_timeframe, 1, number_of_candles)
    # Convert to a dataframe
    dataframe = pd.DataFrame(rates)
    # Add a 'Human Time' column
    dataframe['human_time'] = pd.to_datetime(dataframe['time'], unit='s')
    return dataframe

# Function to retrieve data from MT5 using a time range rather than a number of candles
def query_historic_data_by_time(symbol, timeframe, time_range):
    """
    Function to retrieve data from MT5 using a time range rather than a number of candles
    :param symbol: string of the symbol to be retrieved
    :param timeframe: string of the candlestick timeframe to be retrieved
    :param time_range: string of the time range to be retrieved. Options are: 1Month, 3Months, 6Months, 1Year, 2Years, 3Years, 5Years, All
    :return: dataframe of the queried data
    """
    # Convert the timeframe into MT5 friendly format
    mt5_timeframe = set_query_timeframe(timeframe=timeframe)
    # Get the end datetime of the time range (i.e. now)
    end_time = datetime.datetime.now()
    # Get the start datetime of the time range, based on the time range string
    if time_range == "1Month":
        start_time = end_time - relativedelta(months=1)
    elif time_range == "3Months":
        start_time = end_time - relativedelta(months=3)
    elif time_range == "6Months":
        start_time = end_time - relativedelta(months=6)
    elif time_range == "1Year":
        start_time = end_time - relativedelta(years=1)
    elif time_range == "2Years":
        start_time = end_time - relativedelta(years=2)
    elif time_range == "3Years":
        start_time = end_time - relativedelta(years=3)
    elif time_range == "5Years":
        start_time = end_time - relativedelta(years=5)
    elif time_range == "All":
        start_time = datetime.datetime(1970, 1, 1)
    else:
        raise ValueError("Incorrect time range provided")

    # Retrieve the data
    rates = mt5.copy_rates_range(symbol, mt5_timeframe,start_time, end_time)
    # Convert to a dataframe
    dataframe = pd.DataFrame(rates)
    # Add a 'Human Time' column
    dataframe['human_time'] = pd.to_datetime(dataframe['time'], unit='s')
    return dataframe

# Function to retrieve the pip_size of a symbol from MT5
def get_pip_size(symbol):
    """
    Function to retrieve the pip size of a symbol from MetaTrader 5
    :param symbol: string of the symbol to be queried
    :return: float of the pip size
    """
    # Get the symbol information
    symbol_info = mt5.symbol_info(symbol)
    tick_size = symbol_info.trade_tick_size
    pip_size = tick_size * 10
    # Return the pip size
    return pip_size

# Function to retrieve the base currency of a symbol from MT5
def get_base_currency(symbol):
    """
    Function to retrieve the base currency of a symbol from MetaTrader 5
    :param symbol: string of the symbol to be queried
    :return: string of the base currency
    """
    # Get the symbol information
    symbol_info = mt5.symbol_info(symbol)
    # Return the base currency
    return symbol_info.currency_base

# Function to retrieve the exchange rate of a symbol from MT5
def get_exchange_rate(symbol):
    """
    Function to retrieve the exchange rate of a symbol from MetaTrader 5
    :param symbol: string of the symbol to be queried
    :return: float of the exchange rate
    """
    # Get the symbol information
    symbol_info = mt5.symbol_info(symbol)
    # Return the exchange rate
    return symbol_info.bid

# Get the contract size for a symbol
def get_contract_size(symbol):
    """
    Function to retrieve the contract size of a symbol from MetaTrader 5
    :param symbol: string of the symbol to be queried
    :return: float of the contract size
    """
    # Get the symbol information
    symbol_info = mt5.symbol_info(symbol)
    # Return the contract size
    return symbol_info.trade_contract_size

# Function to get the balance from MT5
def get_balance():
    """
    Function to get the balance from MetaTrader 5
    :return: float of the balance
    """
    # Get the account information
    account_info = mt5.account_info()
    # Return the balance
    return account_info.balance