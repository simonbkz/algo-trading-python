import matplotlib.pyplot as plt
import mt5_lib

def plot_values(df, plot_col):
    """
    This function plots a desired column against timestamp in the timeseries data
    :param df:  dataframe
    :param plot_col: this is a column to plot
    :return: this plots a graph
    """
    fig, ax = plt.subplots()
    df.reset_index(inplace=True)
    ax.plot(df['index'],df[plot_col])
    plt.show()
    return df

def my_plotter(ax, col1, col2, param_dict):
    """
    A helper function to make a plot
    :param df1: first column of the dataframe to plot in x-axis
    :param df2: second column of the dataframe to plot in y-axis
    :param param_dict: dictionary containing parameters
    :return:
    """

    out = ax.plot(col1, col2, **param_dict)
    return out