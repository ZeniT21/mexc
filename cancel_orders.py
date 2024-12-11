
import pickle
import time
from buy import cancel_order, make_order_sell_limit, make_order
import requests
from pymexc import spot, futures
import json
from config import cookie_get, ACCOUNT, TIME_ON_LIMIT_ORDER, SECOND_LIMIT_ORDER, LIMIT_DOWN_CHANGE, api_key, api_secret, redis_client, tg



http_spot_client = spot.HTTP(api_key=api_key, api_secret=api_secret)



def sell_if_old_limit_onsell(cookies):
    data = requests.get(
        "https://www.mexc.com/api/platform/spot/order/current/orders/v2?orderTypes=1%2C2%2C3%2C4%2C5%2C100%2C101%2C102&pageNum=1&pageSize=100&states=0%2C1%2C3",
        cookies=cookies).json()
    for d in data["data"]["resultList"]:
        if (time.time() - (float(d["createTime"]) / 1000)) > SECOND_LIMIT_ORDER:
            cancel_order(cookies, d["id"])
            answer = make_order_sell_limit(cookies, float(d["price"]) - float(d["price"]) * LIMIT_DOWN_CHANGE,
                                           d["quantity"],
                                           "SELL", d["currencyId"])
            if 'data' in answer:
                tg(f"Лимитка стоит больше {SECOND_LIMIT_ORDER} секунд у {d['currency']}\nПереставляем ее на - {LIMIT_DOWN_CHANGE * 100}% ")

        time.sleep(0.1)


def cancel_order_on_buy(cookies):
    for key in redis_client.scan_iter("sub_mexc_order_*"):
        try:
            data = pickle.loads(redis_client.get(key))
            if data["cancel_limit_buy"] == 0:
                if time.time() - int(data["timestamp"]) / 1000 > TIME_ON_LIMIT_ORDER:

                    print(f"После установки лимитики прошло большее {TIME_ON_LIMIT_ORDER} сек отменяем!")
                    resp = cancel_order(cookies, data["order_id"])

                    print(resp)
                    print(data)
                    if resp["code"] == 200:
                        print("Cancelling order {}".format(key))
                        if cnt := sell_if_order_notfullcomplited2(data["ticker"]):
                            make_order_sell_limit(cookies, float(data["buyprice"]) + float(data["buyprice"]) * 0.01,
                                                  cnt, "SELL", data["currencyid"])
                            tg(f"Ставим заявку на продажу, частично закупленного {data['ticker']} {cnt}шт по {float(data['buyprice']) + float(data['buyprice']) * 0.01}")
                        data["cancel_limit_buy"] = 1
                        redis_client.set(key, pickle.dumps(data), ex=3600)

        except Exception as e:
            print(e)
            # redis.delete(key)
        time.sleep(0.1)


def sell_if_order_notfullcomplited2(ticker):
    free = 0
    for balance in http_spot_client.account_information()['balances']:
        if balance["asset"] == ticker.replace("USDT", ""):
            free = float(balance['free'])
    return free


def sell_if_order_notfullcomplited(cookies):
    for key in redis_client.scan_iter("sub_mexc_order_*"):
        try:
            data = redis_client.get(key)
            if data:

                data = pickle.loads(data)

                currency_id = data["currencyid"]
                buy_price = float(data["buyprice"])
                data_req = requests.get(
                    f"https://www.mexc.com/api/platform/spot/asset/currency/balances?coinId={currency_id}",
                    cookies=cookies).json()

                for d in data_req["data"]:

                    try:
                        if d["available"] != '0' and (time.time() - (float(data["timestamp"]) / 1000) > 120):
                            print("Продаем из депо бумагу в ноль +0.5 если не купили всю позу")
                            print(make_order_sell_limit(cookies, buy_price + buy_price * 0.005, d["available"], "SELL",
                                                        d["vcoinId"]))
                            time.sleep(1)
                    except Exception as e:
                        print(e)
                        continue
        except Exception as e:
            print(e)


while True:
    cookie_account = cookie_get(ACCOUNT)
    time.sleep(1)
    # sell_if_order_notfullcomplited(cookie_account)
    time.sleep(1)
    cancel_order_on_buy(cookie_account)
    time.sleep(1)
    sell_if_old_limit_onsell(cookie_account)

    time.sleep(5)

