import json


# Файл содержит все нужны ссылки. Контракты, ABI, ссылки на сети.

def read_file(file_name):
    with open(f'abi/{file_name}') as f:
        return json.load(f)


# Ссылки на ноды
arb_link = 'https://arb-mainnet.g.alchemy.com/v2/fwpdYGooLzR3jw8a6YK5HMRbswJWWQmv'  # chain id 42161
bsc_link = 'https://bsc-dataseed.binance.org/'  # chain id 56
polygon_link = 'https://polygon-mainnet.g.alchemy.com/v2/bNT1IhanZMXGDeq1WswvDHS2Vl3kHd4c'  # chain id 137
ethereum_link = 'https://eth-mainnet.g.alchemy.com/v2/TJ_tNX6LRTX7ZAemte6N7LpbR2zWC4VS'  # chain id 1
test_link = 'https://data-seed-prebsc-1-s3.binance.org:8545'

# Контракты/ABI
# Arbitrum
usdt_arb = "0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9"
usdt_arb_abi = read_file('usdt_arb_abi.json')


# Binance Smart Chain
busd_bsc = "0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56"
usdt_bsc = "0x55d398326f99059fF775485246999027B3197955"
twt_bsc = "0x4B0F1812e5Df2A09796481Ff14017e6005508003"
cake_bsc = "0x0E09FaBB73Bd3Ade0a17ECC321fD13a19e81cE82"



busd_bsc_abi = read_file('busd_bsc_abi.json')
usdt_bsc_abi = read_file('usdt_bsc_abi.json')
twt_bsc_abi = read_file('twt_bsc_abi.json')
cake_bsc_abi = read_file('cake_bsc_abi.json')


# Ethereum

usdt_eth = "0xdAC17F958D2ee523a2206206994597C13D831ec7"

usdt_eth_abi = read_file('usdt_eth_abi.json')

# Polygon

weth_pol = "0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619"
weth_pol_abi = read_file('weth_pol_abi.json')
