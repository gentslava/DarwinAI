from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse, Http404, HttpResponseForbidden, HttpResponseBadRequest
import threading
import pandas as pd
import os, shutil, json, librosa, math
import traceback
from django.utils import timezone
from datetime import datetime
from uuid import uuid4
from django.db import connections
from django.db.models.functions import Length

from .forms import *
from users.forms import CustomAuthenticationForm

from calls.models import Call
from users.models import CustomUser
from scripts.models import Script
from phrases.models import Phrase
from departments.models import Department
from products.models import Product

from DAIML_WA_NEW_SEARCH.main import InfoExtractor, WordAnalyse, get_script_analysis

infoExtractor = InfoExtractor()
wordAnalyse = WordAnalyse()
basedir = '/home/ubuntu/DarwinAI/media'
std_avatar = '/static/images/avatar.svg'

def datetime_tz():
    return timezone.make_aware(datetime.today(), timezone.get_current_timezone())

def records_path(salt):
    return os.path.join(basedir, 'records', salt)

def decrypting_path(salt):
    return os.path.join(basedir, 'decrypting', salt)

def count_calls(manager):
    return Call.objects.filter(user = manager).count()

def recalc_summary(manager):
    calls = Call.objects.filter(user = manager)
    calls_critical = calls.filter(critical = True)
    if calls.count() is 0:
        critical = '‒'
    else:
        critical = calls_critical.count()
        
    calls_purity = calls.exclude(purity = '-')
    purity = 0
    for call in calls_purity:
        purity += int(call.purity[:-1])
    if calls_purity.count() is 0:
        purity = '‒'
    else:
        purity //= calls_purity.count()
        purity = str(purity) + '%'
        
    calls_speed_podstr = calls.exclude(speed_podstr = '-')
    speed_podstr = 0
    for call in calls_speed_podstr:
        speed_podstr += int(call.speed_podstr[:-1])
    if calls_speed_podstr.count() is 0:
        speed_podstr = '‒'
    else:
        speed_podstr //= calls_speed_podstr.count()
        speed_podstr = str(speed_podstr) + '%'
        
    calls_loud_podstr = calls.exclude(loud_podstr = '-')
    loud_podstr = 0
    for call in calls_loud_podstr:
        loud_podstr += int(call.loud_podstr[:-1])
    if calls_loud_podstr.count() is 0:
        loud_podstr = '‒'
    else:
        loud_podstr //= calls_loud_podstr.count()
        loud_podstr = str(loud_podstr) + '%'
        
    calls_script_following = calls.exclude(script_following = '-')
    script_following = 0
    for call in calls_script_following:
        script_following += int(call.script_following[:-1])
    if calls_script_following.count() is 0:
        script_following = '‒'
    else:
        script_following //= calls_script_following.count()
        script_following = str(script_following) + '%'
        
    manager.critical = critical
    manager.purity = purity
    manager.speed_podstr = speed_podstr
    manager.loud_podstr = loud_podstr
    manager.script_following = script_following
    manager.save()
    for conn in connections.all():
        conn.close()

# Получение информации о скрипте
def get_script(script):
    script_phrases = []
    phrases = Phrase.objects.filter(script = script).order_by('id').order_by('number')
    for phrase in phrases:
        script_phrase = {
            'id': phrase.id,
            'text': phrase.text,
            'analogs': phrase.analogs
        }
        script_phrases.append(script_phrase)
    script_info = {
        'id': script.id,
        'name': script.name,
        'department': script.department.name,
        'product': script.product.name,
        'phrases': script_phrases,
        'active': script.active
    }
    return script_info

# Получение списка скриптов
def get_scripts(request_user):
    return Script.objects.filter(manager = request_user).order_by('id')

# Получение списка фраз
def get_phrases(request_user, manager):
    script_phrases = []
    department = manager.department
    products = manager.product.all()
    scripts = get_scripts(request_user).filter(department = department, active = True)
    for product in products:
        script_query = scripts.filter(product = product)
        if script_query.count() > 0:
            script = list(script_query)[0]
            script_info = get_script(script)
            for phrase in script_info['phrases']:
                script_phrases.append([phrase['text']] + phrase['analogs'])
    return script_phrases

def get_dictionary(salt, dictionaries):
    try:
        file_path = decrypting_path(salt)
        df_result = pd.read_csv(file_path+'/result.csv')
        df_loud = pd.read_csv(file_path+'/loud-res.csv')
        extra = {}
        emotional = {'client': {'negative': '‒', 'positive': '‒'}}
        res_dictionaries = []
        dictionaries_names = ['script', 'crit', 'neg', 'par', 'client_pos', 'client_neg']
        channels = ['operator']
        for i in range(6):
            res_dictionaries.append({
                'operator': {
                    'count_total': 0,
                    'count_said': 0,
                    'count_each': {},
                    'said': {},
                    'script_following': '-',
                    'script_following_norm': '-',
                    'purity': '‒',
                },
                'client': {
                    'count_total': 0,
                    'count_said': 0,
                    'count_each': {},
                    'said': {},
                    'script_following': '-',
                    'script_following_norm': '-',
                    'purity': '‒',
                }
            })
            if i >= len(dictionaries):
                dictionaries.append([])

        res = wordAnalyse.extract(df_result, df_loud, False,
            script_words_double_list = dictionaries[0],
            par_words_list = dictionaries[1],
            crit_words_list = dictionaries[2],
            neg_words_list = dictionaries[3],
            client_pos_words_list = dictionaries[4],
            client_neg_words_list = dictionaries[5]
        )
        if 'client' in res[-1]:
            channels.append('client')
        df_extra = res[0]
        df_extra = df_extra.fillna('')
        df_extra.to_csv(file_path+'/extra.csv', index=False)
        for channel in channels:
            for i in range(6):
                timing = {}
                table = {}
                res_dictionaries[i][channel]['count_total'] = res[-1][channel]['num_'+dictionaries_names[i]]
                res_dictionaries[i][channel]['count_each'] = res[-1][channel]['count_'+dictionaries_names[i]]
                res_dictionaries[i][channel]['purity'] = res[-1][channel]['speech_purity']
                res_dictionaries[i][channel]['timing'] = timing
                res_dictionaries[i][channel]['table'] = table
                for j in res[-1][channel]['table_'+dictionaries_names[i]].index:
                    timing[j] = {
                        'start': res[-1][channel]['table_'+dictionaries_names[i]].format_start[j],
                        'words': res[-1][channel]['table_'+dictionaries_names[i]][dictionaries_names[i]][j],
                        'words_counter': res[-1][channel]['table_'+dictionaries_names[i]].counter[j],
                        'line': res[-1][channel]['table_'+dictionaries_names[i]].number_of_row[j],
                    }
                if dictionaries_names[i] == 'script':
                    res_dictionaries[i][channel]['count_said'] = int(res[-1][channel][dictionaries_names[i]+'_said_num'])
                    if res[-1][channel]['num_script'] > 0:
                        res_dictionaries[i][channel]['script_following'] = str(int(res[-1][channel]['script_said_num'] * 100/ res[-1][channel]['num_script'])) + '%'
                        res_dictionaries[i][channel]['script_following_norm'] = str(res[-1][channel]['script_said_num']) + '/' + str(res[-1][channel]['num_script'])
                    for j in res[-1][channel][dictionaries_names[i]+'_said_table'].index:
                        table[j] = {
                            'text': res[-1][channel][dictionaries_names[i]+'_said_table'].script[j],
                            'said': True if res[-1][channel][dictionaries_names[i]+'_said_table'].said[j] == 1 else False,
                        }
                with open(file_path+'/'+dictionaries_names[i]+'.txt', 'w') as outfile:
                    outfile.write(json.dumps(res_dictionaries[i]))

            emotional[channel] = {
                'negative': str(int(res[-1][channel]['emotional_negative'])) + '%',
                'positive': str(int(res[-1][channel]['emotional_positive'])) + '%',
            }
        with open(file_path+'/emotional.txt', 'w') as outfile:
            outfile.write(json.dumps(emotional))
    except Exception as e:
        pass
    return

def get_data(salt):
    error = ''
    data_json = {}
    speak_model = {}
    loud = {}
    additional = {}
    score = {}
    info = {}
    extra = {}
    res_dictionaries = []
    dictionaries_names = ['script', 'crit', 'neg', 'par', 'client_pos', 'client_neg']
    emotional = {}
    record_path = records_path(salt)
    file_path = decrypting_path(salt)
    try:
        if not os.path.isdir(record_path): raise FileNotFoundError('Folder not found')
        if os.path.isfile(file_path+'/info.txt'):
            df_result = pd.read_csv(file_path+'/result.csv')
            df_result = df_result.fillna('')
            channel_num = df_result['channel'].nunique()
            df_result.channel = df_result.channel.apply(lambda x: 'неизвестно' if channel_num == 1 else ('менеджер' if x == 'operator' else 'клиент'))
            for i in df_result.index:
                speak_model[i] = eval(df_result.iloc[i].to_json())
            
            with open(file_path+'/info.txt', 'r') as infile:
                info = json.load(infile)
                
            df_loud = pd.read_csv(file_path+'/loud-res.csv')
            for i in df_loud.index:
                loud[i] = eval(df_loud.iloc[i].to_json())

            df_additional = pd.read_csv(file_path+'/additional.csv')
            for i in df_additional.index:
                additional[i] = eval(df_additional.iloc[i].to_json())

            df_score = pd.read_csv(file_path+'/score.csv')
            for i in df_score.index:
                score[i] = eval(df_score.iloc[i].to_json())
                
            df_extra = pd.read_csv(file_path+'/extra.csv')
            df_extra = df_extra.fillna('')
            for i in df_extra.index:
                extra[i] = eval(df_extra.iloc[i].to_json())
                
            with open(file_path+'/emotional.txt', 'r') as infile:
                emotional = json.load(infile)
                
            for i in range(6):
                with open(file_path+'/'+dictionaries_names[i]+'.txt', 'r') as infile:
                    dictionary = json.load(infile)
                    res_dictionaries.append(dictionary)
                
    except Exception as e:
        error = 'Ошибка'
        with open("/home/ubuntu/files_with_errors.txt", 'a') as file:
            file.write(str(datetime_tz()) + "\n" + file_path + "\n" + traceback.format_exc() + "\n")
    data_json = {
        'error': error,
        'speak_model': speak_model,
        'info': info,
        'loud': loud,
        'additional': additional,
        'score': score,
        'extra': extra,
        'emotional': emotional,
    }
    for i in range(6): data_json[dictionaries_names[i]+'_words'] = res_dictionaries[i]
    return data_json

# OPTIMIZIROVAT
def is_critical(call, request_user):
    salt = call.record.name.split('/')[1]
    file_path = decrypting_path(salt)
    if os.path.isfile(file_path+'/info.txt'):
        file = open(file_path+'/info.txt', 'r')
        info = json.load(file)
        df_result = pd.read_csv(file_path+'/result.csv')
        channel_num = df_result['channel'].nunique()
        df_loud = pd.read_csv(file_path+'/loud-res.csv')
        dictionaries = [
            get_phrases(request_user, call.user),
            request_user.par_words,
            request_user.crit_words,
            request_user.neg_words
        ]
        res = get_data(salt)
        time = call.time.split(':')
        minute = int(time[0])
        second = int(time[1])
        mills = int(time[2])
        time = minute + second/60 + mills/600
        critical = False
        reverse = call.reverse
        channel0 = 'client' if reverse else 'operator'
        channel1 = 'operator' if reverse else 'client'
        
        if channel_num > 1 and request_user.critical_negative_emotions_client != '‒':
            call.critical_emotional_negative_client = eval(call.neg_client[:-1]+request_user.critical_negative_emotions_client)
            critical = critical or call.critical_emotional_negative_client
            
        if request_user.critical_negative_emotions_operator != '‒':
            call.critical_emotional_negative_operator = eval(call.neg_operator[:-1]+request_user.critical_negative_emotions_operator)
            critical = critical or call.critical_emotional_negative_operator
            
        if request_user.critical_speech_volume != '‒':
            call.critical_volume = eval(str(call.volume)+request_user.critical_speech_volume)
            critical = critical or call.critical_volume
            
        if channel_num > 1 and request_user.critical_script_following != '‒' and call.script_following != '-':
            call.critical_script_following = eval(call.script_following[:-1]+request_user.critical_script_following)
            critical = critical or call.critical_script_following
            
        if request_user.critical_loud_podstr != '‒':
            call.critical_loud_control = eval(call.loud_podstr[:-1]+request_user.critical_loud_podstr)
            critical = critical or call.critical_loud_control
            
        if request_user.critical_speed_podstr != '‒':
            call.critical_speed_control = eval(call.speed_podstr[:-1]+request_user.critical_speed_podstr)
            critical = critical or call.critical_speed_control
            
        if request_user.critical_speech_purity != '‒':
            call.critical_speech_purity = eval(call.purity[:-1]+request_user.critical_speech_purity)
            critical = critical or call.critical_speech_purity

        if call.interceptions != '-' and request_user.critical_interception_all != '‒':
            call.critical_interceptions = eval(str(call.interceptions)+request_user.critical_interception_all)
            critical = critical or call.critical_interceptions
        if call.interceptions != '-' and request_user.critical_interception_avg != '‒':
            call.critical_interceptions = call.critical_interceptions or eval(str(call.interceptions/time)+ request_user.critical_interception_avg)
            critical = critical or call.critical_interceptions
            
        if request_user.critical_critical_words_all != '‒':
            call.critical_crit_words = eval(str(call.crit_words_count)+request_user.critical_critical_words_all)
            critical = critical or call.critical_crit_words
        if request_user.critical_critical_words_avg != '‒':
            call.critical_crit_words = call.critical_crit_words or eval(str(call.crit_words_count/time)+ request_user.critical_critical_words_avg)
            critical = critical or call.critical_crit_words
           
        if request_user.critical_negative_words_all != '‒':
            call.critical_neg_words = eval(str(call.neg_words_count)+request_user.critical_negative_words_all)
            critical = critical or call.critical_neg_words
        if request_user.critical_negative_words_avg != '‒':
            call.critical_neg_words = call.critical_neg_words or eval(str(call.neg_words_count/time)+ request_user.critical_negative_words_avg)
            critical = critical or call.critical_neg_words
            
#                 if request_user.critical_hints_count_all != '‒':
#                     critical = critical or eval(+request_user.critical_hints_count_all)
#                 if request_user.critical_hints_count_avg != '‒':
#                     critical = critical or eval(str(/time)+ request_user.critical_hints_count_avg)

        call.critical = critical
        call.status = 'Обработано'
        call.save()

# Постобработка звонка
def calc_call(call_id, request_user):
    for conn in connections.all():
        conn.close()
    call = Call.objects.get(id = call_id)
    manager = call.user
    salt = call.record.name.split('/')[1]
    call.debug_time_wa_sent_again = datetime_tz()
    dictionaries = [
        get_phrases(request_user, manager),
        request_user.par_words,
        request_user.crit_words,
        request_user.neg_words,
        request_user.client_pos_words,
        request_user.client_neg_words
    ]
    get_dictionary(salt, dictionaries)
    data = get_data(salt)
    call.debug_time_wa_arrived_again = datetime_tz()
    if call.size is None: #
        call.size = os.path.getsize(os.path.join(basedir, str(call.record))) #
    wa_spent = (call.debug_time_wa_arrived_again - call.debug_time_wa_sent_again).total_seconds() * 1000
#     call.debug_time_wa_spent_again = int(wa_spent * 1024 * 1024 / call.size)
    call.debug_time_wa_spent_again = int(wa_spent)
    if data['error'] != '':
        call.status = data['error']
    else:
        if call.reverse and not 'client' in data['info']:
            call.reverse = False
        channel0 = 'client' if call.reverse else 'operator'
        channel1 = 'operator' if call.reverse else 'client'
        speed_podstr = data['info']['speed_control']
        loud_podstr = data['info']['volume_control']
        purity = data['par_words'][channel0]['purity']
        script_following = data['script_words'][channel0]['script_following']
        script_following_norm = data['script_words'][channel0]['script_following_norm']
        interceptions = data['info'][channel0]['interseps']
        crit_words_count = data['crit_words'][channel0]['count_total']
        neg_words_count = data['neg_words'][channel0]['count_total']
        pos_operator = data['emotional'][channel0]['positive']
        neg_operator = data['emotional'][channel0]['negative']
        pos_client = data['emotional'][channel1]['positive']
        neg_client = data['emotional'][channel1]['negative']
        volume = data['info'][channel0]['volume_of_speech']
        if speed_podstr != '‒':
            call.speed_podstr = str(speed_podstr) + '%'
        if loud_podstr != '‒':
            call.loud_podstr = str(loud_podstr) + '%'
        if purity != '‒':
            call.purity = str(purity) + '%'
        if script_following != '‒':
            call.script_following = script_following
        if script_following_norm != '‒':
            call.script_following_norm = script_following_norm
        if interceptions != '‒':
            call.interceptions = interceptions
        if crit_words_count != '‒':
            call.crit_words_count = crit_words_count
        if neg_words_count != '‒':
            call.neg_words_count = neg_words_count
        if pos_operator != '‒':
            call.pos_operator = pos_operator
        if neg_operator != '‒':
            call.neg_operator = neg_operator
        if pos_client != '‒':
            call.pos_client = pos_client
        if neg_client != '‒':
            call.neg_client = neg_client
        if volume != '‒':
            call.volume = volume
        call.crit_words_said = data['crit_words'][channel0]['count_each']
        call.neg_words_said = data['neg_words'][channel0]['count_each']
        call.par_words_said = data['par_words'][channel0]['count_each']
        call.client_pos_words_said = data['client_pos_words'][channel1]['count_each']
        call.client_neg_words_said = data['client_neg_words'][channel1]['count_each']
    is_critical(call, request_user)
    recalc_summary(manager)
    for conn in connections.all():
        conn.close()
    
# Пересчет звонков при изменении
def recalc_calls(request_user):
    managers = list(CustomUser.objects.filter(supermanager = request_user))
    for manager in managers:
        calls = list(Call.objects.filter(user = manager))
        for call in calls:
            call.status = 'Обрабатывается'
            call.save()
    for manager in managers:
        calls = list(Call.objects.filter(user = manager))
        for call in calls:
            calc_call(call.id, request_user)

def recalc_critical(request_user):
    managers = CustomUser.objects.filter(supermanager = request_user)
    for manager in managers:
        calls = Call.objects.filter(user = manager)
        for call in calls:
            is_critical(call, request_user)
        recalc_summary(manager)

# Сортировка звонков по параметрам
def get_order_call(manager):
    calls = Call.objects.filter(user = manager)
    calls_date = calls.order_by('status', '-id')
    calls_name = calls.order_by('status', '-name', '-id')
    calls_duration = calls.order_by('status', '-time', '-id')
    calls_freq_hints = calls.order_by('status', '-freq_hints', '-id')
    calls_speed_podstr = calls.order_by('status', -Length('speed_podstr'), '-speed_podstr', '-id')
    calls_loud_podstr = calls.order_by('status', -Length('loud_podstr'), '-loud_podstr', '-id')
    calls_script_following = calls.order_by('status', -Length('script_following'), '-script_following', '-id')
    calls_interceptions = calls.order_by('status', -Length('interceptions'), '-interceptions', '-id')
    calls_volume = calls.order_by('status', -Length('volume'), '-volume', '-id')
    calls_critical = calls.order_by('status', '-critical', '-id')
    
    calls_date_rev = calls.order_by('status', 'id')
    calls_name_rev = calls.order_by('status', 'name', 'id')
    calls_duration_rev = calls.order_by('status', 'time', 'id')
    calls_freq_hints_rev = calls.order_by('status', 'freq_hints', 'id')
    calls_speed_podstr_rev = calls.order_by('status', Length('speed_podstr'), 'speed_podstr', 'id')
    calls_loud_podstr_rev = calls.order_by('status', Length('loud_podstr'), 'loud_podstr', 'id')
    calls_script_following_rev = calls.order_by('status', Length('script_following'), 'script_following', 'id')
    calls_interceptions_rev = calls.order_by('status', Length('interceptions'), 'interceptions', 'id')
    calls_volume_rev = calls.order_by('status', Length('volume'), 'volume', 'id')
    calls_critical_rev = calls.order_by('status', 'critical', 'id')
    
    count = calls_date.count()
    calls_order = {
        'name-order': [None] * count,
        'date-order': [None] * count,
        'duration-order': [None] * count,
        'freq_hints-order': [None] * count,
        'speed_podstr-order': [None] * count,
        'loud_podstr-order': [None] * count,
        'script_following-order': [None] * count,
        'interceptions-order': [None] * count,
        'volume-order': [None] * count,
        'critical-order': [None] * count,
        
        'name-order-rev': [None] * count,
        'date-order-rev': [None] * count,
        'duration-order-rev': [None] * count,
        'freq_hints-order-rev': [None] * count,
        'speed_podstr-order-rev': [None] * count,
        'loud_podstr-order-rev': [None] * count,
        'script_following-order-rev': [None] * count,
        'interceptions-order-rev': [None] * count,
        'volume-order-rev': [None] * count,
        'critical-order-rev': [None] * count,
    }
    for call in calls_date:
        id = call.id
        calls_order['name-order'][list(calls_name).index(call)] = id
        calls_order['date-order'][list(calls_date).index(call)] = id
        calls_order['duration-order'][list(calls_duration).index(call)] = id
        calls_order['freq_hints-order'][list(calls_freq_hints).index(call)] = id
        calls_order['speed_podstr-order'][list(calls_speed_podstr).index(call)] = id
        calls_order['loud_podstr-order'][list(calls_loud_podstr).index(call)] = id
        calls_order['script_following-order'][list(calls_script_following).index(call)] = id
        calls_order['interceptions-order'][list(calls_interceptions).index(call)] = id
        calls_order['volume-order'][list(calls_volume).index(call)] = id
        calls_order['critical-order'][list(calls_critical).index(call)] = id
        
        calls_order['name-order-rev'][list(calls_name_rev).index(call)] = id
        calls_order['date-order-rev'][list(calls_date_rev).index(call)] = id
        calls_order['duration-order-rev'][list(calls_duration_rev).index(call)] = id
        calls_order['freq_hints-order-rev'][list(calls_freq_hints_rev).index(call)] = id
        calls_order['speed_podstr-order-rev'][list(calls_speed_podstr_rev).index(call)] = id
        calls_order['loud_podstr-order-rev'][list(calls_loud_podstr_rev).index(call)] = id
        calls_order['script_following-order-rev'][list(calls_script_following_rev).index(call)] = id
        calls_order['interceptions-order-rev'][list(calls_interceptions_rev).index(call)] = id
        calls_order['volume-order-rev'][list(calls_volume_rev).index(call)] = id
        calls_order['critical-order-rev'][list(calls_critical_rev).index(call)] = id
    return calls_order
    
# Получение статуса и длительности звонка
def get_duration(path):
    status = 'Обработка'
    time = '--:--:-'
    size = 0
    try:
        norm_time = librosa.get_duration(filename=path)
        time = "{:02d}".format(int(norm_time)//60)+":"+"{:02d}".format(int(norm_time)%60)+":"+str(int((norm_time-int(norm_time))*10))
        size = os.path.getsize(path)
    except OSError as e:
        status = 'Ошибка'
        with open("/home/ubuntu/files_not_found.txt", 'a') as file:
            file.write(str(datetime_tz()) + "\n" + path + "\n" + traceback.format_exc() + "\n")
    return status, time, norm_time, size

# Получение информации о менеджере
def get_manager(manager):
    avatar = manager.avatar if manager.avatar else std_avatar
    count = count_calls(manager)
    rating = '‒'
    color = 0
    if manager.critical != '‒' and count > 0:
        rating = int((count - int(manager.critical))*100/count)/10
        if rating == 10:
            rating = int(rating)
        if rating < 9.5:
            color = 1
        if rating < 8:
            color = 2
        rating = str(rating).replace(',', '.')
    
    manager_info = {
        'id': manager.id,
        'rating': rating,
        'first_name': manager.first_name,
        'last_name': manager.last_name,
        'critical': manager.critical,
        'purity': manager.purity,
        'speed_podstr': manager.speed_podstr,
        'loud_podstr': manager.loud_podstr,
        'script_following': manager.script_following,
        'count': count,
        'color': color,
        'avatar': avatar,
        'status': manager.is_active,
        'department': manager.department.name,
        'product': list(manager.product.all().values_list('name', flat=True)),
    }
    return manager_info

# Получение списка отделов
def get_departments(request_user):
    return list(Department.objects.filter(company = request_user.company).order_by('id').values_list('name', flat=True))

# Получение списка проектов
def get_products(request_user):
    return list(Product.objects.filter(company = request_user.company).order_by('id').values_list('name', flat=True))

# Подготовка файлов на экспорт
def prepare_export(call, request_user):
    if not call is None:
        salt = call.record.name.split('/')[1]
        file_path = decrypting_path(salt)
        export_path = os.path.join('/home/ubuntu/DarwinAI/export/calls', salt)
        if not os.path.isdir(export_path):
            os.makedirs(export_path)
        if not os.path.isfile(file_path+'/result.csv'):
            return
        df_result = pd.read_csv(file_path+'/result.csv')
        df_export = df_result[['channel', 'format_start', 'denormalized_text']].copy()
        df_export.to_csv(export_path+'/'+call.name+'.csv', index=False)
        
        channel_num = df_result['channel'].nunique()
        results_info_extractor = infoExtractor.extract(
            file_path+'/speech.csv',
            file_path+'/loud.csv',
            file_path+'/clear.csv'
        )
        results_words_anal = get_data(salt)
        tables_script_analysis = get_script_analysis(results_info_extractor, results_words_anal)
        if not os.path.isdir(os.path.join(export_path, 'operator')):
            os.makedirs(os.path.join(export_path, 'operator'))
            if channel_num > 1:
                os.makedirs(os.path.join(export_path, 'client'))
        tables_script_analysis['operator'].to_csv(export_path+'/operator/scripts.csv', index=False)
        if channel_num > 1:
            tables_script_analysis['client'].to_csv(export_path+'/client/scripts.csv', index=False)
        if call.reverse:
            call.script_statistics = tables_script_analysis['client'].to_json()
        else:
            call.script_statistics = tables_script_analysis['operator'].to_json()
        call.save()
        for conn in connections.all():
            conn.close()
    else:
        export_path = os.path.join('/home/ubuntu/DarwinAI/export/managers', str(request_user.id))
        if not os.path.isdir(export_path):
            os.makedirs(export_path)
        data_export = []
        managers = CustomUser.objects.filter(supermanager = request_user)
        for manager in managers:
            calls = Call.objects.filter(user = manager)
            for call in calls:
                salt = call.record.name.split('/')[1]
                file_path = decrypting_path(salt)
                if not os.path.isfile(file_path+'/result.csv'):
                    continue
                df_result = pd.read_csv(file_path+'/result.csv')
                channel_num = df_result['channel'].nunique()
                channel0 = 'client' if call.reverse else 'operator'
                channel1 = 'operator' if call.reverse else 'client'
                dictionaries = [
                    get_phrases(request_user, manager),
                    request_user.par_words,
                    request_user.crit_words,
                    request_user.neg_words,
                    request_user.client_pos_words,
                    request_user.client_neg_words
                ]
                data = get_data(salt)
                data_export.append([
                    manager.get_full_name(),
                    call.name,
                    call.volume,
                    call.script_following,
                    data['info']['speed_control'],
                    data['info']['volume_control'],
                    call.interceptions,
                    call.purity,
                    data['crit_words'][channel0]['count_total']+data['neg_words'][channel0]['count_total'],
                    data['emotional'][channel0]['positive'],
                    data['emotional'][channel1]['positive'] if channel_num > 1 else '‒',
                    data['emotional'][channel0]['negative'],
                    data['emotional'][channel1]['negative'] if channel_num > 1 else '‒',
                    data['crit_words'][channel0]['count_each'],
                    data['neg_words'][channel0]['count_each'],
                    data['par_words'][channel0]['count_each'],
                    data['client_pos_words'][channel1]['count_each'],
                    data['client_neg_words'][channel1]['count_each'],
                ])
        df_export = pd.DataFrame(data_export, columns = [
            'manager',
            'file',
            'speech_volume',
            'script_following',
            'speed_control',
            'loud_control',
            'interceptions',
            'purity',
            'neg_words',
            'operator_positive',
            'client_positive',
            'operator_negative',
            'client_negative',
            'crit_words',
            'neg_words',
            'par_words',
            'client_int_words',
            'client_answ_words'
        ])
        df_export.to_csv(export_path+'/'+request_user.first_name+'.csv', index=False)
        
@login_required(login_url='/login/')
def index(request):
    request_user = request.user
    if 'critical-calls' in request.path:
        managers = CustomUser.objects.filter(supermanager = request_user, is_active = True)
        critical_calls = {}
        i = 0
        for manager in managers:
            calls = Call.objects.filter(user = manager, critical = True)
            for call in calls:
                salt = call.record.name.split('/')[1]
                critical_calls[i] = {
                    'manager': manager.get_full_name(),
                    'id': call.id,
                    'path': '/manager-' + str(manager.id) + '/post_analyze/' + salt,
                    'name': call.name,
                    'date': call.start_date,
                    'time': call.time,
                    'volume': call.critical_volume,
                    'script_following': call.critical_script_following,
                    'loud_control': call.critical_loud_control,
                    'speed_control': call.critical_speed_control,
                    'speech_purity': call.critical_speech_purity,
                    'interceptions': call.critical_interceptions,
                    'crit_words': call.critical_crit_words,
                    'neg_words': call.critical_neg_words,
                    'emotional_negative_operator': call.critical_emotional_negative_operator,
                    'emotional_negative_client': call.critical_emotional_negative_client
                }
                i += 1
        json_obj = {'critical_calls': critical_calls}
        return JsonResponse(json_obj)
    context = {
        'balance': request_user.company.balance_minutes if request_user.company.balance_minutes else '∞'
    }
    return render(request, 'frontend/dashboard.html', context)

@login_required(login_url='/login/')
def analytics(request):
    request_user = request.user
    my_thread = threading.Thread(target=prepare_export, args=(None,request_user,))
    my_thread.start()
    context = {
        'id': request_user.id,
        'name': request_user.first_name
    }
    return render(request, 'frontend/managers.html', context)

@login_required(login_url='/login/')
def calls(request, manager_id):
    request_user = request.user
    manager = CustomUser.objects.get(id = manager_id)
    if manager.supermanager != request_user:
        return HttpResponseForbidden()
    if request.method == 'POST':
        if 'upload' in request.path:
            post_start = datetime_tz()
            if 'time' in request.POST:
                if 'call_id' in request.POST:
                    call = Call.objects.get(id = request.POST['call_id'])
                    call.debug_time_uploaded_spent = request.POST['time']
                    call.save()
                else:
                    calls = Call.objects.filter(user = manager)
                    for call in calls:
                        call.debug_time_calls_showing = request.POST['time']
                        call.save()
                return JsonResponse({'status': 'ok'})
            form = UploadForm(request.POST, request.FILES)
            if form.is_valid():
                company = request_user.company
                if not company.limit is None and company.uploaded_amount >= company.limit:
                    return JsonResponse({'status': 'Limit for company'}, status = 403)
                if not request_user.limit is None and request_user.uploaded_amount >= request_user.limit:
                    return JsonResponse({'status': 'Limit for user'}, status = 403)
                file = request.FILES['file']
                call = Call(record = file, name = file.name, user = manager, reverse = request.POST['reverse'])
                call.debug_time_uploaded = datetime_tz()
                call.save()
                
                path_to_file = os.path.join(basedir, str(call.record))
                
                status, time, norm_time, size = get_duration(path_to_file)
                if not company.balance_minutes is None:
                    balance_time = company.balance_minutes * 60 + company.balance_seconds
                    time_seconds = int(norm_time)
                    if balance_time < time_seconds:
                        call.delete()
                        return JsonResponse({'status': 'Limit for time'}, status = 403)
                    else:
                        balance_time -= time_seconds
                        company.balance_minutes = balance_time // 60
                        company.balance_seconds = balance_time % 60
                call.status = status
                call.time = time
                call.size = size
                call.save()
                company.uploaded_amount += 1
                company.save()
                request_user.uploaded_amount += 1
                request_user.save()
                manager.uploaded_amount += 1
                manager.save()
                
                number = list(Call.objects.filter(user = manager).order_by('id')).index(call)
                
                with open("/home/ubuntu/files_to_processing.txt", 'a') as file:
                    file.write(call.record.url + "\n")
                
                salt = call.record.name.split('/')[1]
                
                post_end = datetime_tz()
                post_duration = (post_end - post_start).total_seconds() * 1000
                json_obj = {
                    'id': call.id,
                    'number': number,
                    'name': call.name,
                    'date': call.start_date,
                    'time': call.time,
                    'status': call.status,
                    'duration': post_duration
                }
                return JsonResponse(json_obj)
            
        elif 'remove' in request.path:
            calls_id = eval(request.POST['calls_id'])
            for call_id in calls_id:
                call = Call.objects.get(id = call_id)
                salt = call.record.name.split('/')[1]
                record_path = records_path(salt)
                decrypted_path = decrypting_path(salt)
                shutil.rmtree(record_path)
                shutil.rmtree(decrypted_path)
                call.delete()
            my_thread = threading.Thread(target=recalc_summary, args=(manager,))
            my_thread.start()
            return JsonResponse({'status': 'ok'})
        
        elif 'calls' in request.path:
            if 'update' in request.POST['type']:
                json_struct = {
                        'critical': manager.critical,
                        'purity': manager.purity,
                        'speed_podstr': manager.speed_podstr,
                        'loud_podstr': manager.loud_podstr,
                        'script_following': manager.script_following
                    }
                return JsonResponse(json_struct)
            
            elif 'order' in request.POST['type']:
                return JsonResponse(get_order_call(manager))
            
            elif 'stats' in request.POST['type']:
                calls_id = eval(request.POST['calls_id'])
                json_struct = {}
                i = int(request.POST['start_num'])
                for call_id in calls_id:
                    call = Call.objects.get(id = call_id)
                    my_thread = threading.Thread(target=calc_call, args=(call.id, request_user,))
                    my_thread.start()
                    salt = call.record.name.split('/')[1]
                    json_struct[i] = {
                            'id': call.id,
                            'name': call.name,
                            'date': call.start_date,
                            'time': call.time,
                            'status': call.status,
                            'critical': call.critical,
                            'interceps': call.interceptions if call.interceptions != '-' else '‒',
                            'script_following': call.script_following if call.script_following != '-' else '‒',
                            'purity': call.purity if call.purity != '-' else '‒',
                            'vol': call.volume if call.volume != '-' else '‒',
                            'path': salt
                        }
                    i += 1
                    if not call.debug_time_uploaded is None:
                        if call.debug_time_first_stats_showing is None and call.status == 'Обработано':
                            stats_time = (datetime_tz() - call.debug_time_uploaded).total_seconds() * 1000
                            call.debug_time_first_stats_showing = int(stats_time)
                            call.save()
                return JsonResponse(json_struct)
        
    else:        
        count = count_calls(manager)
        context = get_manager(manager)
        context['form'] = UploadForm()
        return render(request, 'frontend/calls.html', context)

@login_required(login_url='/login/')
def post_analyze(request, manager_id, salt):
    request_user = request.user
    manager = CustomUser.objects.get(id = manager_id)
    if manager.supermanager != request_user:
        return HttpResponseForbidden()
    salt_clear = salt.split('.')[0]
    path = records_path(salt_clear)
    file_path = decrypting_path(salt_clear)
    name = '/'+os.listdir(path)[0] if os.path.isdir(path) else ''
    call = Call.objects.get(record = (path+name)[28:])
    if 'time' in request.POST:
        call.debug_time_postanalyze_spent = request.POST['time']
        call.save()
        return JsonResponse({'status': 'ok'})
    if '.speak-model' in salt:
        dictionaries = [
            get_phrases(request_user, manager),
            request_user.par_words,
            request_user.crit_words,
            request_user.neg_words,
            request_user.client_pos_words,
            request_user.client_neg_words
        ]
        data = get_data(salt_clear)
        return JsonResponse(data)
    
    elif '.reverse' in salt:
        call.reverse = not call.reverse
        call.save()
        return JsonResponse({'status': 'ok'})
    
    elif '.update-text_emotion' in salt:
        moderator_suffix = 'unmoderated'
        if request_user.is_staff or request.COOKIES.get('moderator'):
            moderator_suffix = 'moderated'
        
        df_result = pd.read_csv(file_path+'/result.csv')
        new_num = int(request.POST['new_num'])
        new_text = ''
        new_emotion = ''
        prev_text = df_result.at[new_num, 'normalized_text']
        prev_emotion = df_result.at[new_num, 'emotion_result']
        if 'new_text' in request.POST:
            new_text = request.POST['new_text']
            if request.COOKIES.get('moderator'):
                df_result.at[new_num, 'normalized_text'] = new_text
                new_result = infoExtractor.recognize_text_and_params_on_segment(new_text, df_result.at[new_num, 'duration'])
                for key in new_result:
                    df_result.at[new_num, key] = new_result[key] if new_result[key] == new_result[key] else '‒'
            else:
                df_result.at[new_num, 'denormalized_text'] = new_text
        elif 'new_emotion' in request.POST:
            new_emotion = request.POST['new_emotion']
            df_result.at[new_num, 'emotion_result'] = new_emotion
        else:
            df_result = df_result.drop(new_num)
        df_result.to_csv(file_path+'/result.csv', index=False)
        
        edited_path = os.path.join(basedir, 'edited', moderator_suffix, salt_clear)
        if not os.path.isdir(edited_path):
            os.makedirs(edited_path)
        if not os.path.isfile(edited_path+'/edit.csv'):
            df = pd.DataFrame(columns = ['channel', 'start', 'end', 'original text', 'previous text', 'new text', 'previous emotion', 'new emotion'])
            df.to_csv(edited_path+'/edit.csv', index=False)
        df_edit = pd.read_csv(edited_path+'/edit.csv')
        df_speech = pd.read_csv(file_path+'/speech.csv')
        row = [
            df_speech.at[new_num, 'channel'],
            df_speech.at[new_num, 'start'],
            df_speech.at[new_num, 'end'],
            df_speech.at[new_num, 'text'],
            prev_text,
            new_text,
            prev_emotion,
            new_emotion
        ]
        df_edit.loc[len(df_edit)] = row
        df_edit.to_csv(edited_path+'/edit.csv', index=False)
        my_thread = threading.Thread(target=prepare_export, args=(call,request_user,))
        my_thread.start()
        return JsonResponse({'status': 'ok'})
    
    my_thread = threading.Thread(target=prepare_export, args=(call,request_user,))
    my_thread.start()
    context = {
        'id': call.id,
        'path': salt,
        'name': name,
        'filename': call.name,
        'duration': call.time,
        'reverse': call.reverse,
        
        'hsv': 'none' if request_user.hide_speech_volume else '',
        'hsf': 'none' if request_user.hide_script_following else '',
        'hlp': 'none' if request_user.hide_loud_podstr else '',
        'hsp': 'none' if request_user.hide_speed_podstr else '',
        'hspu': 'none' if request_user.hide_speech_purity else '',
        'hi': 'none' if request_user.hide_interception else '',
        'hcw': 'none' if request_user.hide_critical_words else '',
        'hnw': 'none' if request_user.hide_negative_words else '',
        'hpc': 'none' if request_user.hide_positive_count else '',
        'hnc': 'none' if request_user.hide_negative_count else ''
    }
    return render(request, 'frontend/post_analyze.html', context)

@login_required(login_url='/login/')
def real_time(request, manager_id, salt):
    request_user = request.user
    manager = CustomUser.objects.get(id = manager_id)
    if manager.supermanager != request_user:
        return HttpResponseForbidden()
    if ('.speak-model' in salt):
        salt = salt.replace('.speak-model', '')
        file_path = decrypting_path(salt)
        dictionaries = [
            get_phrases(request_user, manager),
            request_user.par_words
        ]
        data = get_data(salt)
        return JsonResponse(data)
    path = records_path(salt)
    name = '/'+os.listdir(path)[0] if os.path.isdir(path) else ''
    call = Call.objects.get(record = (path+name)[28:])
    context = {
        'path': salt,
        'name': name,
        'duration': call.time,
        'reverse': call.reverse
    }
    return render(request, 'frontend/real_time.html', context)

@login_required(login_url='/login/')
def dictionaries(request):
    request_user = request.user
    form = WordsForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            word = form.cleaned_data['word']
            form_type = -1
            action = ''
            # Добавление слова
            if 'add' in request.POST['action']:
                action = 'add'
                if 'operator_crit_form' in request.POST['name']:
                    if word not in request_user.crit_words:
                        form_type = 0
                        request_user.crit_words += [word]
                elif 'operator_neg_form' in request.POST['name']:
                    if word not in request_user.neg_words:
                        form_type = 1
                        request_user.neg_words += [word]
                elif 'operator_par_form' in request.POST['name']:
                    if word not in request_user.par_words:
                        form_type = 2
                        request_user.par_words += [word]
                elif 'client_pos_form' in request.POST['name']:
                    if word not in request_user.client_pos_words:
                        form_type = 3
                        request_user.client_pos_words += [word]
                elif 'client_neg_form' in request.POST['name']:
                    if word not in request_user.client_neg_words:
                        form_type = 4
                        request_user.client_neg_words += [word]
            # Удаление слова
            else:
                action = 'remove'
                if 'operator_crit_form' in request.POST['name']:
                    if word in request_user.crit_words:
                        form_type = 0
                        request_user.crit_words.remove(word)
                elif 'operator_neg_form' in request.POST['name']:
                    if word in request_user.neg_words:
                        form_type = 1
                        request_user.neg_words.remove(word)
                elif 'operator_par_form' in request.POST['name']:
                    if word in request_user.par_words:
                        form_type = 2
                        request_user.par_words.remove(word)
                elif 'client_pos_form' in request.POST['name']:
                    if word in request_user.client_pos_words:
                        form_type = 3
                        request_user.client_pos_words.remove(word)
                elif 'client_neg_form' in request.POST['name']:
                    if word in request_user.client_neg_words:
                        form_type = 4
                        request_user.client_neg_words.remove(word)
                        
            my_thread = threading.Thread(target=recalc_calls, args=(request_user,))
            my_thread.start()            
            request_user.save()
            json_obj = {'word': word, 'type': form_type, 'action': action}
            return JsonResponse(json_obj)
        
    # Запрошен список слов
    if 'words-list' in request.path:
        json_obj = {
            'crit_words': request_user.crit_words,
            'neg_words': request_user.neg_words,
            'par_words': request_user.par_words,
            'client_pos_words': request_user.client_pos_words,
            'client_neg_words': request_user.client_neg_words
        }
        return JsonResponse(json_obj)

    context = {'form': form}
    return render(request, 'frontend/dictionaries.html', context)
    
@login_required(login_url='/login/')
def scripts(request, script_id = ''):
    request_user = request.user
    company = request_user.company
    form = AddScriptForm(request.POST or None)
    if request.method == 'POST':
        script = None
        name = request.POST['name']
        department = Department.objects.filter(company = company).get(name = request.POST['department'])
        product = Product.objects.filter(company = company).get(name = request.POST['product'])
        if 'add' in request.POST['method']:
            if product == '':
                product = Script._meta.get_field('product').get_default()

            script = Script(
                name = name,
                manager = request_user,
                department = department,
                product = product
            )
            script.save()

            for phrase in eval(request.POST['phrases']):
                phrase = Phrase(
                    text = phrase['text'],
                    script = script,
                    number = int(phrase['number']),
                    analogs = phrase['analogs']
                )
                phrase.save()
        elif 'edit' in request.POST['method']:
            script_id = request.POST['id']
            script = Script.objects.get(id = script_id)
            if script.manager != request_user:
                return HttpResponseForbidden()
            if 'active' in request.POST['method']:
                script_changed_status = []
                if request.POST['active'] == 'true':
                    scripts_other = Script.objects.filter(department = department, product = product, active = True)
                    for script_other in scripts_other:
                        script_other.active = False
                        script_other.save()
                        script_changed_status.append({'id': script_other.id, 'active': script_other.active})
                script.active = True if request.POST['active'] == 'true' else False
                script.save()
                script_changed_status.append({'id': script.id, 'active': script.active})
                return JsonResponse(script_changed_status, safe = False)
            else:
                script.name = name
                script.department = department
                script.product = product
                script.save()

                phrases_remove = list(Phrase.objects.filter(script = script).values_list('id', flat=True))
                for phrase_post in eval(request.POST['phrases']):
                    phrase = None
                    text = phrase_post['text']
                    number = int(phrase_post['number'])
                    analogs = phrase_post['analogs']
                    if phrase_post['id'] == '':
                        phrase = Phrase(
                            text = text,
                            script = script,
                            number = number,
                            analogs = analogs
                        )
                    else:
                        phrase_id = int(phrase_post['id'])
                        phrase = Phrase.objects.get(id = phrase_id)
                        phrase.text = text
                        phrase.number = number
                        phrase.analogs = analogs
                        phrases_remove.remove(phrase_id)
                    phrase.save()
                for id_remove in phrases_remove:
                    Phrase.objects.get(id = id_remove).delete()
            
        my_thread = threading.Thread(target=recalc_calls, args=(request_user,))
        my_thread.start()
        return JsonResponse(get_script(script))
        
    if request.method == 'DELETE':
        script = Script.objects.get(id = script_id)
        if script.manager != request_user:
            return HttpResponseForbidden()
        script.delete()
        
        my_thread = threading.Thread(target=recalc_calls, args=(request_user,))
        my_thread.start()
        return JsonResponse({'status': 'ok'})
        
    if 'words-list' in request.path:
        scripts = get_scripts(request_user)
        json_struct = []
        for script in scripts:
            json_struct += [get_script(script)]
        json_obj = {'scripts': json_struct}
        return JsonResponse(json_obj)
    
    departments = get_departments(request_user)
    products = get_products(request_user)
    context = {
        'departments': departments,
        'products': products,
        'form': form
    }
    return render(request, 'frontend/scripts.html', context)
    
@login_required(login_url='/login/')
def settings(request):
    request_user = request.user
    if request.method == 'POST':
        if 'hsv' in request.POST['name']:
            request_user.hide_speech_volume = True if request.POST['value'] == 'T' else False
        elif 'hsf' in request.POST['name']:
            request_user.hide_script_following = True if request.POST['value'] == 'T' else False
        elif 'hlp' in request.POST['name']:
            request_user.hide_loud_podstr = True if request.POST['value'] == 'T' else False
        elif 'hspu' in request.POST['name']:
            request_user.hide_speech_purity = True if request.POST['value'] == 'T' else False
        elif 'hsp' in request.POST['name']:
            request_user.hide_speed_podstr = True if request.POST['value'] == 'T' else False
        elif 'hi' in request.POST['name']:
            request_user.hide_interception = True if request.POST['value'] == 'T' else False
        elif 'hcw' in request.POST['name']:
            request_user.hide_critical_words = True if request.POST['value'] == 'T' else False
        elif 'hnw' in request.POST['name']:
            request_user.hide_negative_words = True if request.POST['value'] == 'T' else False
        elif 'hpc' in request.POST['name']:
            request_user.hide_positive_count = True if request.POST['value'] == 'T' else False
        elif 'hnc' in request.POST['name']:
            request_user.hide_negative_count = True if request.POST['value'] == 'T' else False
        
        if 'cnec' in request.POST['name']:
            request_user.critical_negative_emotions_client = request.POST['value']
        elif 'cneo' in request.POST['name']:
            request_user.critical_negative_emotions_operator = request.POST['value']
        elif 'csv' in request.POST['name']:
            request_user.critical_speech_volume = request.POST['value']
        elif 'csf' in request.POST['name']:
            request_user.critical_script_following = request.POST['value']
        elif 'clp' in request.POST['name']:
            request_user.critical_loud_podstr = request.POST['value']
        elif 'cspu' in request.POST['name']:
            request_user.critical_speech_purity = request.POST['value']
        elif 'csp' in request.POST['name']:
            request_user.critical_speed_podstr = request.POST['value']
        elif 'cial' in request.POST['name']:
            request_user.critical_interception_all = request.POST['value']
        elif 'ciav' in request.POST['name']:
            request_user.critical_interception_avg = request.POST['value']
        elif 'ccwal' in request.POST['name']:
            request_user.critical_critical_words_all = request.POST['value']
        elif 'ccwav' in request.POST['name']:
            request_user.critical_critical_words_avg = request.POST['value']
        elif 'cnwal' in request.POST['name']:
            request_user.critical_negative_words_all = request.POST['value']
        elif 'cnwav' in request.POST['name']:
            request_user.critical_negative_words_avg = request.POST['value']
        elif 'chcal' in request.POST['name']:
            request_user.critical_hints_count_all = request.POST['value']
        elif 'chcav' in request.POST['name']:
            request_user.critical_hints_count_avg = request.POST['value']
        request_user.save()
        my_thread = threading.Thread(target=recalc_critical, args=(request_user,))
        my_thread.start()
        return JsonResponse({'status': 'ok'})
    else:
        context = {
            'hsv': request_user.hide_speech_volume,
            'hsf': request_user.hide_script_following,
            'hlp': request_user.hide_loud_podstr,
            'hsp': request_user.hide_speed_podstr,
            'hspu': request_user.hide_speech_purity,
            'hi': request_user.hide_interception,
            'hcw': request_user.hide_critical_words,
            'hnw': request_user.hide_negative_words,
            'hpc': request_user.hide_positive_count,
            'hnc': request_user.hide_negative_count,
            
            'cnec': request_user.critical_negative_emotions_client,
            'cneo': request_user.critical_negative_emotions_operator,
            'csv': request_user.critical_speech_volume,
            'csf': request_user.critical_script_following,
            'clp': request_user.critical_loud_podstr,
            'csp': request_user.critical_speed_podstr,
            'cspu': request_user.critical_speech_purity,
            'cial': request_user.critical_interception_all,
            'ciav': request_user.critical_interception_avg,
            'ccwal': request_user.critical_critical_words_all,
            'ccwav': request_user.critical_critical_words_avg,
            'cnwal': request_user.critical_negative_words_all,
            'cnwav': request_user.critical_negative_words_avg,
            'chcal': request_user.critical_hints_count_all,
            'chcav': request_user.critical_hints_count_avg
        }
        return render(request, 'frontend/settings.html', context)

@login_required(login_url='/login/')
def team(request, type = '', data = ''):
    request_user = request.user
    company = request_user.company
    form = AddManagerForm(request.POST or None)
    if request.method == 'POST':
        if request.POST['type'] == 'manager':
            if form.is_valid():
                first_name = request.POST['first_name']
                last_name = request.POST['last_name']
                department = Department.objects.filter(company = company).get(name = request.POST['department'])
                status = 'active'
                if 'add' in request.POST['method']:
                    randstr = uuid4().hex
                    manager = CustomUser.objects.create_user(randstr, randstr+'@test.ru', randstr)
                    manager.company = company
                    manager.supermanager = request_user
                else:
                    manager_id = request.POST['id']
                    manager = CustomUser.objects.get(id = manager_id)
                    if manager.supermanager != request_user:
                        return HttpResponseForbidden()
                    status = request.POST['status']
                manager.first_name = first_name
                manager.last_name = last_name
                manager.department = department
                manager.is_active = True if (status == 'true') else False;
                
                manager.product.clear()
                names = request.POST['product'].split(',')
                for name in names:
                    if (request.POST['product'] == ''): name = Product._meta.get_field('name').get_default()
                    product = Product.objects.filter(company = company).get(name = name)
                    manager.product.add(product)
                manager.save()
                return JsonResponse(get_manager(manager))
        else:
            name = request.POST['first_name']
            old_name = request.POST['last_name']
            if request.POST['type'] == 'department':
                if name == Department._meta.get_field('name').get_default():
                    return HttpResponseBadRequest()
                if 'add' in request.POST['method']:
                    department = Department(name = name, company = company)
                    department.save()
                else:
                    department = Department.objects.filter(company = company).get(name = old_name)
                    department.name = name
                    department.save()
            if request.POST['type'] == 'product':
                if name == Product._meta.get_field('name').get_default():
                    return HttpResponseBadRequest()
                if 'add' in request.POST['method']:
                    product = Product(name = name, company = company)
                    product.save()
                else:
                    product = Product.objects.filter(company = company).get(name = old_name)
                    product.name = name
                    product.save()
            return JsonResponse({'status': 'ok'})
        
    if request.method == 'DELETE':
        if type == 'manager':
            manager = CustomUser.objects.get(id = data)
            if manager.supermanager != request_user:
                return HttpResponseForbidden()
            manager.delete()
        elif type == 'department':
            department_undef = Department.objects.filter(company = company).get(
                name = Department._meta.get_field('name').get_default()
            )
            department = Department.objects.filter(company = company).get(name = data)
            managers_with_department = CustomUser.objects.filter(company = company).filter(department = department)
            for manager_with_department in managers_with_department:
                manager_with_department.department = department_undef
                manager_with_department.save()
            scripts_with_department = Script.objects.filter(company = company).filter(department = department)
            for script_with_department in scripts_with_department:
                script_with_department.department = department_undef
                script_with_department.save()
            department.delete()
        elif type == 'product':
            product_undef = Product.objects.filter(company = company).get(
                name = Product._meta.get_field('name').get_default()
            )
            product = Product.objects.filter(company = company).get(name = data)
            managers_with_product = CustomUser.objects.filter(company = company).filter(product = product)
            for manager_with_product in managers_with_product:
                manager_with_product.product.remove(product)
                if manager_with_product.product.count() is 0:
                    manager_with_product.product.set([product_undef])
                    manager_with_product.save()
            scripts_with_product = Script.objects.filter(company = company).filter(product = product)
            for script_with_product in scripts_with_product:
                script_with_product.product = product_undef
                script_with_product.save()
            product.delete()
        return JsonResponse({'status': 'ok'})
        
    if 'managers-list' in request.path:
        managers = CustomUser.objects.filter(supermanager = request_user).order_by('department', 'id')
        json_struct = []
        for manager in managers:
            json_struct += [get_manager(manager)]
            my_thread = threading.Thread(target=recalc_summary, args=(manager,))
            my_thread.start()
        json_obj = {'managers': json_struct}
        return JsonResponse(json_obj)
    
    departments = get_departments(request_user)
    products = get_products(request_user)
    context = {
        'departments': departments,
        'products': products,
        'form': form
    }
    return render(request, 'frontend/team.html', context)

def logout_view(request):
    logout(request)
    return redirect('/login/')

def login_view(request):
    form = CustomAuthenticationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        elogin = form.cleaned_data['login']
        moderator = False
        if '-moderator' in elogin:
            moderator = True
            response = HttpResponse("moderator")
            response.set_cookie('moderator', 'True')
            elogin = elogin[:-10]
        try:
            user = CustomUser.objects.get(email = elogin)
        except CustomUser.DoesNotExist:
            try:
                user = CustomUser.objects.get(username = elogin)
            except CustomUser.DoesNotExist:
                user = None
        if user is not None:
            request_user = authenticate(username = user.username, password = form.cleaned_data['password'])
            login(request, request_user)
#             return redirect(request.GET.get('next')) Редирект на запрашиваемую страницу
            if moderator:
                return response
            return redirect('/')
        else:
            return HttpResponse('Неверный логин или пароль')
        
    context = {'form': form}
    return render(request, 'auth/login.html', context)

@login_required(login_url='/login/')
def registration_view(request):
    request_user = request.user
    if (request_user.is_staff):
        form = CustomRegistrationForm(request.POST or None)
        if request.method == 'POST' and form.is_valid():
            manager = CustomUser.objects.create_user(form.cleaned_data['login'], form.cleaned_data['email'], form.cleaned_data['password'])
            manager.save()
            json_obj = {
                'id': manager.id
            }
            return JsonResponse(json_obj) 
            
        context = {'form': form}
        return render(request, 'auth/registration.html', context)
    else:
        raise Http404()

def recalc():
    for manager in CustomUser.objects.all():
        recalc_calls(manager)
        
@login_required(login_url='/login/')
def recalc_view(request):
    request_user = request.user
    if (request_user.is_superuser):
        my_thread = threading.Thread(target=recalc, args=())
        my_thread.start()
        return JsonResponse({'status': 'ok'})
    else:
        raise Http404()
        
def migrate():
    for manager in CustomUser.objects.all():
        if manager.scripts:
            script = Script(
                name = 'Скрипт #1',
                manager = manager,
                department = CustomUser._meta.get_field('department').get_default(),
                product = Script._meta.get_field('product').get_default()
            )
            script.save()
            
            i = 0
            for text in manager.scripts:
                phrase = Phrase(
                    text = text,
                    script = script,
                    number = i,
                )
                phrase.save()
                i += 1
        
@login_required(login_url='/login/')
def migrate_view(request):
    request_user = request.user
    if (request_user.is_superuser):
#         my_thread = threading.Thread(target=migrate, args=())
#         my_thread.start()
        return JsonResponse({'status': 'ok'})
    else:
        raise Http404()
        