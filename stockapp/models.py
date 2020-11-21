from django.db import models
# Create your models here.


class MyStocks(models.Model):
    ticker = models.CharField(max_length=100)

    def __str__(self):
        return self.ticker
