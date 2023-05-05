import os
import sys
from pywallet import wallet
import seed_create
from requests import get
import certifi
import threading
import time
import threading


ENDPOINTS = {
    "bitcore": "https://api.bitcore.io/api/BTC/mainnet/address/{address}/balance",
    #"haskoin": "https://api.haskoin.com/btc/address/balances?addresses={address}",
    "chain.api.btc": "https://chain.api.btc.com/v3/address/{address}",
    #"api-r.bitcoinchain.com": "https://api-r.bitcoinchain.com/v1/address/{address}",
    "chainflyer.bitflyer.jp": "https://chainflyer.bitflyer.jp/v1/address/{address}",
    "api.blockcypher.com": "https://api.blockcypher.com/v1/btc/main/addrs/{address}/",
    #"multiexplorer.com": "https://multiexplorer.com/api/address_balance/private5?addresses={address}&currency=btc",
    #"blockchain.info4": "https://blockchain.info/balance?active={address}"
}


def get_balance(provider, endpoint, address: str) -> int:
    endpointUrl = endpoint.format(address=address)
    try:
        response = get(endpointUrl, timeout=10, verify=pathCertificate)
        if response.status_code != 200:
            print(
                "Status code response: "
                + str(response.status_code)
                + " from "
                + provider
            )
            time.sleep(10)
            return -1

        response = response.json()
        balance = switch(provider, response, address)
        return balance

    except Exception as e:
        print("Exception on get_balance with " + provider + ": ", e)
        return -1
    


def switch(provider, json, address):

    if provider == "api.blockcypher.com":
        return json["final_balance"]
    elif provider == "haskoin":
        return json[0]["confirmed"]
    elif provider == "bitcore":
        return max(json["balance"], json["confirmed"]) 
    elif provider == "chain.api.btc":
        return json["data"]["balance"]
    elif provider == "api-r.bitcoinchain.com":
        if len(json[0]) == 0: #[{}]
            return 0
        return json[0]["balance"]
    elif provider == "chainflyer.bitflyer.jp":
        return max(json["unconfirmed_balance"], json["confirmed_balance"])
    elif provider == "multiexplorer.com":
        return json["balance"]["total_balance"]
    elif provider == "blockchain.info4":
        return json[address]["final_balance"]


def task(provider, endpoint):
    global count
    while True:

        #Generation seed list
        seedList = seed_create.getRandomSeedList()

        for seed in seedList:
            with threadLock:
                count+=1
            # print(seed)
            #Create wallet with current seed
            wallets = wallet.create_wallet(network="btc", seed=seed, children=0)
            address = wallets["address"]
            balance = get_balance(provider, endpoint, address)
            if balance != -1 and balance!=0.00000000000000000:
                with open("found.csv", "a") as f:
                    f.write(
                        seed
                        + ","
                        + str(balance)
                        + ","
                        + wallets["address"]
                        + ","
                        + wallets["private_key"]
                        + "\n"
                    )

def restart():
    print("RESTART")
    os.execv(sys.executable, ['python'] + sys.argv)

nThread = 4  # limits 4, choice between [0,3]
pathCertificate = certifi.where()
count=0
threadLock = threading.Lock()
start=(time.time())
time.sleep(1)

for i, threadNumber in enumerate(ENDPOINTS.items()):
    if i == nThread:
        break
    thread = threading.Thread(target=task, args=(threadNumber[0], threadNumber[1]))
    print(
        "Start thread "
        + str(i)
        + " with "
        + threadNumber[0]
        + " and "
        + threadNumber[1]
    )
    thread.start()

while True:
    print("Processed: "+str(count))
    partial=(time.time())
    print("Pass "+str(partial-start)+" seconds from start")
    print("Address checked in one second: "+str(count/(partial-start)))
    if count>10000:
        restart()
    time.sleep(30)


