# scripts/models.py
from django.db import models
from companies.models import Company
from users.models import CustomUser
from departments.models import Department
from products.models import Product

class Script(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)
    manager = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    active = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Скрипт'
        verbose_name_plural = 'Скрипты'
