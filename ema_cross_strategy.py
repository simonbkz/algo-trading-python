import mt5_lib
import indicator_lib

def ema_cross_strategy(symbol, timeframe, ema_one, ema_two):
    """
    Function which runs the ema cross strategy
    :param symbol: string of the symbol to be queried
    :param timeframe: timeframe to be applied to the queried symbol
    :param ema_one: integer size of ema 1
    :param ema_two: integer size of ema 2
    :return: trade event of the dataframe
    """

    #pseudo code
    # step 1: Retrieve data
    # step 2: calculate indicator
    # step 3: determine if the trade event has occured
    # step 4: check the previous trade
    # step 5: return information back to the user

    # step 1:
    df = get_data(symbol,timeframe)

    #step 2
    df = calc_indicators(df, ema_one, ema_two)

    # step 3
    df = det_trade(df, ema_one, ema_two)

    # step 4: return information back to the user
    trade_event = df.tail(1).copy()
    # check if ema cross has occured
    if trade_event['ema_cross'].values:
        new_trade = True
    else:
        new_trade = False

    return new_trade

# Function to determine if trading event has occured
def det_trade(df, ema_one, ema_two):
    """
    Function to determine the signal for a trade event
    :param df: dataframe
    :param ema_one: integer of ema 1 size
    :param ema_two: integer of ema 2 size
    :return:
    """
    ema_one_column = "ema_"+str(ema_one)
    ema_two_column = "ema_"+str(ema_two)
    if ema_one > ema_two:
        ema_column = ema_one_column
        min_value = ema_one
    elif ema_two > ema_one:
        ema_column = ema_two_column
        min_value = ema_two
    else:
        raise ValueError("EMA values are equal")
    data = df.copy()
    data['take_profit'] = 0.00
    data['stop_price'] = 0.00
    data['stop_loss'] = 0.00
    #Iterate through the dataframe and build signals
    for i in range(len(data)):
        if i <= min_value:
            continue
        else:
            if data.loc[i, 'ema_cross']:
                #determine if this is a green candle
                if data.loc[i,'open'] < data.loc[i,'close']:
                    # This is a green candle
                    stop_loss = data.loc[i, ema_column] # stop loss is the larger of the two ema's (200 in this case)
                    stop_price = data.loc[i, 'high']
                    distance = stop_price - stop_loss
                    take_profit = stop_price + distance
                # if the row is not green, it is green
                else:
                    # stop loss = column of largest ema
                    stop_loss = data.loc[i, ema_column]
                    stop_price = data.loc[i, 'low']
                    distance = stop_loss - stop_price
                    take_profit = stop_price - distance
                # Add the calculated columns back to data
                data.loc[i, 'stop_loss'] = stop_loss
                data.loc[i, 'stop_price'] = stop_price
                data.loc[i, 'take_profit'] = take_profit
    return data

def calc_indicators(df, ema_one, ema_two):
    """
    Function to calculate the indicators for the ema cross strategy
    :param df: dataframe
    :param ema_one: size of ema 1
    :param ema_two: size of ema 2
    :return: dataframe with updated columns
    """

    df = indicator_lib.calc_custom_ema(df, ema_one)
    df = indicator_lib.calc_custom_ema(df, ema_two)

    #calculate ema_cross
    df = indicator_lib.ema_cross_calc(df, ema_one, ema_two)
    return df

def get_data(symbol, timeframe):
    """
    Function used to retrieve data
    :param symbol: symbol to be queried
    :param timeframe: timeframe for which the symbol will be queried
    :return:
    """

    df = mt5_lib.get_candles_data(symbol, timeframe, 1000)

    return df