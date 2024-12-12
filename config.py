import json
import requests
import redis


api_key = "mx0vgldJMn0c8ATpmD"
api_secret = "208c9eea4ae040faad16c283b4064ade"


redis_client = redis.Redis(host='localhost', port=6379, db=0)


TICKERS = ['NEIUSDT','BRISEUSDT','MCOINUSDT','ASTUSDT','PHILUSDT','UNPUSDT','ALUUSDT','3ULLUSDT','ORNJUSDT','PALMAIUSDT','SVNUSDT','OPTIMUSUSDT','WORKUSDT','LCGUSDT','PAIUSDT','ABDSUSDT','NFEUSDT','XFIUSDT','FAKTUSDT','CRTAIUSDT','HNTUSDT','LRTUSDT','FORUSDT','ISLMUSDT','ZNDUSDT','RGOATUSDT','CEBUSDT','VMINTUSDT','TDMUSDT','VSCUSDT','SWCHUSDT','BCCOINUSDT','PAPUUSDT', 'AXOLUSDT']

mexc_pars_tg_coins = []
for key in redis_client.scan_iter("sub_coin_from_pars_*"):
    coin = str(redis_client.get(key).decode('utf-8'))+'USDT'
    mexc_pars_tg_coins.append(coin)

TICKERS += mexc_pars_tg_coins
TICKERS = list(set(TICKERS))

MIN_CHANGE = 1.3 # changed! 0.9- 1.4

MAX_TRADE = 22 # changed! 33 - 20

TIME_ON_BUY_ONE_COIN = 60
TIME_ON_LIMIT_ORDER = 60
SECOND_LIMIT_ORDER = 14400 # if older => set limit -LIMIT_DOWN_CHANGE
LIMIT_DOWN_CHANGE = 0.003 # of old limit set
MAX_SUM_ON_COIN = 66 # changed! 90 - 60

tickers_data = {}
tickers_balance = {}
tickers_drawdown = {}

data = requests.get("https://www.mexc.com/api/platform/spot/market-v2/web/symbols").json()
for ticker_data in data["data"]["USDT"]:
    tickers_data[f'{ticker_data["vn"]}USDT'] = ticker_data["cd"]

ACCOUNT = "cookie.json"

def cookie_get(account):
    with open(account) as f:
        cookies_data = json.load(f)
        cookies = {}
        for cookie in cookies_data:
            cookies[cookie['name']] = cookie['value']
        return cookies


def tg(bot_message):
    data = {'chat_id': -1002424928510, 'text': bot_message}
    send_url = f'https://api.telegram.org/bot1609618970:AAGeY7Ilqh40ngumMX2RImNLnle5Eeb7qJI/sendMessage'
    response = requests.post(send_url, data=data)
    return response.json()