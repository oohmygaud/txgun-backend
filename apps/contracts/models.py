from .. import model_base
from django.db import models
import pytz
from datetime import datetime, timedelta
from requests import Request, Session
from django.conf import settings
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json

class Interface(model_base.NicknamedBase):
    abi = models.TextField(null=True, blank=True)

class Contract(model_base.NicknamedBase):
    network = models.ForeignKey('networks.Network', on_delete=models.DO_NOTHING)
    address = models.CharField(max_length=255)
    abi = models.TextField(null=True, blank=True)
    interfaces = models.ManyToManyField(Interface)

    @classmethod
    def DISCOVERED_TOKEN(cls, network, address):
        contract, _new = cls.objects.get_or_create(
            network=network, address=address)
        contract.interfaces.add(Interface.UNIQUE('evmTransfer'))
        return contract, _new

class PriceLookup(model_base.RandomPKBase):
    created_at = models.DateTimeField(auto_now_add=True)
    asset = models.CharField(max_length=16)
    currency = models.CharField(max_length=4, default='USD')
    price = models.DecimalField(max_digits=20, decimal_places=10)

    def __str__(self):
        return '%s: 1%s = %s%s'%(
            self.created_at,
            self.asset,
            self.price,
            self.currency
        )

    @classmethod
    def get_latest(cls, asset, currency='USD'):
        try:
            recent = datetime.now(pytz.utc)-timedelta(minutes=10)
            return cls.objects.get(asset=asset, created_at__gte=recent)
        except cls.DoesNotExist:
            return cls.objects.create(asset=asset, price=cls.do_lookup(asset, currency))

    @classmethod
    def do_lookup(cls, asset, currency='USD'):
        if asset == 'ETH':
            url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
            parameters = {
                'symbol': asset,
                'convert': currency
            }
            headers = {
                'Accepts': 'application/json',
                'X-CMC_PRO_API_KEY': settings.CMC_API_KEY
            }

            session = Session()
            session.headers.update(headers)

            try:
                response = session.get(url, params=parameters)
                data = json.loads(response.text)
                return data['data'][asset]['quote'][currency]['price']
            except (ConnectionError, Timeout, TooManyRedirects) as e:
                print(e)

