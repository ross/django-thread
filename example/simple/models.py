from django.db import models


class Item(models.Model):
    key = models.CharField(max_length=32, unique=True)
    value = models.CharField(max_length=255)
