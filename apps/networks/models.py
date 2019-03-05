from django.db import models
from .. import model_base
from conf import eth
from web3 import Web3, HTTPProvider
import time
import logging

scanlog = logging.getLogger('scanner')

class EthDriver(object):
    def __init__(self, endpoint):
        self.web3 = Web3(HTTPProvider(endpoint))

    def current_block(self):
        return self.web3.eth.blockNumber

    def get_block(self, block_number):
        return self.web3.eth.getBlock(block_number, full_transactions=True)

    def find_transactions(self, block_number, retry=True):
        scanlog.debug('find_transactions: block=%s'%block_number)
        block = self.get_block(block_number)

        # Been some odd errors where block is None...
        # My best guess is that it's the head block
        if not block and retry:
            scanlog.warning('find_transactions: got a null block, retrying in 2 seconds...')
            time.sleep(2)
            return self.find_transactions(block_number, retry=False)

        for rawtx in block.get('transactions', []):
            tx = dict(rawtx)
            tx['hasData'] = 'input' in tx and tx['input'] != '0x'
            tx['isToken'] = False
            if tx['hasData'] and tx['input'].startswith('0xa9059cbb'):
                tx['isToken'] = True
                tx['tokenAmount'] = Web3.toInt(hexstr=tx['input'][-32:])
                START_BYTE = 2 + 8 + (64 - 40) # 0x a9059cbb [24 0s] [address]
                address = '0x' + tx['input'][START_BYTE:START_BYTE+40]
                try:
                    tx['tokenTo'] = Web3.toChecksumAddress(address)
                except ValueError as e:
                    from apps.errors.models import ErrorLog
                    ErrorLog.objects.create(
                        nickname="Missing or corrupt input data, examine transaction",
                        traceback='Transaction: %s\n%s'%(tx, e))
                    tx['tokenTo'] = address
                for key in ['hash', 'blockHash']:
                    tx[key] = str(tx[key])
                tx.pop('r', '')
                tx.pop('s', '')

            yield tx

class Software(model_base.NicknamedBase):
    def get_driver(self, network):
        if(self.nickname == 'Ethereum'):
            return EthDriver(network.endpoint)

    @classmethod
    def ETHEREUM(cls):
        return cls.UNIQUE('Ethereum')

class Network(model_base.NicknamedBase):
    software = models.ForeignKey(Software, on_delete=models.DO_NOTHING)
    endpoint = models.TextField()

    @property
    def driver(self):
        if not hasattr(self, '_driver'):
            setattr(self, '_driver', self.software.get_driver(self))
        return self._driver

    def current_block(self):
        return self.driver.current_block()

class Scanner(model_base.NicknamedBase):
    network = models.ForeignKey(Network, on_delete=models.DO_NOTHING)
    latest_block = models.PositiveIntegerField(default=0)

    def get_watched_addresses(self):
        # TODO: IF LENGTH OF WATCHED > 2000 MAIL ADMINS
        from apps.subscriptions.models import Subscription
        watched_addresses = [s.watched_address for s in Subscription.objects.all()]
        cleaned = list(map(lambda s: s.lower().strip(), watched_addresses))
        print('Watch addresses:', cleaned)
        return cleaned

    def in_watch_cache(self, tx):
        # We'll eventually need to move the lookup to
        # a sql query, once it is no longer memory efficient
        # to do here
        get = lambda key: (tx.get(key, '') or '').lower()
        to = get('to')
        frm = get('from')
        tkto = get('tokenTo')
        return to in self.watched_cache or frm in self.watched_cache or tkto in self.watched_cache

    @property
    def watched_cache(self):
        if not hasattr(self, '_watched_addresses'):
            setattr(self, '_watched_addresses',
                self.get_watched_addresses())
        return self._watched_addresses

    def next_block_to_scan(self):
        current = self.network.driver.current_block()
        if current > self.latest_block:
            return self.latest_block + 1

    def process_next_block(self):
        next_block = self.next_block_to_scan()
        if not next_block:
            return None
        self.process_block(next_block)
        self.latest_block = next_block
        self.save()

    def process_block(self, block_number, save_transactions=False):
        transactions = list(self.network.driver.find_transactions(block_number))
        
        scanlog.info('Processing block: %s @ %s - %s transactions'%(
            self.network, block_number, len(transactions)))
        
        if save_transactions:
            import json
            fh = open('tests/transactions/block-%s.json'%block_number, 'w+')
            json.dump(transactions, fh, indent=2)

        return self.process_transactions(transactions)

    def process_transactions(self, transactions):
        from apps.subscriptions.models import Subscription
        for tx in transactions:
            if self.in_watch_cache(tx):
                scanlog.info('Found transaction: %s'%tx)
                subscriptions = Subscription.objects.filter(
                    models.Q(watched_address__iexact=tx['to']) |
                    models.Q(watched_address__iexact=tx['from'])
                )
                for subscription in subscriptions:
                    subscription.found_transaction(tx)
                if tx.get('isToken'):
                    from apps.contracts.models import Contract
                    contract, _new = Contract.DISCOVERED_TOKEN(self.network, tx['to'])
                    if _new:
                        scanlog.info('Found a new token contract: %s'%tx['to'])

    @classmethod
    def MAIN(cls):
        return MAIN_SCANNER()
    @classmethod
    def TEST(cls):
        return TEST_SCANNER()

    def block_scan(self, start_block, end_block=None, timeout=10, update_latest=False):
        scanlog.info('Starting blockscan: %s'%self.network)
        start = time.time()
        end = start + timeout
        next_block = start_block
        while time.time() < end:
            elapsed = time.time() - start
            if next_block > self.network.current_block():
                scanlog.info('Ending blockscan [%s]: No more blocks!'%elapsed)
                return
            if end_block and next_block > end_block:
                scanlog.info('Ending blockscan [%s]: Reached endblock!'%elapsed)
                return

            self.process_block(next_block)

            if update_latest:
                self.latest_block = next_block
                self.save()

            next_block += 1

        elapsed = time.time() - start

        # Mail an admin if we run out of scanblock time
        scanlog.info('Ending blockscan [%s]: Out of time!'%elapsed)
        raise Exception('Blockscan took more than %s seconds'%timeout)

    def scan_tail(self, timeout):
        return self.block_scan(self.latest_block, timeout=timeout, update_latest=True)

def DEFAULT():
    ether = Software.ETHEREUM()
    return {
        'mainnet': Network.UNIQUE('Ethereum Mainnet',
            software=ether,
            endpoint=eth.WEB3_INFURA['mainnet']
        ),
        'ropsten': Network.UNIQUE('Ethereum Ropsten',
            software=ether,
            endpoint=eth.WEB3_INFURA['ropsten']
        ),
    }

def MAIN_NETWORK():
    return DEFAULT()['mainnet']

def MAIN_SCANNER():
    main = MAIN_NETWORK()
    return Scanner.UNIQUE('PRIMARY - %s'%main.nickname, network=main)

def TEST_SCANNER():
    main = MAIN_NETWORK()
    return Scanner.UNIQUE('TEST - %s'%main.nickname, network=main)
