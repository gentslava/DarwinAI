# users/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField
from companies.models import Company
from departments.models import Department
from products.models import Product

def default_par_words():
    return list('щас че э ээ эээ аа ааа ниче типа ну мм ммм скока нискока скоко нискоко але здрасьте'.split(' '))

class CustomUser(AbstractUser):
    id = models.AutoField(primary_key=True)
    first_name = models.CharField("Имя", max_length=255, null=True)
    last_name = models.CharField("Фамилия", max_length=255, null=True)
    email = models.EmailField("E-mail", null=True, unique=True)
    avatar = models.CharField(max_length=255, null=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True)
    supermanager = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True)
    scripts = ArrayField(models.CharField(max_length=255, default=list), default=list, blank=True)
    pos_words = ArrayField(models.CharField(max_length=255, null=True), default=list, blank=True)
    crit_words = ArrayField(models.CharField(max_length=255, null=True), default=list, blank=True)
    neg_words = ArrayField(models.CharField(max_length=255, null=True), default=list, blank=True)
    par_words = ArrayField(models.CharField(max_length=255, null=True), default=default_par_words, blank=True)
    client_pos_words = ArrayField(models.CharField(max_length=255, null=True), default=list, blank=True)
    client_neg_words = ArrayField(models.CharField(max_length=255, null=True), default=list, blank=True)
    critical = models.CharField(max_length=255, default="‒")
    purity = models.CharField(max_length=255, default="‒")
    speed_podstr = models.CharField(max_length=255, default="‒")
    loud_podstr = models.CharField(max_length=255, default="‒")
    script_following = models.CharField(max_length=255, default="‒")
    crit_words_count = models.CharField(max_length=255, default='-')
    neg_words_count = models.CharField(max_length=255, default='-')
    pos_operator = models.CharField(max_length=255, default='-')
    neg_operator = models.CharField(max_length=255, default='-')
    pos_client = models.CharField(max_length=255, default='-')
    neg_client = models.CharField(max_length=255, default='-')
    uploaded_amount = models.IntegerField(default=0)
    limit = models.IntegerField(null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    product = models.ManyToManyField(Product)
    
    hide_speech_volume = models.BooleanField(default=False)
    hide_script_following = models.BooleanField(default=False)
    hide_loud_podstr = models.BooleanField(default=False)
    hide_speed_podstr = models.BooleanField(default=False)
    hide_speech_purity = models.BooleanField(default=False)
    hide_interception = models.BooleanField(default=False)
    hide_critical_words = models.BooleanField(default=False)
    hide_negative_words = models.BooleanField(default=False)
    hide_positive_count = models.BooleanField(default=False)
    hide_negative_count = models.BooleanField(default=False)
    
    critical_negative_emotions_client = models.CharField(max_length=255, default="‒")
    critical_negative_emotions_operator = models.CharField(max_length=255, default="‒")
    critical_speech_volume = models.CharField(max_length=255, default="‒")
    critical_script_following = models.CharField(max_length=255, default="‒")
    critical_loud_podstr = models.CharField(max_length=255, default="‒")
    critical_speed_podstr = models.CharField(max_length=255, default="‒")
    critical_speech_purity = models.CharField(max_length=255, default="‒")
    critical_interception_all = models.CharField(max_length=255, default="‒")
    critical_interception_avg = models.CharField(max_length=255, default="‒")
    critical_critical_words_all = models.CharField(max_length=255, default="‒")
    critical_critical_words_avg = models.CharField(max_length=255, default="‒")
    critical_negative_words_all = models.CharField(max_length=255, default="‒")
    critical_negative_words_avg = models.CharField(max_length=255, default="‒")
    critical_hints_count_all = models.CharField(max_length=255, default="‒")
    critical_hints_count_avg = models.CharField(max_length=255, default="‒")
    
    def __str__(self):
        return f'{self.last_name} {self.first_name} - {self.username} {self.id}'
    
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'