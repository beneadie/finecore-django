"""
Any changes made to this file won't apply to datase until you run a migration.
To do this, run 'python manage.py makemigrations' and then 'python manage.py migrate'.
makemigrations creates the python code to make the changes to the DB.
migrate applies these changes.

Note that each class/model is a table in the datbase
"""

from django.db import models


import uuid
from decimal import Decimal



class UserApiKey(models.Model):
     uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True)  # Explicit primary key
     key = models.CharField(max_length=255, unique=True)
     created_at = models.DateTimeField(auto_now_add=True)



class Transaction(models.Model):
    transactionid = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)  # Explicit primary key
    uuid = models.UUIDField(editable=False)
    api_key = models.CharField(max_length=255) # logs the api key that was used so can be useful for retracing instances of fraud
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=25, decimal_places=2)
    datetime = models.DateTimeField(auto_now_add=True)



class UserWallet(models.Model):
     uuid = models.ForeignKey(UserApiKey, editable=False, on_delete=models.CASCADE, to_field='uuid', related_name='balance')
     balance = models.DecimalField(max_digits=26, decimal_places=2, default=Decimal("0.0"))
