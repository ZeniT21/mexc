from pymexc import spot
import traceback
from buy import make_order

from config import TICKERS, tickers_data, ACCOUNT, cookie_get, MAX_SUM_ON_COIN, TIME_ON_BUY_ONE_COIN, redis_client, api_secret, api_key, tg


http_spot_client = spot.HTTP(api_key=api_key, api_secret=api_secret)


def handle_message(message):
    try:
        if 'kline' in message["c"]:
            if redis_client.get(f"sub_final_change_avg_{message['s']}"):

                change = float(message['d']['k']['c']) * 100 / float(message['d']['k']['o']) - 100

                need_change = float(redis_client.get(f"sub_final_change_avg_{message['s']}")) * -1
                print(message["s"], change, need_change)
                avg_price = float(redis_client.get(f"sub_final_price_avg_{message['s']}"))

                if change < need_change and change > -10 and (avg_price > float(message['d']['k']['c'])):

                    tg(f"https://www.mexc.com/ru-RU/exchange/{message['s'].replace('USDT', '_USDT')}\nПросадка: {change}%, при необходимой средней просадки {need_change}%\nЦена закрытия свечи: {message['d']['k']['c']} при средней цене за 10 мин: {avg_price}")

                    buy_price = float(message['d']['k']['c'])
                    koef = 0.0015
                    if change < -3:
                        koef = 0.008
                    buy_price = buy_price + buy_price * koef

                    # print(f"buy_price {buy_price}")

                    sum_trade = float(redis_client.get(f"sub_sum_trade_avg_{message['s']}"))

                    account_money = 0
                    balance_coin = {}
                    for balance in http_spot_client.account_information()['balances']:
                        if balance["asset"] == "USDT":
                            account_money = float(balance['free'])
                            continue
                        print(f'{balance["asset"]}USDT')
                        balance_coin[f'{balance["asset"]}USDT'] = float(
                            http_spot_client.ticker_price(f'{balance["asset"]}USDT')["price"]) * float(
                            balance["locked"])

                    if message['s'] in balance_coin:
                        if MAX_SUM_ON_COIN < balance_coin[message['s']]:
                            tg(f"Затарено уже более чем на {MAX_SUM_ON_COIN}$ не тарим {message['s']}")
                            return

                    if sum_trade > account_money:
                        sum_trade = account_money - 0.1
                    qty = round(sum_trade / buy_price)

                    if sum_trade > 1:

                        if not redis_client.get(
                                f"sub_in_depo_{message['s']}_{ACCOUNT}"):  # если 60 секунд с тарки прошло тарим!

                            make_order(cookie_get(ACCOUNT), ACCOUNT, buy_price, qty, "BUY", change,
                                       message['d']['k']['o'], message['d']['k']['c'], message['s'],
                                       tickers_data[message['s']])
                        else:
                            tg(f"Не прошло {TIME_ON_BUY_ONE_COIN} сек после втарки {message['s']} не тарим")

    except Exception as e:
        print(traceback.format_exc())
        exit()


ws_spot_client = spot.WebSocket(api_key=api_key, api_secret=api_secret, restart_on_error=True, ping_interval=60,
                                ping_timeout=30)
ws_spot_client2 = spot.WebSocket(api_key=api_key, api_secret=api_secret, restart_on_error=True, ping_interval=60,
                                 ping_timeout=30)

for i, t in enumerate(TICKERS):
    if i % 2 == 0:
        ws_spot_client.kline_stream(handle_message, t, "Min1")
    else:
        ws_spot_client2.kline_stream(handle_message, t, "Min1")

while True:

    if not ws_spot_client.is_connected() or not ws_spot_client2.is_connected():
        exit()

    pass



