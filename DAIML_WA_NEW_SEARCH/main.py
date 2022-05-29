import torch
import yaml
from DAIML_WA_NEW_SEARCH.word_analysis.word_analysis_models import WordAnalysisModels, search_key_words, not_replace_forward
import numpy as np
import matplotlib.pyplot as plt
import time
import os
import glob
import pandas as pd
from tqdm import tqdm
from hyperpyyaml import load_hyperpyyaml
import re
from collections import Counter
import functools
import operator

class InfoExtractor:
    def __init__(self, with_punc=True):
        with open(r'/home/ubuntu/DarwinAI/DAIML_WA_NEW_SEARCH/args.yaml') as file:
            args = load_hyperpyyaml(file)
        self.channel_name = args['channel_name']
        self.wordAnalysisModels = WordAnalysisModels(args)
        self.int_t_start = args['int_t_start']
        self.int_t_stop = args['int_t_stop']
        self.vad_padding = args['vad_padding']
        self.columns = args['columns']
        self.time_format = args['time_format']
        self.channel_name = args['channel_name']
        self.numbers_float = args['numbers_float']
        self.sprs_history_iters = args['sprs_history_iters']
        self.spr_mean = args['sprs_mean']
        self.emo_keys = args['emo_keys']
        self.thr_emo_text = args['thr_emo_text']
        self.thr_emo_voice = args['thr_emo_voice']
        self.args = args
        self.with_punc = with_punc
        
    def recognize_text_and_params_on_segment(self, text, duration):
        normalized_text =  self.wordAnalysisModels.prepare_text_with_punc(text)
        if self.with_punc:
            normalized_text_with_punc =  self.wordAnalysisModels.prepare_text_with_punc(text)
            normalized_text_with_punc = self.wordAnalysisModels.add_spaces_before_punc(text)
        else:
            normalized_text_with_punc =  normalized_text
        denormalized_text = self.wordAnalysisModels.denormalize(normalized_text_with_punc, with_punc=self.with_punc)
        denormalized_text_without_punc = self.wordAnalysisModels.remove_punc(denormalized_text)
        spr, symbols = self.wordAnalysisModels.symbols_per_min(normalized_text, duration)
        wpr, words = self.wordAnalysisModels.words_per_min(normalized_text, duration)
        results_speech = {'normalized_text': text, 'denormalized_text': denormalized_text,
                          'denormalized_text_without_punc': denormalized_text_without_punc,
                          'spr': spr, 'symbols': symbols, 'wpr': wpr, 'words': words}
        return results_speech
    

    def search_interseptions(self, starts_speech, ends_speech, starts, ends, channel_num):
        interception = 0
        starts[channel_num] = starts_speech
        ends[channel_num] = ends_speech
        start_new_0 = starts[0] + self.vad_padding
        start_new_1 = starts[1] + self.vad_padding
        end_new_0 = ends[0] - self.vad_padding
        end_new_1 = ends[1] - self.vad_padding
        if start_new_0 > 0 and end_new_1 > 0 and channel_num == 0:
            if start_new_0 < end_new_1 and end_new_1 - self.int_t_start > start_new_0 and end_new_0 - start_new_0 > 2 and end_new_1 - self.int_t_stop < start_new_0:
                interception = 1
        if start_new_1 > 0 and end_new_0 > 0 and channel_num == 1: 
            if start_new_1 < end_new_0 and end_new_0 - self.int_t_start > start_new_1 and end_new_1 - start_new_1 > 2 and end_new_0 - self.int_t_stop < start_new_1: 
                interception = 1
                
        return {'interception': interception}, starts, ends
    
    
    def calculate_volume_of_speech(self, start, end, vol_old):
        time_arr = np.arange(1, safe_to_int(end+1) - safe_to_int(start) + 1, 1.0)
        if time_arr.shape[-1] > 1:
            time_arr -= start % 1
            time_arr[-1] -= 1 - end % 1
        else:
            time_arr[0] = end - start
        return time_arr + vol_old        
   
    def calculate_spr_table(self, duration, df_results, channels):
        spr_values = np.empty((df_results.channel.nunique(), duration))
        spr_values_mean = np.empty((df_results.channel.nunique(), duration))
        volume_values = np.empty((df_results.channel.nunique(), duration))
        spr_values[:] = np.nan
        spr_values_mean[:] = np.nan
        volume_values[:] = np.nan
        columns_spr = ['time']
        columns_spr += ['0_spr', '1_spr', '0_spr_avg', '1_spr_avg', '0_volume',
                        '1_volume'] if channels == 2 else ['0_spr', '0_spr_avg', '0_volume', ]
        df_spr = pd.DataFrame(data = np.zeros((duration, len(columns_spr))), columns=columns_spr)
        for channel in df_results.channel.unique():
            df_channel = df_results[df_results.channel == channel]
            starts_speech = df_channel.start.to_numpy()
            ends_speech = df_channel.end.to_numpy()
            sprs =  df_channel.spr.to_numpy()
            sprs_mean =  df_channel.spr_mean.to_numpy()
            volumes = df_channel.volume.to_numpy()
            durations = df_channel.duration.to_numpy()
            for start, end, spr, spr_mean, dur, vol in zip(starts_speech, ends_speech, sprs, sprs_mean, durations, volumes): 
                spr_values[safe_to_int(channel)][safe_to_int(start) : safe_to_int(end) + 1] = spr
                spr_values_mean[safe_to_int(channel)][safe_to_int(start) : safe_to_int(end) + 1] = spr_mean                    
                volume_of_speech = self.calculate_volume_of_speech(start, end, vol)
                if volume_of_speech.shape[-1] > volume_values[:, safe_to_int(start):safe_to_int(end)+1].shape[-1]:
                    volume_of_speech = volume_of_speech[:volume_values[:, safe_to_int(start):safe_to_int(end)+1].shape[-1]]

                volume_values[safe_to_int(channel)][safe_to_int(start) : safe_to_int(end)+1] = volume_of_speech 
          
        df_spr.time = np.arange(0, duration, 1.0)
        if channels == 2:
            df_spr['0_spr'] = spr_values[0]
            df_spr['1_spr'] = spr_values[1]
            df_spr['0_spr_avg'] = spr_values_mean[0]
            df_spr['1_spr_avg'] = spr_values_mean[1]
            df_spr['0_volume'] = volume_values[0]
            df_spr['1_volume'] = volume_values[1]
        else:
            df_spr['0_spr'] = spr_values[0]
            df_spr['0_spr_avg'] = spr_values_mean[0]
            df_spr['0_volume'] = volume_values[0]
        
        
        df_spr = df_spr.fillna(method='ffill')
        df_spr['0_volume'] = df_spr['0_volume'].fillna(0)
        if channels == 2:
            df_spr['1_volume'] = df_spr['1_volume'].fillna(0)
            df_spr['0_vol_part'] = np.round(100 * (df_spr['0_volume'] / (df_spr['0_volume'] + df_spr['1_volume'])))
            df_spr['1_vol_part'] = 100 - df_spr['0_vol_part']     
        else:
            df_spr['0_vol_part'] = 100
        
        
        return df_spr
    
    def min_max(self, x, y, dim):
        return np.min(np.array([x, y]), axis=dim) / np.max(np.array([x, y]), axis=dim)
    
    def emo_text_trans(self, x):
        if x > self.thr_emo_text:
            return 'positive'
        elif x < 1 - self.thr_emo_text:
            return 'negative'
        else:
            return 'neutral'
        
    def emo_voice_trans(self, x, emo='positive'):
        if x > self.thr_emo_text:
            return emo
        else:
            return 'neutral'
        
    def emo_get_result(self, row):
        if row['emotion_voice'] != 'neutral' or row['emotion_text'] != 'neutral':
            if row['emotion_voice'] != 'neutral':
                return row['emotion_voice']
            else:
                return row['emotion_text']
        else:
            return row['emotion_text']
            
    def extract(self, df_speech_path, df_loud_path, df_clear_score_path, type_='out'):
        assert type_ in ['out', 'in', 'unknown']
        df_results = pd.DataFrame(data=None, columns=self.columns)
        df = pd.read_csv(df_speech_path)
        df_loud = pd.read_csv(df_loud_path)
        df_clear_score = pd.read_csv(df_clear_score_path)
        
        if df.channel.nunique() == 1:
            df.channel = 0 
        channels = df.channel.nunique()
        if channels == 2:
            starts = [-1, -1]
            ends = [-1, -1]
          
        for i_segment in range(df.shape[0]):
            channel_num = df.iloc[i_segment].channel
            starts_speech = df.iloc[i_segment].start
            ends_speech = df.iloc[i_segment].end
            text = df.iloc[i_segment].text
            duration = ends_speech - starts_speech
            
            start_info = {'channel': channel_num, 'start': starts_speech, 'end': ends_speech}
            speech_recognition_results = self.recognize_text_and_params_on_segment(text, duration)
                             
            if channels == 2:
                interseptions, starts, ends = self.search_interseptions(starts_speech, ends_speech, starts,
                                                                        ends, safe_to_int(channel_num))
            else:
                interseptions = {'interception': 0}

            dict_all_params = dict(start_info, **speech_recognition_results)
            dict_all_params.update(interseptions)
            df_results = df_results.append(dict_all_params, ignore_index=True)   
        
        df_results['duration'] = df_results['end'] - df_results['start']
        for emo_key in self.emo_keys:
            df_results[emo_key] = df[emo_key]
            
        df_results['emotion_text'] = df_results['positive_text'].apply(self.emo_text_trans)
        df_results['emotion_voice'] = df_results['positive_voice'].apply(lambda x: self.emo_voice_trans(x, 'positive'))
        df_results['emotion_voice'] = df_results['negative_voice'].apply(lambda x: self.emo_voice_trans(x, 'negative'))
        df_results['emotion_result'] = df_results.apply(self.emo_get_result, axis = 1)
        

        for channel in range(channels):
            df_results_channel = df_results[df_results.channel == channel]
            for j_row, i_row in enumerate(df_results_channel.index):
                df_results.at[i_row, 'spr_mean'] = df_results_channel.iloc[ : j_row].spr.median()
                df_results.at[i_row, 'volume'] = df_results_channel.iloc[ : j_row].words.sum()
        
        df_spr = self.calculate_spr_table(df_loud.shape[0], df_results, channels)
        df_results = df_results.round(self.numbers_float)
        df_loud = df_loud.round(self.numbers_float).fillna(method='ffill')
        df_clear_score = df_clear_score.round(self.numbers_float).fillna(method='ffill')
        df_spr = df_spr.round(self.numbers_float).fillna(method='ffill')
        
        for channel in range(channels):
            df_loud.loc[:, str(channel)] = df_loud.loc[:, str(channel)].clip(lower=self.args['loud_min'],
                                                                     upper=self.args['loud_max'])
            df_loud.loc[:, str(channel) + '_avg'] = df_loud.loc[:, str(channel) + '_avg'].clip(lower=self.args['loud_min'],
                                                                     upper=self.args['loud_max'])
            
            
            df_spr.loc[:, str(channel) + '_spr'] = df_spr.loc[:, str(channel) + '_spr'].clip(lower=self.args['spr_min'],
                                                                     upper=self.args['spr_max'])
            
            df_spr.loc[:, str(channel)+'_spr_avg'] = df_spr.loc[:,str(channel)+ '_spr_avg'].clip(lower=self.args['spr_min'],
                                                                     upper=self.args['spr_max'])
        
        if channels == 2:
            df_results.channel = df_results.channel.apply(lambda x: self.channel_name[2][type_][0] if x == 0 else self.channel_name[2][type_][1])
            
            df_loud['pod'] = self.min_max(df_loud['0_avg'].to_numpy(), df_loud['1_avg'].to_numpy(), 0)
            df_spr['pod'] = self.min_max(df_spr['0_spr_avg'].to_numpy(), df_spr['1_spr_avg'].to_numpy(), 0)
    
  
            df_loud = df_loud.rename(columns={'0': self.channel_name[2][type_][0],
                                            '1': self.channel_name[2][type_][1],
                                            '0_vsplesk': self.channel_name[2][type_][0] + '_vsplesk',
                                            '1_vsplesk': self.channel_name[2][type_][1] + '_vsplesk',
                                            '0_avg': self.channel_name[2][type_][0] + '_avg',
                                            '1_avg': self.channel_name[2][type_][1] + '_avg'})
          
            df_clear_score = df_clear_score.rename(columns={'0': self.channel_name[2][type_][0],
                                            '1': self.channel_name[2][type_][1]})
            
            df_spr = df_spr.rename(columns={'0_spr': self.channel_name[2][type_][0] + '_spr',
                                            '1_spr': self.channel_name[2][type_][1] + '_spr',
                                            '0_spr_avg': self.channel_name[2][type_][0] + '_spr_avg',
                                            '1_spr_avg': self.channel_name[2][type_][1] + '_spr_avg',
                                            '0_volume': self.channel_name[2][type_][0] + '_volume',
                                            '1_volume': self.channel_name[2][type_][1] + '_volume',
                                            '0_vol_part': self.channel_name[2][type_][0] +'_vol_part',
                                            '1_vol_part': self.channel_name[2][type_][1] + '_vol_part'})
        else:
            df_results.channel = self.channel_name[1]
            df_loud = df_loud.rename(columns={'0': self.channel_name[1],
                                            '0_vsplesk': self.channel_name[1] + '_vsplesk',
                                            '0_avg': self.channel_name[1] + '_avg'})
            
            df_clear_score = df_clear_score.rename(columns={'0': self.channel_name[1]})
            
            df_spr = df_spr.rename(columns={'0_spr': self.channel_name[1],
                                            '0_spr_avg': self.channel_name[1] + '_avg',
                                            '0_volume': self.channel_name[1] + '_volume',
                                            '0_vol_part': self.channel_name[1] +'_vol_part'})
            
                  
        df_results['format_start'] = df_results.start.apply(lambda x: time.strftime('%M:%S:',
                                                                          time.gmtime(x)) + str(np.round(x % 1, 2))[-1])
        df_results['format_end'] = df_results.end.apply(lambda x: time.strftime('%M:%S:',
                                                                      time.gmtime(x)) + str(np.round(x % 1, 2))[-1])
        
        info = self.get_info(df_results, df_loud, df_spr, df_clear_score)
        
        return df_results, df_loud, df_spr, df_clear_score, info

    
    def extract_parallel(self, df_speech_path):
        #df_speech_path, df_loud_path, df_clear_score_path = files[0], files[1], files[2]
        
        df_loud_path = df_speech_path[:-len('speech.csv')] + 'load.csv'
        df_clear_score_path = df_speech_path[:-len('speech.csv')] + 'clear.csv'
        
        return self.extract(df_speech_path, df_loud_path, df_clear_score_path)
       
    def get_info(self, df_results, df_loud, df_spr, df_clear_score):
        users = df_results.channel.unique()
        results = {}
        words_all_users = 0
        symbols_all_users = 0
        for i, user in enumerate(users):
            results_user = {}
            df_user = df_results[df_results.channel == user].reset_index(drop=True)
            results_user['words_all'] = safe_to_int(df_user.words.sum())
            words_all_users += results_user['words_all']
            results_user['symbols_all'] = safe_to_int(df_user.symbols.sum())
            symbols_all_users += results_user['symbols_all']
            results_user['words_per_minute'] = float(np.round(df_user.wpr.median(), 1))
            results_user['symbols_per_minute'] = float(np.round(df_user.spr.median(), 1))
            if len(users) is 1:
                results_user['interseps'] = '-'
            elif 'interception' in list(df_results):
                results_user['interseps'] = safe_to_int(df_user.interception.sum())
            else:
                results_user['interseps'] = '-'
               
            #потом изменить
            #results_user['emotional_eval'] =  safe_round(100 * (1 - df_results.negative_voice.median()))
            results_user['median_loud'] = df_loud[user].median()
            results_user['volume_of_speech'] = safe_round(df_spr.iloc[-1][user + '_vol_part'])
            results_user['speech_ch'] = df_clear_score[user].median()
                
            results[user] = results_user
        
            
        if max(df_loud[user].median() for user in users) > 0 and min(df_loud[user].median() for user in users) > 0:
            results['volume_control'] = safe_round(100 * min(df_loud[user].median() for user in users) / max(df_loud[user].median() for user in users))
        else:
            results['volume_control'] = 100
        
        if max(results[user]['symbols_per_minute'] for user in users)>0 and min(results[user]['symbols_per_minute'] for user in users)>0:
            results['speed_control'] = safe_round(100 * min(results[user]['symbols_per_minute'] for user in users) / max(results[user]['symbols_per_minute'] for user in users))
        else:
            results['speed_control'] = 100
        
        return results
    
    
class WordAnalyse:
    def __init__(self):
        with open(r'/home/ubuntu/DarwinAI/DAIML_WA_NEW_SEARCH/args.yaml') as file:
            args = load_hyperpyyaml(file)
        self.wa = WordAnalysisModels(args)
      
    
    def calculate_purity_table(self, duration, df_results):
        channels = df_results.channel.unique()
        purity_values = np.empty((len(channels), duration))
        purity_values[:] = np.nan
        columns_puriry = ['time'] + channels.tolist()
        df_purity = pd.DataFrame(data = np.zeros((duration, len(columns_puriry))), columns=columns_puriry)
        
        for channel_num, channel_name in enumerate(channels):
            df_channel = df_results[df_results.channel == channel_name]
            starts_speech = df_channel.start.to_numpy()
            ends_speech = df_channel.end.to_numpy()
            puritys =  df_channel.purity.to_numpy()
            for start, end, purity in zip(starts_speech, ends_speech, puritys): 
                purity_values[safe_to_int(channel_num)][safe_to_int(start) : safe_to_int(end) + 1] = purity
                
            df_purity[channel_name] = purity_values[channel_num]
                        
        df_purity.time = np.arange(0, duration, 1.0)
        df_purity = df_purity.fillna(method='ffill')
     
        return df_purity
    
    def double_list_to_dict(self, double_list):
        result_dict = {}
        for l in double_list:
            for s in l:
                result_dict[s] = l[0]
        return result_dict 
            
    def extract(self, df_speech, df_loud=None, return_per_sec=False,
                neg_words_list=[], pos_words_list=[], par_words_list=[], crit_words_list=[],
                client_pos_words_list=[], client_neg_words_list=[], script_words_double_list=[[]]):
        
        if df_speech.shape[0] == 0:
            return None, None
     
        script_words_list = functools.reduce(operator.iconcat, script_words_double_list, [])
        script_corresponging_dict = self.double_list_to_dict(script_words_double_list)
        if len(script_words_list) > 0:
            script_main = [s[0] for s in script_words_double_list]
        else:
            script_main = []
        
        key_words_all = {'neg': {'list': neg_words_list}, 'pos': {'list': pos_words_list},
                         'par': {'list': par_words_list}, 'crit': {'list': crit_words_list},
                         'client_pos': {'list': client_pos_words_list},
                         'client_neg': {'list': client_neg_words_list},
                         'script': {'list': script_words_list}}
        
        
        for key_word in key_words_all.keys():
            _, key_original_array, key_prep_array = self.wa.regex_proccesing(key_words_all[key_word]['list'])
            #key_prep_array = np.array(list(map(not_replace_forward, list(key_prep_array))))
            key_words_all[key_word]['orig'] = key_original_array
            key_words_all[key_word]['prep'] = key_prep_array
        
        
        df = pd.DataFrame()
        df['channel'] = df_speech['channel']
        df['format_start'] = df_speech['format_start']
        df['format_end'] = df_speech['format_end']
        df['start'] = df_speech['start']
        df['end'] = df_speech['end']
        df['text'] = df_speech['denormalized_text'].apply(self.wa.prepare_text_with_numbers)
        df['words'] = df_speech['words']
        df['emotion_result'] = df_speech['emotion_result']
        
        
        list_of_dfs_after_preparing = []
        df['old_indices'] = df.index

        for channel in df.channel.unique():
            df_one_channel = df[df.channel==channel].reset_index(drop=True)
            #получаем полный текст разговора для одного участника разговора (массив)
            all_phrases = df_one_channel.text.tolist()
            #получаем позиицию каждого слова относительно фразы
            positions_phrases_array = np.concatenate([np.array([i]*len(x.split(' '))) for i,
                                                      x in enumerate(all_phrases)])
            #получаем полный текст разговора для одного участника разговора
            all_text = ' '.join(all_phrases)
            
            #нормализуем все слова разговора для поиска
            all_text_prepared = self.wa.prepare_for_search(all_text)
            
            words_array_original = np.array(all_text.split(' '))
            words_array_prepared = np.array(all_text_prepared.split(' '))
            
            assert len(words_array_prepared) == len(words_array_original)
            
            for key in key_words_all.keys():
                df_one_channel = search_key_words(df_one_channel, key_words_all[key]['prep'], key_words_all[key]['orig'],
                                                  words_array_prepared, words_array_original,
                                                  positions_phrases_array, all_text_prepared,
                                                  name_key_word=key, script=True if key=='script' else False,
                                                 corresponging_dict=script_corresponging_dict if key=='script' else None, 
                                                 len_of_neigh=7 if key=='script' else 3)
                
            list_of_dfs_after_preparing.append(df_one_channel)
            
        df = pd.concat(list_of_dfs_after_preparing).sort_values(by='old_indices').reset_index(drop=True)
        df = df.drop(['old_indices'], axis=1)
        
        
        if return_per_sec and df_loud is not None:
            df['words_all'] = 0
            df['number_of_par_all'] = 0
            for channel in df.channel.unique():
                df_channel = df[df.channel == channel]
                for j_row, i_row in enumerate(df_channel.index):
                    df.at[i_row, 'words_all'] = df_channel.iloc[ : j_row].words.sum()
                    df.at[i_row, 'number_of_par_all'] = df_channel.iloc[:j_row].num_par.sum()
                
            df['purity'] = 1 - df['number_of_par_all'] / df['words_all']
            df_purity = self.calculate_purity_table(df_loud.shape[0], df)
        
        info = self.get_info(df, key_words_all, script_main)
        
        #return df, return_per_sec
        if return_per_sec:
            return df, df_purity, info
        else:
            return df, None, info
    
    
    def word_counter(self, df_words):
        words = []
        words_counter = []
        df_words['counter'] = ''
        for i in range(df_words.shape[0]):
            words += df_words.iloc[i, 1].split(', ')
            counter = dict(Counter(words))
            words_counter.append(', '.join(list(map(lambda x: x[0] + '|' + str(x[1]), counter.items()))))
        
        df_words['words_counter'] = words_counter
        return df_words
    
    
    def calculate_table_timing(self, df, channel, column):
        words_timing = df[df['channel'] == channel].loc[:, ['format_start', column]]
        words_timing = words_timing[words_timing[column] != ''].reset_index()
        words_timing = words_timing.rename({'index': 'number_of_row'}, axis=1)
        words_timing2 = pd.DataFrame(data=None, columns=['format_start', column, 'counter', 'number_of_row'])
        for i in range(words_timing.shape[0]):
            words = words_timing.loc[i, column].split('&')
            for word in words:
                if words_timing2[words_timing2[column] == word].shape[0] > 0:
                    count = safe_to_int(words_timing2[words_timing2[column] == word].counter.iloc[-1]) + 1
                else:
                    count = 1
                words_timing2 = words_timing2.append({'format_start': words_timing.loc[i, 'format_start'],
                                                      column: word, 'counter': count,
                                                      'number_of_row': words_timing.loc[i, 'number_of_row']},
                                                     ignore_index=True)
                                             
        l_words = '&'.join(list(words_timing[column])).split('&')
        words_count = dict(Counter(l_words))
        if list(words_count.keys()) == [''] or len(list(words_count.keys())) == 0 or l_words == ['']:
            words_count = {}
        
        return words_timing2, words_count
    

    def get_info(self, df, key_words_all, script_words_list):
        users = df.channel.unique()
        results = {}
        
        for i, user in enumerate(users):
            results_user = {}
            df_user = df[df.channel == user].reset_index(drop=True)
            results_user['emotional_negative'] =  df_user[df_user['emotion_result'] == 'negative'].shape[0]
            results_user['emotional_negative'] = results_user['emotional_negative'] / df_user.shape[0] if df_user.shape[0] > 0 else 0
            results_user['emotional_negative'] = 100 * (results_user['emotional_negative'])
            results_user['emotional_positive'] =  df_user[df_user['emotion_result'] == 'positive'].shape[0]
            results_user['emotional_positive'] = results_user['emotional_positive'] / df_user.shape[0] if df_user.shape[0] > 0 else 0
            results_user['emotional_positive'] = 100 * (results_user['emotional_positive'])
            results_user['words_all'] = safe_to_int(df_user.words.sum()) 
            
            
          
            
            results_user['speech_purity'] = 100
            for key in key_words_all.keys():
                if len(key_words_all[key]['list']) != 0:
                    results_user['num_' + key] = safe_to_int(df_user['num_' + key].sum())
                    results_user['table_' + key], results_user['count_' + key] = self.calculate_table_timing(df, user, key)
                    
                    if key == 'par' and results_user['words_all'] > 0:
                        results_user['speech_purity'] = safe_int(100 * (1 - results_user['num_par'] / results_user['words_all']))
                    
                else:
                    results_user['num_' + key] = 0
                    results_user['table_' + key] = pd.DataFrame(data=None, columns=['format_start', key])
                    results_user['count_' + key] = {}
                    

                          
            results_user['num_script'] = len(script_words_list)
            
            
            if len(script_words_list) != 0:
                script_said_table = pd.DataFrame()
                script_said_table['script'] = script_words_list
                script_said_table['said'] = script_said_table['script'].apply(lambda x: 1 if x in results_user['table_script'].script.unique() else 0)
                results_user['script_said_table'] = script_said_table
                results_user['script_said_num'] = results_user['script_said_table'].said.sum()
                
                
                
            else:
                results_user['script_said_num'] = 0
                script_said_table = pd.DataFrame(columns=['script', 'said'])
                results_user['script_said_table'] = script_said_table
                
            results[user] = results_user
            
        
        return results
    
    
def safe_to_int(x):
    if x == x:
        return int(x)
    else:
        return x
    
def safe_round(x):
    if x == x:
        return round(x)
    else:
        return x
    
def safe_int(x):
    if x == x:
        return int(x)
    else:
        return x
    
    
    
"""
метод для вычисления таблиц для анализа скриптов

Input:
  results_info_extractor - таблицы, которые вышли из InfoExtractor
  results_words_anal - таблицы, которые вышли из WordAnalyse
  script_group_name - названия группы скриптов, dict, взаимооднозная
  num_words_analysis_answer - количество слов клиента для анализа после фразы оператора, содержащей скрипт

Return:
   tables_script_analysis - dict из двух таблиц (pandas.DataFrame).
       Под ключом 'operator' для исходящих звонков относительно менджера, под ключом 'client' для входящих.

   Таблицы содержат следующее:
      -script_parent - название группы скриптов, string
      -script_child - название сказанного скрипта, string
      -said - 0 или 1, сказан ли скрипт
      
      Анализ одной фразы оператора, которая содержит скрипт:
      -loud_of_phrase - громкость фразы, содержащей скрипт, float
      -clear_of_phrase - чистота фразы, содержащей скрипт, float
      -spr_of_phrase - скорость фразы (колво символов в минуту), содержащей скрипт, float
      -wpr_of_phrase - скорость фразы (колво слов в минуту), содержащей скрипт, float
      -emo_of_phrase_text - эмоция фразы по тексту, содержащей скрипт, string (neutral, negative, positive)
      -emo_of_phrase_voice - эмоция фразы по голосу, содержащей скрипт, string (neutral, negative, positive)
      -emo_of_phrase_results - итоговая эмоция фразы, содержащей скрипт, string (neutral, negative, positive)
      
      Анализ нескольких фраз клиента (итоговое колво слов больше num_words_analysis_answer) после фразы оператора:
      -spr_of_answer - скорость речи клиента (реакция после скрипта, символы в минуту), float
      -wpr_of_answer - скорость речи клиента (реакция после скрипта, слова в минуту), float
      -emo_of_phrase_text_answer - эмоция реакции клиента по тексту, string (neutral, negative, positive)
      -emo_of_phrase_voice_answer - эмоция реакции клиента по голосу, string (neutral, negative, positive)
      -emo_of_phrase_results_answer - итоговая эмоция реакции клиента, string (neutral, negative, positive)
      -loud_of_phrase_answer_mean - усредненная громкость фраз с реакцией float
      -clear_of_phrase_answer_mean -  усредненная чистота фраз с реакцией float
"""


def get_script_analysis(results_info_extractor, results_words_anal, script_group_name=None,
                        num_words_analysis_answer=10):
    
    tables_script_analysis = {}
    
    
    
    info_results_words_anal = results_words_anal['info']
    keys = list(info_results_words_anal.keys())
    
    for key in keys:
         tables_script_analysis[key] = pd.DataFrame(columns=['script_parent', 'script_child', 'said', 'text', 'time',
                                                      'loud_of_phrase', 'clear_of_phrase', 'spr_of_phrase',
                                                      'wpr_of_phrase', 'emo_of_phrase_text', 'emo_of_phrase_voice',
                                                      'emo_of_phrase_results', 'loud_of_phrase_answer_mean',
                                                      'clear_of_phrase_answer_mean', 'spr_of_answer',
                                                      'wpr_of_answer', 'emo_of_phrase_text_answer',
                                                      'emo_of_phrase_voice_answer', 'emo_of_phrase_results_answer'])
        
    
    if len(keys) != 2:
        return tables_script_analysis
    
    table_stt = results_info_extractor[0]
    table_loud = results_info_extractor[1]
    table_clear = results_info_extractor[3]
    table_res_words_anal = results_words_anal[0]
    
    for i_key, key in enumerate(keys):
        key_other = keys[i_key - 1]
        
        all_scripts_main = info_results_words_anal[key]['script_said_table']
        script_table = info_results_words_anal[key]['table_script']
   
        table_script_analysis = pd.DataFrame(columns=['script_parent', 'script_child', 'said', 'text', 'time',
                                                      'loud_of_phrase', 'clear_of_phrase', 'spr_of_phrase',
                                                      'wpr_of_phrase', 'emo_of_phrase_text', 'emo_of_phrase_voice',
                                                      'emo_of_phrase_results', 'loud_of_phrase_answer_mean',
                                                      'clear_of_phrase_answer_mean', 'spr_of_answer',
                                                      'wpr_of_answer', 'emo_of_phrase_text_answer',
                                                      'emo_of_phrase_voice_answer', 'emo_of_phrase_results_answer'])
    
        if all_scripts_main is None or all_scripts_main.shape[0] == 0:
            continue
        
        for i in range(all_scripts_main.shape[0]):
            script_info = all_scripts_main.iloc[i]
            script_name = script_info.script
            if script_info.said == 0:
                table_script_analysis = table_script_analysis.append({'script_parent': script_name,
                                                                      'said': 0}, ignore_index=True)
                
                
                continue
            
                
            idx_with_script = script_table[script_table.script == script_name].number_of_row.tolist()
            
            
            for number_row in idx_with_script:
                idx_script = np.where(np.array(table_res_words_anal.iloc[number_row].script.split('&')) == script_name)[0][0]
                script_child = table_res_words_anal.iloc[number_row].child_script.split('&')[idx_script]
                info_from_stt_table = table_stt.iloc[number_row]
                text = info_from_stt_table.denormalized_text
                start_phrase = info_from_stt_table.start
                start_time = info_from_stt_table.format_start
                ent_phrase = info_from_stt_table.end
                loud_of_phrase = table_loud[key].iloc[int(start_phrase): int(ent_phrase) + 1].mean()
                clear_of_phrase = table_clear[key].iloc[int(start_phrase): int(ent_phrase) + 1].mean()
                spr_of_phrase = info_from_stt_table.spr
                wpr_of_phrase = info_from_stt_table.wpr
                emo_of_phrase_text = info_from_stt_table.emotion_text
                emo_of_phrase_voice = info_from_stt_table.emotion_voice
                emo_of_phrase_results = info_from_stt_table.emotion_result
                
                table_stt_answer = table_stt[table_stt.channel==key_other].loc[number_row:].reset_index(drop=True)
                
                cumsum_table = table_stt_answer[table_stt_answer['words'].cumsum() > num_words_analysis_answer]
                
                if cumsum_table.shape[0] > 0:
                    index_end_analysis = cumsum_table.index[0]
                    table_stt_answer_crop = table_stt_answer.iloc[ :index_end_analysis+1]
                else:
                    table_stt_answer_crop = table_stt_answer
                
                if table_stt_answer_crop.shape[0] == 0:
                    spr_of_answer = 0
                    wpr_of_answer = 0 
                    emo_of_phrase_text_answer = 'neutral'
                    emo_of_phrase_voice_answer = 'neutral'
                    emo_of_phrase_results_answer = 'neutral'
                    loud_of_phrase_answer_mean = 0
                    clear_of_phrase_answer_mean = 0
                else:
                    
                    spr_of_answer = table_stt_answer_crop.spr.dropna().mean()
                    wpr_of_answer = table_stt_answer_crop.wpr.dropna().mean()
                    emo_of_phrase_text_answer = table_stt_answer_crop.emotion_text.value_counts().idxmax()
                    emo_of_phrase_voice_answer = table_stt_answer_crop.emotion_voice.value_counts().idxmax()
                    emo_of_phrase_results_answer = table_stt_answer_crop.emotion_result.value_counts().idxmax()
                    loud_of_phrase_answer = np.zeros(table_stt_answer_crop.shape[0])
                    clear_of_phrase_answer = np.zeros(table_stt_answer_crop.shape[0])
                    for k, (start, end) in enumerate(zip(table_stt_answer_crop.start, table_stt_answer_crop.end)):
                        loud_of_phrase_answer[k] = table_loud[key_other].iloc[int(start): int(end) + 1].mean()
                        clear_of_phrase_answer[k] = table_clear[key_other].iloc[int(start): int(end) + 1].mean()
                        
                    loud_of_phrase_answer_mean = loud_of_phrase_answer.mean()
                    clear_of_phrase_answer_mean = clear_of_phrase_answer[clear_of_phrase_answer!=0].mean()
                
                table_script_analysis = table_script_analysis.append({'script_parent': script_name,
                                                                      'script_child': script_child,
                                                                      'said': 1,
                                                                      'text': text,
                                                                      'time': start_time,
                                                                      'loud_of_phrase':loud_of_phrase,
                                                                      'clear_of_phrase': clear_of_phrase,
                                                                      'spr_of_phrase': spr_of_phrase,
                                                                      'wpr_of_phrase': wpr_of_phrase,
                                                                      'emo_of_phrase_text': emo_of_phrase_text,
                                                                      'emo_of_phrase_voice': emo_of_phrase_voice,
                                                                      'emo_of_phrase_results': emo_of_phrase_results,
                                                                      'spr_of_answer': spr_of_answer,
                                                                      'wpr_of_answer': wpr_of_answer,
                                                                  'emo_of_phrase_text_answer': emo_of_phrase_text_answer,
                                                                  'emo_of_phrase_voice_answer': emo_of_phrase_voice_answer,
                                                                  'emo_of_phrase_results_answer': emo_of_phrase_results_answer,
                                                                  'loud_of_phrase_answer_mean': loud_of_phrase_answer_mean,
                                                                  'clear_of_phrase_answer_mean': clear_of_phrase_answer_mean},
                                                                 ignore_index=True)
      
        #table_script_analysis['script_parent'] = table_script_analysis['script_parent'].apply(lambda x: script_group_name[x])
        table_script_analysis = table_script_analysis.round(1)
        tables_script_analysis[key] = table_script_analysis
        
    return tables_script_analysis