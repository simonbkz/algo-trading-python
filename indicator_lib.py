import numpy as np


def calc_custom_ema(df, ema_size):

    ema_name = "ema_"+str(ema_size)
    multiplier = 2 / (ema_size + 1)
    initial_mean = df['close'].head(ema_size).mean()

    for i in range(len(df)):
        if i == ema_size:
            df.loc[i,ema_name] = initial_mean
        elif i > ema_size:
            ema_value = df.loc[i,'close'] * multiplier + df.loc[i-1,ema_name] * (1 - multiplier)
            df.loc[i,ema_name] = ema_value
        else:
            df.loc[i,ema_name] = 0.00
    return df

def ema_cross_calc(df, ema_one, ema_two):
    """
    Function to calculate ema cross event.
    :param df: dataframe object
    :param ema_one: integer of ema 1 size
    :param ema_two: integer of ema 2 size
    :return: dataframe with cross events
    """
    #Get the column names
    ema_one_column = "ema_"+str(ema_one)
    ema_two_column = "ema_"+str(ema_two)
    df['position'] = df[ema_one_column] > df[ema_two_column]
    df['pre_position'] = df['position'].shift(1)
    df.dropna(inplace=True)
    df['ema_cross'] = np.where(df['position'] == df['pre_position'],False, True)
    df.drop(['position','pre_position'], axis=1, inplace = True)
    return df
