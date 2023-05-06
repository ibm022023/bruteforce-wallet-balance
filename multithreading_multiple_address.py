import os
import sys
from pywallet import wallet
from seed_create import getRandomSeedListWithSize
from requests import get
import certifi
import threading
import time
import threading
import tracemalloc
import gc



MULTIPLE_ADDRESS_ENDPOINT = {
    "api.haskoin.com": [
        "https://api.haskoin.com/btc/address/balances?addresses=",
        232,
    ],  # max 232 wallet
    "api-r.bitcoinchain.com": [
        "https://api-r.bitcoinchain.com/v1/address/",
        100,
    ],  # max 100 wallet
    "blockchain.info": ["https://blockchain.info/balance?active=", 465],  # max 465
}


def parse_url(endpoint: str, addressList):
    first = True
    for i, address in enumerate(addressList):
        if first:
            first = False
        else:
            endpoint += ","
        endpoint += address
    return endpoint


def get_balance(
    provider: str, addressList: list[str], recursive=False):
    endpoint=MULTIPLE_ADDRESS_ENDPOINT.get(provider)[0]
    endpointUrl = parse_url(endpoint, addressList)
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
            if not recursive:
                print("Recursive with " + provider)
                return get_balance(provider, endpoint, addressList, True)
            return [-1 for _ in range(len(addressList))]

        response = response.json()
        balance = switch(provider, response, addressList)
        return balance

    except Exception as e:
        print("Exception on get_balance with " + provider + ": ", e)
        return [-1 for _ in range(len(addressList))]


def switch(provider: str, json, addressList):
    """
    Given the endfpoint provider, the json response, and the addresses, it try to find the balance of each address in the json response
    @return the balance
    """
    balance = []
    assert(len(json) == MULTIPLE_ADDRESS_ENDPOINT.get(provider)[1])
    if provider == "haskoin":
        for i in range(len(json)): 
            balance.append(json[i]["confirmed"])

    elif provider == "api-r.bitcoinchain.com":
        for i in range(len(json)):
            try:
                balance.append(json[i]["balance"])
            except:
                balance.append(0)

    elif provider == "blockchain.info4":
        for i in range(len(json)):
            balance.append(json[addressList[i]]["final_balance"])

    return balance

def createWalletListFromSeedList(seedList):
    walletsList = []
    for seed in seedList:
        assert (type(seed) == str)
        walletData = wallet.create_wallet(network="btc", seed=seed,children=0)
        walletsList.append(walletData)
    return walletsList

def task(provider: str):
    global count
    nAddress=MULTIPLE_ADDRESS_ENDPOINT.get(provider)[1]
    while True:
        seedList = getRandomSeedListWithSize(nAddress)
        walletsList=createWalletListFromSeedList(seedList)
        addressList = [wallet["address"] for wallet in walletsList]
        balanceList = get_balance(provider, addressList)


        for i, balance in enumerate(balanceList):
            if balance != -1 and balance != 0.00000000000000000:
                with open("found_with_multiple_addresses.csv", "a") as f:
                    f.write(
                        seedList[i]
                        + ","
                        + str(balance)
                        + ","
                        + walletsList[i]["address"]
                        + ","
                        + walletsList[i]["private_key"]
                        + "\n"
                    )
        with threadLock:
            count += nAddress
        
def restart():
    print("RESTART")
    os.execv(sys.executable, ['python'] + sys.argv)


nThread = 3
pathCertificate = certifi.where()
count = 0
threadLock = threading.Lock()
start = time.time()
time.sleep(1)
gc.enable()
tracemalloc.start()


for i, threadNumber in enumerate(MULTIPLE_ADDRESS_ENDPOINT.items()):
    if i == nThread:
        break
    thread = threading.Thread(
        target=task, args=([threadNumber[0]])
    )
    print(
        "Start thread "
        + str(i)
        + " with "
        + threadNumber[0]
        + " and url "
        + threadNumber[1][0]
        + " and  max address "
        + str(threadNumber[1][1])
    )
    thread.start()

print("\n")
while True:
    print("Proccessed " + str(count)+" addresses")
    partial = time.time()
    print("Elapsed " + str(int(partial - start)) + " seconds from start")
    print("Mean address checked in one second: " + str(count / (partial - start)))
    print("Current memory usage:",str(round(tracemalloc.get_traced_memory()[0]/1024/1024)))
    if tracemalloc.get_traced_memory()[0]>350*1024*1024:
        print("Memory usage exceeded 350MB")
        restart()
    time.sleep(60)






