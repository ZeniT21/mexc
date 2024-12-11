import requests
import time
from datetime import datetime
import pickle
from config import TIME_ON_BUY_ONE_COIN, redis_client, tg


def make_order(cookies, account, price, quantity, type_, change, price_o, price_c, ticker_, currencyId):
    marketCurrencyId = "128f589271cb4951b03e71e6323eb7be"
    _timestamp = time.time()

    profitTriggerPrice = price + price * (abs(change) / 2 / 100)
    loseTriggerPrice = price - price * 0.12

    price = format(price, ".10f")
    change = format(change, ".10f")

    profitTriggerPrice = format(profitTriggerPrice, ".10f")

    loseTriggerPrice = format(loseTriggerPrice, ".10f")

    json_data = {
        'currencyId': currencyId,
        'marketCurrencyId': marketCurrencyId,
        'tradeType': type_,
        'price': price,
        'quantity': quantity,
        'profitTriggerPrice': profitTriggerPrice,
        # 'loseTriggerPrice': loseTriggerPrice,
        'orderType': 'LIMIT_ORDER',
        # 'mtoken': cookies["mexc_fingerprint_visitorId"],

        # 'mhash': 'c667374fa18b54c207fd7a586bd99895',
    }

    # print("СТАВИМ ЛИМИТКУ:")
    # print(datetime.today().strftime('%d.%m.%Y %H:%M:%S.%f'))
    response = requests.post(
        'https://www.mexc.com/api/platform/spot/order/place',
        # params=params,
        cookies=cookies,
        json=json_data,

    )

    data = response.json()

    if 'data' in data:
        print(_timestamp - time.time())
        print(
            f"LIMIT ORDER!\nprice: {price}\nquantity: {quantity}\nprofitTriggerPrice: {profitTriggerPrice}\nloseTriggerPrice: {loseTriggerPrice}\n PriceO: {price_o} PriceClose: {price_c}")

        redis_client.set(f"sub_in_depo_{ticker_}_{account}", 1,
                  TIME_ON_BUY_ONE_COIN)  # если затарили не тарим 60 секунд чтобы нож не взять на все депо
        redis_client.set(f"sub_mexc_order_{data['data']}", pickle.dumps(
            {"order_id": data["data"], "timestamp": data["timestamp"], "currencyid": currencyId, "buyprice": price,
             "cancel_limit_buy": 0, "ticker": ticker_}), 90000)  # для отмены лимитки через 30 сек
        tg(f"https://www.mexc.com/ru-RU/exchange/{ticker_.replace('USDT', '_USDT')}\nПросадка: {change}%\nЛимитка на {price}")
        # redis.set(f"mexc_cancel_profit_{currencyId}", pickle.dumps({"currency_id": currencyId, "order_id": data["data"], "timestamp": data["timestamp"]}))

        # requests.delete(f"https://www.mexc.com/api/platform/spot/order/cancel/v2?orderId={order_id}", cookies=cookies)
        # time.sleep(1)
        # requests.delete(f"https://www.mexc.com/api/platform/spot/order/cancel/v2?orderId={order_id}", cookies=cookies,
        #                 headers=headers)
    return


def cancel_order(cookies, order_id):
    print(order_id)
    return requests.delete(f"https://www.mexc.com/api/platform/spot/order/cancel/v2?orderId={order_id}",
                           cookies=cookies).json()


def make_order_sell_limit(cookies, price, quantity, type_, currencyId):
    marketCurrencyId = "128f589271cb4951b03e71e6323eb7be"

    _timestamp = time.time()

    print("Попытка Поставить лимитку на продажу")
    print(price)
    price = format(float(price), ".10f")

    json_data = {
        'currencyId': currencyId,
        'marketCurrencyId': marketCurrencyId,
        'tradeType': type_,
        'price': price,
        'quantity': quantity,

        'orderType': 'LIMIT_ORDER',

        # 'mtoken': cookies["mexc_fingerprint_visitorId"],

        # 'mhash': 'c667374fa18b54c207fd7a586bd99895',
    }
    print(''
          ''
          ''
          ''
          '')
    print(datetime.today().strftime('%d.%m.%Y %H:%M:%S.%f'))

    # print("СТАВИМ ЛИМИТКУ:")
    # print(datetime.today().strftime('%d.%m.%Y %H:%M:%S.%f'))
    response = requests.post(
        'https://www.mexc.com/api/platform/spot/order/place?mh=12ab395285f3c73c9b5c9630f6655920',

        cookies=cookies,
        json=json_data,

    )

    print(datetime.today().strftime('%d.%m.%Y %H:%M:%S.%f'))
    print(_timestamp - time.time())

    data = response.json()
    print(data)
    if 'data' in data:
        print(_timestamp - time.time())
        # tg(f"LIMIT ORDER!\nprice: {price}\nquantity: {quantity}\nprofitTriggerPrice: {abs(price + price * (change / 2 / 100))}\nloseTriggerPrice: {price - price * 0.1}")

        # redis.set(f"mexc_cancel_profit_{currencyId}", pickle.dumps({"currency_id": currencyId, "order_id": data["data"], "timestamp": data["timestamp"]}))

        # requests.delete(f"https://www.mexc.com/api/platform/spot/order/cancel/v2?orderId={order_id}", cookies=cookies)
        # time.sleep(1)
        # requests.delete(f"https://www.mexc.com/api/platform/spot/order/cancel/v2?orderId={order_id}", cookies=cookies,
        #                 headers=headers)
    return data