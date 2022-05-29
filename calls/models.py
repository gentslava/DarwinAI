# app/models.py
from django.db import models
from django.db.models import JSONField
from users.models import CustomUser
from uuid import uuid4
from django.utils.deconstruct import deconstructible

@deconstructible
class UploadTo(object):
    def __init__(self, path):
        self.path = path

    def __call__(self, instance, filename):
        return '{}/{}/{}.{}'.format(self.path, uuid4().hex, uuid4().hex, filename.split('.')[-1])

class Call(models.Model):
    id = models.AutoField(primary_key=True)
    start_date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)
    record = models.FileField(upload_to=UploadTo('records'))
    name = models.TextField(null=True)
    time = models.CharField(max_length=255, null=True)
    size = models.IntegerField(null=True)
    status = models.CharField(max_length=255, default='Обработка')
    freq_hints = models.CharField(max_length=255, default='-')
    speed_podstr = models.CharField(max_length=255, default='-')
    loud_podstr = models.CharField(max_length=255, default='-')
    script_following = models.CharField(max_length=255, default='-')
    script_following_norm = models.CharField(max_length=255, default='-')
    purity = models.CharField(max_length=255, default='-')
    interceptions = models.CharField(max_length=255, default='-')
    volume = models.CharField(max_length=255, default='-')
    crit_words_count = models.CharField(max_length=255, default='-')
    neg_words_count = models.CharField(max_length=255, default='-')
    pos_operator = models.CharField(max_length=255, default='-')
    neg_operator = models.CharField(max_length=255, default='-')
    pos_client = models.CharField(max_length=255, default='-')
    neg_client = models.CharField(max_length=255, default='-')
    crit_words_said = JSONField(default=dict)
    neg_words_said = JSONField(default=dict)
    par_words_said = JSONField(default=dict)
    client_pos_words_said = JSONField(default=dict)
    client_neg_words_said = JSONField(default=dict)
    critical = models.BooleanField(default=False)
    reverse = models.BooleanField(default=False)
    
    script_statistics = JSONField(default=dict)
    
    critical_volume = models.BooleanField(default=False)
    critical_script_following = models.BooleanField(default=False)
    critical_loud_control = models.BooleanField(default=False)
    critical_speed_control = models.BooleanField(default=False)
    critical_speech_purity = models.BooleanField(default=False)
    critical_interceptions = models.BooleanField(default=False)
    critical_crit_words = models.BooleanField(default=False)
    critical_neg_words = models.BooleanField(default=False)
    critical_emotional_negative_operator = models.BooleanField(default=False)
    critical_emotional_negative_client = models.BooleanField(default=False)
    
    debug_time_uploaded = models.DateTimeField(blank=True, null=True)
    debug_time_daiml_sent = models.DateTimeField(blank=True, null=True)
    debug_time_daiml_start = models.DateTimeField(blank=True, null=True)
    debug_time_daiml_end = models.DateTimeField(blank=True, null=True)
    debug_time_daiml_arrived = models.DateTimeField(blank=True, null=True)
    debug_time_wa_sent = models.DateTimeField(blank=True, null=True)
    debug_time_wa_arrived = models.DateTimeField(blank=True, null=True)
    debug_time_wa_sent_again = models.DateTimeField(blank=True, null=True)
    debug_time_wa_arrived_again = models.DateTimeField(blank=True, null=True)
    
    debug_time_uploaded_spent = models.IntegerField(blank=True, null=True)
    debug_time_daiml_spent = models.IntegerField(blank=True, null=True)
    debug_time_wa_spent = models.IntegerField(blank=True, null=True)
    debug_time_wa_spent_again = models.IntegerField(blank=True, null=True)
    debug_time_first_stats_showing = models.IntegerField(blank=True, null=True)
    debug_time_postanalyze_spent = models.IntegerField(blank=True, null=True)
    debug_time_calls_showing = models.IntegerField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'Звонок'
        verbose_name_plural = 'Звонки'
