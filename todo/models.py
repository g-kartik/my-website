from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class ToDoItems(models.Model):
    item_name = models.CharField(max_length=200)
    is_completed = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.item_name
