# phrases/models.py
from django.db import models
from scripts.models import Script
from django.contrib.postgres.fields import ArrayField

class Phrase(models.Model):
    id = models.AutoField(primary_key=True)
    text = models.TextField(null=True)
    analogs = ArrayField(models.TextField(null=True), default=list, blank=True)
    number = models.IntegerField(null=True, blank=True)
    script = models.ForeignKey(Script, on_delete=models.CASCADE, null=True)
    
    class Meta:
        verbose_name = 'Фраза'
        verbose_name_plural = 'Фразы'
