from django.db import models
from uuid import uuid4


class Base(models.Model):
    id = models.UUIDField(default=uuid4, primary_key=True, editable=True)  # should i call uuid() or not
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)


    class Meta:
        abstract = True # not to add