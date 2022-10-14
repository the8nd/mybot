import web3
from web3 import Web3
from main import get_price
from abi_links_contracts import *


# Функция отвечающая за проверку баланса в сети арбитрума
async def arb_checker(addresses: list):
    web3 = Web3(Web3.HTTPProvider(arb_link))
    addresses = addresses.split('\n')
    contract_usdt_arb = web3.eth.contract(address=usdt_arb, abi=usdt_arb_abi)
    price_dollar = await get_price('ETH', 'BUSD')
    arb_result = []
    for i in range(len(addresses)):
        try:
            address = web3.toChecksumAddress(addresses[i])
            balance = web3.eth.get_balance(address)
            balance = web3.fromWei(balance, 'ether')
            balance_arb_usdt = contract_usdt_arb.functions.balanceOf(address).call()
            balance_arb_usdt = web3.fromWei(balance_arb_usdt, 'ether')
            balance_eth_in_busd = float(balance) * float(price_dollar['price'])
            arb_result.append(f"{address}\n{'%.3f' % balance} ETH ~ {'%.2f' % balance_eth_in_busd}$\n{'%2.f' % balance_arb_usdt} USDT")
        except Exception:
            arb_result.append(f"{address} - адрес некорректен")
    return arb_result


# Функция отвечает за проверку баланса в сети смартчейн
async def bsc_cheker(addresses: list):
    address = ''
    web3 = Web3(Web3.HTTPProvider(bsc_link))
    addresses = addresses.split('\n')
    contract_busd = web3.eth.contract(address=busd_bsc, abi=busd_bsc_abi)
    contract_usdt_bsc = web3.eth.contract(address=usdt_bsc, abi=usdt_bsc_abi)
    contract_twt = web3.eth.contract(address=twt_bsc, abi=twt_bsc_abi)
    contract_cake = web3.eth.contract(address=cake_bsc, abi=cake_bsc_abi)
    price_dollar_bnb = await get_price('BNB', 'BUSD')
    price_dollar_twt = await get_price('TWT', 'BUSD')
    price_dollar_cake = await get_price('CAKE', 'BUSD')
    bsc_result = []
    for i in range(len(addresses)):
        try:
            address = web3.toChecksumAddress(addresses[i])
            balance = web3.eth.get_balance(address)
            balance = web3.fromWei(balance, 'ether')
            balance_busd = contract_busd.functions.balanceOf(address).call()
            balance_busd = web3.fromWei(balance_busd, 'ether')
            balance_usdt = contract_usdt_bsc.functions.balanceOf(address).call()
            balance_usdt = web3.fromWei(balance_usdt, 'ether')
            balance_twt = contract_twt.functions.balanceOf(address).call()
            balance_twt = web3.fromWei(balance_twt, 'ether')
            balance_cake = contract_cake.functions.balanceOf(address).call()
            balance_cake = web3.fromWei(balance_cake, 'ether')
            balance_bnb_in_busd = float(balance) * float(price_dollar_bnb['price'])
            balance_twt_in_busd = float(balance_twt) * float(price_dollar_twt['price'])
            balance_cake_in_busd = float(balance_cake) * float(price_dollar_cake['price'])
            bsc_result.append(f"{address}\n{'%.3f' % balance}BNB ~ {'%.2f' % balance_bnb_in_busd}$\n{'%2.f' % balance_busd} BUSD\n{balance_usdt} USDT\n{'%2.f' % balance_twt} TWT ~ {'%.2f' % balance_twt_in_busd}\n{'%2.f' % balance_cake} Cake ~ {'%.2f' % balance_cake_in_busd}")
        except Exception:
            bsc_result.append(f"{address} - адрес некорректен")

    return bsc_result


async def eth_checker(addresses: list):
    address = ''
    web3 = Web3(Web3.HTTPProvider(ethereum_link))
    addresses = addresses.split('\n')
    contract_usdt = web3.eth.contract(address=usdt_eth, abi=usdt_eth_abi)
    price_dollar_eth = await get_price('ETH', 'USDT')
    eth_result = []
    for i in range(len(addresses)):
        try:
            address = web3.toChecksumAddress(addresses[i])
            balance = web3.eth.get_balance(address)
            balance = web3.fromWei(balance, 'ether')
            balance_usdt = contract_usdt.functions.balanceOf(address).call()
            balance_usdt = web3.fromWei(balance_usdt, 'ether')
            balance_eth_in_usdt = float(balance) * float(price_dollar_eth['price'])
            eth_result.append(f"{address}\n{round(balance, 3)} ETH ~ {round(balance_eth_in_usdt, 2)}$\n{round(balance_usdt, 2)} USDT")

        except Exception:
            eth_result.append(f"{address} - адрес некорректен")
    return eth_result


async def pol_checker(addresses: list):
    address = ''
    web3 = Web3(Web3.HTTPProvider(polygon_link))
    addresses = addresses.split('\n')
    contract_weth = web3.eth.contract(address=weth_pol, abi=weth_pol_abi)
    price_dollar_weth = await get_price('ETH', 'USDT')
    price_dollar_matic = await get_price('MATIC', 'USDT')
    pol_result = []
    for i in range(len(addresses)):
        try:
            address = web3.toChecksumAddress(addresses[i])
            balance = web3.eth.get_balance(address)
            balance = web3.fromWei(balance, 'ether')
            balance_weth = contract_weth.functions.balanceOf(address).call()
            balance_weth = web3.fromWei(balance_weth, 'ether')
            balance_weth_in_usdt = float(balance_weth) * float(price_dollar_weth['price'])
            balance_in_usdt = float(balance) * float(price_dollar_matic['price'])
            pol_result.append(f"{address}\n{round(balance, 3)} MATIC ~ {round(balance_in_usdt, 2)}$\n{round(balance_weth, 3)} wETH ~ {round(balance_weth_in_usdt, 2)}$")
        except Exception:
            pol_result.append(f"{address} - адрес некорректен")
    return pol_result


# Удалить или скрыть после тестов
async def test_cheker(addresses: list):
    address = ''
    web3 = Web3(Web3.HTTPProvider(test_link))
    addresses = addresses.split('\n')
    test_result = []
    for i in range(len(addresses)):
        try:
            address = web3.toChecksumAddress(addresses[i])
            balance = web3.eth.get_balance(address)
            balance = web3.fromWei(balance, 'ether')
            test_result.append(f"{address}\n{round(balance, 3)} BNB")
            print('add adds')
        except Exception:
            test_result.append(f"{address} - адрес некорректен")

    return test_result