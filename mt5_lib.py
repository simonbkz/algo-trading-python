import pandas as pd
import ast
import MetaTrader5 as mt5
import talib

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
    print(f"timeframe in use: {timeframe}")
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

    