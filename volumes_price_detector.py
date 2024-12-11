from pymexc import spot, futures
import time
import statistics

from config import TICKERS, MIN_CHANGE, MAX_TRADE, redis_client, api_secret, api_key


http_spot_client = spot.HTTP(api_key=api_key, api_secret=api_secret)

while True:
    for ticker in TICKERS:

        data_candels_temp = http_spot_client.klines(ticker, "1m")

        data_candels = data_candels_temp[-30:]

        data_candels_data = data_candels_temp[-20:]





        data_trades = http_spot_client.trades(ticker, 30)

        _avg_trade = []
        for trade in data_trades:
            _avg_trade.append(float(trade['qty']) * float(trade['price']))
        avg_trade = statistics.median(_avg_trade)



        counter_candels = 0
        change_sum = []

        final_price_avg = float(http_spot_client.avg_price(ticker)["price"])
        print(final_price_avg)

        for dat in data_candels:

            change = abs(float(dat[4]) * 100 / float(dat[1]) - 100)

            if change > 0.8:

                change_sum.append(change)
        try:
            change_avg = statistics.median(change_sum)
        except:
            change_avg = 9




        if avg_trade > MAX_TRADE:
            avg_trade = MAX_TRADE

        if change_avg < MIN_CHANGE:
            change_avg = MIN_CHANGE




        print(ticker, change_avg, format(final_price_avg, ".10f"))
        redis_client.set(f"sub_sum_trade_avg_{ticker}", avg_trade, 300)
        redis_client.set(f"sub_final_price_avg_{ticker}", format(final_price_avg, ".10f"), 300)
        redis_client.set(f"sub_final_change_avg_{ticker}", change_avg, 300)

        time.sleep(0.1)

    time.sleep(10)