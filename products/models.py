# products/models.py
from django.db import models
from companies.models import Company

class Product(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, default="Не задан")
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)
    
    def __str__(self):
        return f'{self.company} - {self.name}'
    
    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'
        