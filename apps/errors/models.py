from ..model_base import NicknamedBase
from django.db import models

class ErrorLog(NicknamedBase):
    traceback = models.TextField()
