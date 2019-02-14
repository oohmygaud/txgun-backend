import json, os

ETHSCAN_TOKEN='I522H7BV8BPUNX2XEB8Y85DQGRMTKU75Q6'
ETHSCAN_URL='http://api.etherscan.io/api?apikey=%s&'%ETHSCAN_TOKEN

ETH_CONFIRMATIONS = 3

WEI_FROM_ETH = WEI = WEI_PER_ETH = 10**18
ETH_FROM_WEI = ETH = 1.0/WEI

CORP = '0x79bE4e987D616855F0894611d92f2632B4A9EA38'

WEB3_INFURA = {'mainnet': 'https://mainnet.infura.io/pnHIbVmvOcdMwe246xYS',
               'ropsten': 'https://ropsten.infura.io/pnHIbVmvOcdMwe246xYS'}

SHIP_CONTRACT_ADDRS = {
    'main': '0xe25b0BBA01Dc5630312B6A21927E578061A13f55',
    'ropsten': '0x6542EFD9efc4b140b046C18868A271Cb653d3607'
}
