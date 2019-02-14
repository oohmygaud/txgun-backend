from .. import model_base
from django.db import models

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