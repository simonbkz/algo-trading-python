import json
import os
import pandas as pd
pd.set_option('display.max_columns',None)

# Custom libraries
import mt5_lib
import indicator_lib
import ema_cross_strategy

#location of settings file
import_file_path = "C:\\Users\\SIMON\\Documents\\trading\\credentials.json"

def get_project_settings(import_file_path):
    if os.path.exists(import_file_path):
        f = open(import_file_path,'r')
        project_settings = json.load(f)
        f.close()
        return project_settings
    else:
        raise ImportError("this file does not exist in specified location")

def start_up(settings):
    startup = mt5_lib.start_mt5(settings)
    print("MetaTrader 5 has started up successfully!")
    if startup:
        symbols = settings['mt5']['symbols']
        for symbol in symbols:
            outcome = mt5_lib.initialize_symbol(symbol)
            if outcome:
                print(f"symbol {symbol} initialized")
            else:
                raise Exception(f"unable to initialize symbol {symbols}")
        return True
    return False

if __name__ == '__main__':

    settings = get_project_settings(import_file_path)
    startup = start_up(settings)
    symbols = settings['mt5']['symbols']
    timeframe = settings['mt5']['timeframe'] # we will focus on one timeframe for now, please ensure you only have one time frame in the .json file
    for symbol in symbols:
        #retrieve data for each candle
        sym_data = mt5_lib.get_candles_data(symbol=symbol, timeframe=timeframe, number_of_candles=10000)
        df = ema_cross_strategy.ema_cross_strategy(symbol, timeframe, ema_one=50, ema_two= 200)
        # getting ema cross signals
        ema_cross_trade_signals = df[df['ema_cross'] == True]
        last_signal = df.tail(1).copy()
        print(f"last signal: {last_signal}")

        if last_signal['ema_cross'].values:
            print("signal found")
        else:
            print("no signal for this candle")

    #     ema_50 = indicator_lib.calc_custom_ema(df=sym_data, ema_size=50)
    #     ema_20 = indicator_lib.calc_custom_ema(df=sym_data, ema_size=20)
    #     ema_200 = indicator_lib.calc_custom_ema(df=sym_data, ema_size=200)
    #     ema_cross = indicator_lib.ema_cross_calc(df=sym_data, ema_one=50, ema_two=200)
    #     ema_cross = ema_cross[ema_cross['ema_cross'] == True]
    #     print(ema_cross)
    # init_symbol = mt5_lib.initialize_symbol(symbol)
    # print(f"initialized symbols outcome: {init_symbol}")

    # git@github.com:simonbkz/algo-trading-python.git
