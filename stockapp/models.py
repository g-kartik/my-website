from django.db import models
from django.contrib.auth.models import User
from mysite.models import UserSession
# Create your models here.


class MyStocks(models.Model):
    ticker = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    session = models.ForeignKey(UserSession, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.ticker
