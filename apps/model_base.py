from django.db import models

class NicknamedBase(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    nickname = models.CharField(max_length=255)
    
    @classmethod
    def UNIQUE(cls, nickname, **defaults):
        try:
            return cls.objects.get(nickname=nickname)
        except cls.DoesNotExist:
            return cls.objects.create(nickname=nickname, **defaults)

    def __str__(self):
        return self.nickname

    class Meta:
        abstract = True

class OwnedBase(models.Model):
    user = models.ForeignKey('auth.user', on_delete=models.DO_NOTHING)

    class Meta:
        abstract = True