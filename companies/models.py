# companies/models.py
from django.db import models

class Company(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, null=True, unique=True)
    uploaded_amount = models.IntegerField(default=0)
    limit = models.IntegerField(null=True, blank=True)
    balance_minutes = models.IntegerField(null=True, blank=True)
    balance_seconds = models.IntegerField(default=0)
    
    def __str__(self):
        return f'{self.name}'
    
    class Meta:
        verbose_name = 'Компания'
        verbose_name_plural = 'Компании'
        