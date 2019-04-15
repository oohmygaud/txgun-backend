from web3 import Web3, HTTPProvider

ETHSCAN_TOKEN='I522H7BV8BPUNX2XEB8Y85DQGRMTKU75Q6'
ETHSCAN_URL='http://api.etherscan.io/api?apikey=%s&'%ETHSCAN_TOKEN

WEI_FROM_ETH = WEI = WEI_PER_ETH = 10**18
ETH_FROM_WEI = ETH = 1.0/WEI

GET_WEB3 = lambda host: Web3(HTTPProvider(host))

WEB3_INFURA = {'main': 'https://mainnet.infura.io/pnHIbVmvOcdMwe246xYS',
               'ropsten': 'https://ropsten.infura.io/pnHIbVmvOcdMwe246xYS'}

WEB3_DRIVERS = {k: GET_WEB3(v) for k, v in WEB3_INFURA.items()}

