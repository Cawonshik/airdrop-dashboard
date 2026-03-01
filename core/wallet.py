import requests

RPC = {
    "eth": "https://rpc.ankr.com/eth",
    "bsc": "https://rpc.ankr.com/bsc",
    "polygon": "https://rpc.ankr.com/polygon",
    "base": "https://rpc.ankr.com/base",
    "arbitrum": "https://rpc.ankr.com/arbitrum",
    "optimism": "https://rpc.ankr.com/optimism"
}

PRICE = {
    "eth": 3000,
    "bsc": 300,
    "polygon": 1,
    "base": 3000,
    "arbitrum": 3000,
    "optimism": 3000
}

def get_balance(chain, wallet):
    try:
        if chain not in RPC:
            return 0, 0

        payload = {
            "jsonrpc": "2.0",
            "method": "eth_getBalance",
            "params": [wallet, "latest"],
            "id": 1
        }

        res = requests.post(RPC[chain], json=payload).json()
        wei = int(res["result"], 16)

        coin = wei / 1e18
        usd = coin * PRICE.get(chain, 0)

        return round(coin, 5), round(usd, 2)

    except:
        return 0, 0