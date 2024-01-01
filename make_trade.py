import helper_function
import mt5_lib

def make_trade(balance, comment, amount_to_risk, symbol, take_profit, stop_loss, stop_price):
    """
    Function to make a trade once a signal has been found
    :param balance: float of current balance / static balance
    :param comment: string of comment. Used to denote different strategies
    :param amount_to_risk: float of amount to risk
    :param symbol: string of the symbol being tested
    :param take_profit: float of take profit
    :param stop_loss: float of stop loss
    :param stop_price: float of stop price
    :return: trade outcome
    """
    ### pseudo code
    # step  1: Format all values
    # step 2: Determine the lot sizes
    # step 3: send trade to MT5
    # step 4: return outcome
    # step 5: send trade outcome / signal to discord
    # step 6: account for different currencies in balance (i.e. AUD dollar to USD when trading USDJPY)

    #formating the values
    balance = float(balance)
    balance = round(balance, 2)
    take_profit = float(take_profit)
    take_profit = round(take_profit, 4)
    stop_loss = float(stop_loss)
    stop_loss = round(stop_loss, 4)
    stop_price = float(stop_price)
    stop_price = round(stop_price, 4)

    # step 2: Determine lot size
    lot_size = helper_function.calc_lot_size(balance,amount_to_risk,stop_loss,stop_price,symbol)

    #step 3: send trade to MetaTrader 5
    if stop_price > stop_loss:
        trade_type = "BUY_STOP"
    else:
        trade_type = "SELL_STOP"

    trade_outcome = mt5_lib.place_order(order_type=trade_type,symbol=symbol,
                                        volume=lot_size,stop_loss=stop_loss,
                                        take_profit=take_profit,comment=comment,
                                        stop_price=stop_price,direct=False)
    #step 4: return outcome
    return trade_outcome