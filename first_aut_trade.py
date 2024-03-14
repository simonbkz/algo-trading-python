import json
import os
import pandas as pd
import numpy as np
import torch
from sklearn.preprocessing import MinMaxScaler
pd.set_option('display.max_columns',None)
import matplotlib.pyplot as plt
import torch
import torch.nn as nn
import torch.utils.data as data

# Custom libraries
import mt5_lib
import indicator_lib
import ema_cross_strategy
import plot_helper

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

def create_dataset(dataset, seq_len):
    """Transform a time series into a prediction dataset
    Args:
        dataset: A numpy array of time series, first dimension is the time steps
        seq_len: Size of window for prediction
    """
    X, y = [], []
    for i in range(len(dataset) - seq_len):
        feature = dataset[i:i + seq_len]
        target = dataset[i + seq_len]
        X.append(feature)
        y.append(target)
    return torch.tensor(X), torch.tensor(y)

class Model(nn.Module):
    def __init__(self, input_size, hidden_size):
        super().__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, batch_first=True)
        self.fc = nn.Linear(hidden_size, 1)
    def forward(self, x):
        output, (hidden, cell) = self.lstm(x)
        return self.fc(output[:, -1, :])


if __name__ == '__main__':

    settings = get_project_settings(import_file_path)
    startup = start_up(settings)
    symbols = settings['mt5']['symbols']
    timeframe = settings['mt5']['timeframe'] # we will focus on one timeframe for now, please ensure you only have one time frame in the .json file
    for symbol in symbols:
        #retrieve data for each candle
        df = mt5_lib.get_candles_data(symbol=symbol, timeframe=timeframe, number_of_candles=10000)
        out = ema_cross_strategy.ema_cross_strategy(symbol, timeframe, ema_one=50, ema_two= 200,balance=10000,amount_to_risk=0.01)
        # print(f"ema cross signal: {df}")
        # print(f"final dataframe snapshot: {df.head()}")
        close_prices = df['close']
        timeseries = df[["close"]].values.astype('float32')
        timeseries_len = close_prices.shape[0]
        # print(close_prices)
        # train_x_list = list(close_prices)[:8000]
        # test_y_list = list(close_prices)[-2000:]

        train_size = int(len(timeseries) * 0.67)
        test_size = len(timeseries) - train_size
        train, test = timeseries[:train_size], timeseries[train_size:]

        seq_len = 15
        train_x, train_y = create_dataset(train, seq_len)
        test_x, test_y = create_dataset(test, seq_len)

        model = Model(1, 96)
        optimizer = torch.optim.Adam(model.parameters())
        loss_fn = nn.MSELoss()
        loader = data.DataLoader(data.TensorDataset(train_x, train_y), shuffle=True, batch_size=8)

        n_epochs = 10
        for epoch in range(n_epochs):
            model.train(True)
            for x_batch, y_batch in loader:

                output = model(x_batch)
                loss = loss_fn(output, y_batch)

                optimizer.zero_grad()
                loss.backward()
                optimizer.step() #adjust weights
        # # Validation
            if epoch % 10 and epoch != 0:
                print(epoch, "epoch loss", loss.detach().numpy())
            model.eval()
            with torch.no_grad():
                output = model(test_x)
                output_train = model(train_x)
                test_rmse = np.sqrt(loss_fn(output, test_y))
                train_rmse = np.sqrt(loss_fn(output_train, train_y))
                print("Epoch %d: train RMSE %.4f, test RMSE %.4f" % (epoch, train_rmse, test_rmse))

        with torch.no_grad():
            model.train(False)
            # shift train predictions for plotting
            train_plot = np.ones_like(timeseries) * np.nan
            y_pred = model(train_x)
            y_pred = y_pred[:, -1]
            train_plot[seq_len:train_size] = model(train_x)
            # shift test predictions for plotting
            test_plot = np.ones_like(timeseries) * np.nan
            test_plot[train_size + seq_len:len(timeseries)] = model(test_x)
        # plot
        plt.plot(timeseries)
        plt.plot(train_plot, c='r')
        plt.plot(test_plot, c='g')
        plt.show()

        # mm = MinMaxScaler()
        # scaled_train_prices = mm.fit_transform(np.array(train_x_list)[..., None]).squeeze()
        # scaled_test_prices = mm.fit_transform(np.array(test_y_list)[..., None]).squeeze()
        # # print(scaled_prices)
        # X = []
        # X_test = []
        # y = []
        # y_test = []

        # for i in range(len(scaled_train_prices) - seq_len):
        #     X.append(scaled_train_prices[i: i + seq_len])
        #     y.append(scaled_train_prices[i+seq_len])
        #
        # for j in range(len(scaled_test_prices) - seq_len):
        #     X_test.append(scaled_test_prices[j: j + seq_len])
        #     y_test.append(scaled_test_prices[j+seq_len])
        #
        # X = np.array(X)[..., None]
        # X_test = np.array(X_test)[..., None]
        # y = np.array(y)[..., None]
        # y_test = np.array(y_test)[..., None]
        #
        # train_x = torch.from_numpy(X[:int(X.shape[0])]).float()
        # train_y = torch.from_numpy(y[:int(X.shape[0])]).float()
        #
        # test_x = torch.from_numpy(X_test[:int(X_test.shape[0])]).float()
        # test_y = torch.from_numpy(y_test[:int(X_test.shape[0])]).float()

        # model = Model(1, 96)
        #
        # optimizer = torch.optim.Adam(model.parameters(), lr = 0.001)
        # loss_fn = nn.MSELoss()
        #
        # num_epochs = 100
        # for epoch in range(num_epochs):
        #     output = model(train_x)
        #     loss = loss_fn(output, train_y)
        #
        #     optimizer.zero_grad()
        #     loss.backward()
        #     optimizer.step() #adjust weights
        #
        #     if epoch % 10 and epoch != 0:
        #         print(epoch, "epoch loss", loss.detach().numpy())
        #     with torch.no_grad():
        #         output = model(test_x)
        #         output_train = model(train_x)
        #         test_rmse = np.sqrt(loss_fn(output, test_y))
        #         train_rmse = np.sqrt(loss_fn(output_train, train_y))
        #         print("Epoch %d: train RMSE %.4f, test RMSE %.4f" % (epoch, train_rmse, test_rmse))
        #
        # model.eval()
        # train_size = train_y.shape[0]
        # with torch.no_grad():
        #     train_plot = np.ones_like(timeseries) * np.nan
        #     y_pred = model(train_x)
        #     train_plot[seq_len:train_size] = model(train_x)
        #     test_plot = np.ones_like(timeseries) * np.nan
        #     test_plot[train_size + seq_len:len(timeseries)] = model(test_x)
        #
        #     # output = model(test_x)
        #     # test_plot[train_size + seq_len:len(timeseries_len)] = model(test_x)[:, -1, :]
        #
        # # plot
        # plt.plot(timeseries)
        # plt.plot(train_plot, c='r')
        # plt.plot(test_plot, c='g')
        # plt.show()

        # pred = mm.inverse_transform(output.numpy())
        # actual = mm.inverse_transform(test_y.numpy())
        #
        # plt.plot(pred.squeeze(), color = 'red', label = 'predicted')
        # plt.plot(actual.squeeze(), color = 'green', label = 'actual')
        # plt.show()
        # print(train_x.shape, test_x.shape)


        # fig, (ax1, ax2) = plt.subplots(2,1, figsize=(5,7))
        # df.reset_index(inplace=True)
        # out_open = plot_helper.my_plotter(ax1,df['time'],df['open'], {'color':'r'})
        # out_close = plot_helper.my_plotter(ax1, df['time'], df['close'], {'color': 'b'})
        # out_spread = plot_helper.my_plotter(ax2, df['time'], df['spread'], {'color': 'g'})
        # # close_prices = plot_helper.my_plotter(ax2, df['index'], df['close'], {'marker':'o'})
        # plt.show()
