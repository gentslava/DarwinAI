from django.db import models
from django_better_admin_arrayfield.models.fields import ArrayField
# from django.contrib.postgres.fields import ArrayField

class Dictionary(models.Model):
    id = models.AutoField(primary_key=True)
    dictionary_name = models.CharField(max_length=255, null=True)
    dictionary_words = ArrayField(models.TextField(null=True), default=list, blank=True)
    
    class Meta:
        verbose_name = 'Словарь'
        verbose_name_plural = 'Словари'
