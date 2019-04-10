from django.db import models
import uuid


class RandomPKBase(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class NicknamedBase(RandomPKBase):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    nickname = models.CharField(max_length=255, null=True, blank=True)
    
    @classmethod
    def UNIQUE(cls, nickname, **defaults):
        try:
            return cls.objects.get(nickname=nickname)
        except cls.DoesNotExist:
            return cls.objects.create(nickname=nickname, **defaults)

    def __str__(self):
        return self.nickname or "unnamed"

    class Meta:
        abstract = True


class OwnedBase(models.Model):
    user = models.ForeignKey('auth.user', on_delete=models.DO_NOTHING)

    class Meta:
        abstract = True