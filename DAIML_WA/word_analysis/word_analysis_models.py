import numpy as np
import re
import yaml
import pandas as pd
from DAIML_WA.word_analysis.extractor import NumberExtractor
import pymorphy2


class WordAnalysisModels:
    def __init__(self, args):
        self.load_and_prepare_replace_dict('/home/ubuntu/DarwinAI/DAIML_WA/word_analysis/SLOVAR.csv')
        self.number_extractor = NumberExtractor()
        self.morph = pymorphy2.MorphAnalyzer()
        self.score_treschold = args['score_treschold']
        self.blacklist_cap = args['blacklist_cap']
    
    def load_and_prepare_replace_dict(self, path):
        self.words_all_replace = []
        self.target_all_replace = []
        table = pd.read_csv(path)
        for i in range(table.shape[0]):
            words = table.iloc[i].dropna().to_list()
            words[1: ] = list(map(lambda x: r'\b' + x + r'\b', words[1: ]))
            target = words[0]
            original = ('|'.join(words[1:]))
            original_regex = r"{}".format(original)
            self.words_all_replace.append(original_regex)
            self.target_all_replace.append(target)
        
         
    def replace_subwords(self, normalized_text):
        for word, target in zip(self.words_all_replace, self.target_all_replace):
            normalized_text = re.sub(word, target, normalized_text)
        return normalized_text
    
    def capitalization_restoring_punc(self, text):
        old_text = np.array(list(text))
        if len(old_text) > 0:
            old_text[0] = old_text[0].upper()
            indexes_dot = np.argwhere(old_text == '.')[:, 0]
            indexes_q = np.argwhere(old_text == '?')[:, 0]
            
            for index in indexes_dot:
                if index + 2 < len(old_text):
                    old_text[index + 2] = old_text[index + 2].upper()
                    
            for index in indexes_q:
                if index + 2 < len(old_text):
                    old_text[index + 2] = old_text[index + 2].upper()        
             
            if old_text[-1] != '.' and old_text[-1] != '?' and old_text[-1] != ',':
                new_text = ''.join(old_text.tolist()) + '.'
                
            elif old_text[-1] == ',':
                 new_text = ''.join(old_text.tolist()[:-1]) + '.'
            else:
                new_text = ''.join(old_text.tolist())
                
            return new_text
        else:
            return ''

        
    def denormalize(self, normalized_text, with_punc=False):
        denorm_text = self.number_extractor.replace_groups_new(normalized_text)
        denorm_text = self.replace_subwords(denorm_text)
        denorm_text = self.restore_capitalization(denorm_text)
        denorm_text = self.plus_replace(denorm_text)
        
        if with_punc:
            denorm_text = re.sub(' \.', '.', denorm_text)
            denorm_text = re.sub(' \,', ',', denorm_text)
            denorm_text = re.sub(' \?', '?', denorm_text)
            if len(denorm_text) > 1:
                denorm_text = self.capitalization_restoring_punc(denorm_text)
  
        else:
            if len(denorm_text) > 1:
                denorm_text = denorm_text[0].upper() + denorm_text[1:] + '.'
            else:
                denorm_text = denorm_text.upper() + '.'
                
        return denorm_text
    
    def denormalize_keywords(self, normalized_text):
        denorm_text = self.number_extractor.replace_groups_new(normalized_text)
        denorm_text = self.replace_subwords(denorm_text)
        denorm_text = self.plus_replace(denorm_text)
        return denorm_text
    
    
    def restore_capitalization(self, text):
        words = text.split(' ')
        for i, word in enumerate(words):
            res_anal = self.morph.parse(word)[0]
            tag = res_anal.tag
            score = res_anal.score
            if ('Geox' in tag or 'Name' in tag or 'Surn' in tag or 'Patr' in tag) and (score > self.score_treschold) and word not in self.blacklist_cap:
                words[i] = words[i].capitalize()
                
        return ' '.join(words)
    
    
    def regex_proccesing(self, words_list):
        words_orignal_array = np.array(words_list)
        words_list = list(map(lambda x: self.denormalize_keywords(x), words_list))
        words_list_regex_list = list(map(lambda x: r'\b' + self.prepare_for_search(self.prepare_text_with_numbers(x)) + r'\b', words_list))
        words_list_regex = '|'.join(words_list_regex_list)
        words_list_regex = r"{}".format(words_list_regex)
        words_regex_array = np.array(list(map(lambda x: x.strip()[2:-2], words_list_regex_list)))
        return words_list_regex, words_orignal_array, words_regex_array
        
        
    
    def prepare_for_search(self, text):
        words_new = []
        words = text.split(' ')
        for word in words:
            parsed = self.morph.parse(word)[0]
            if 'Infr' not in parsed.tag and 'Erro' not in parsed.tag and len(word) > 1:
                words_new.append(parsed.normal_form)
               
            else:
                words_new.append(word)
   
        return ' '.join(words_new)
    
    
    def splitText(self, text, parts=1):
        words = text.split()
        grouped_words = [' '.join(words[i: i + parts]) for i in range(0, len(words))]
        return grouped_words
    
    
    def search_words_in_original_text(self, original_text, prepared_text, word_for_search):
        searched_words = []
        grouped_original = self.splitText(original_text, len(word_for_search.split(' ')))
        grouped_prepared = self.splitText(prepared_text, len(word_for_search.split(' ')))
        for i, segment in enumerate(grouped_prepared):
            if word_for_search == segment:
                if i < len(grouped_original):
                    searched_words.append(grouped_original[i])
         
        return list(set(searched_words))
    
    def search_words(self, s, words, original_array, regex_list_array):
        text = s['text']
        prepared_for_search = self.prepare_for_search(text)
        words_found = re.findall(words, prepared_for_search)
        num_of_words = len(words_found)
        list_all_words = []
        searched_words = []
        for word_found in words_found:
            searched_words += self.search_words_in_original_text(text, prepared_for_search, word_found)
            arr_mask = np.where(regex_list_array == word_found, True, False)
            list_all_words += original_array[arr_mask].tolist()
            
        all_words = '&'.join(list_all_words)
        all_words_text_origin = '&'.join(list(set(searched_words)))
        return num_of_words, all_words, all_words_text_origin
    
    
    def scripts_per_word_regex(self, sentence):
        sentence_regex = ''
        words = sentence.split(' ')
        if len(words) == 1:
            return r'(\b{}\b)'.format(sentence)
        else:
            for i, word in enumerate(words):
                if i == len(words) - 1:
                    sentence_regex += r'(\b{}\b)'.format(word)
                else:
                    sentence_regex += r'(\b{}\b)(?:(?:\s.+\s)+|\s)'.format(word)
        return sentence_regex
    
    
    def regex_proccesing_for_scripts(self, words_list):
        if len(words_list) != 0:
            words_orignal_array = np.array(words_list)
            words_list = list(map(lambda x: self.denormalize_keywords(x), words_list))
            words_regex = list(map(lambda x: self.prepare_for_search(self.prepare_text_with_numbers(x)), words_list))
            words_regex_prepared_list = list(map(lambda x: self.scripts_per_word_regex(x), words_regex))
            words_regex_array = np.array(words_regex)
            return words_regex_prepared_list, words_orignal_array, words_regex_array
        else:
            return None, None, None
        
    
    def search_script(self, s, words_regex_prepared_list, original_array, regex_list_array, corr_dict):
        text = s['text']
        prepared_for_search  = self.prepare_for_search(text)
        words_found = []
        for word_regex_prepared in words_regex_prepared_list:
            words_found += re.findall(word_regex_prepared, prepared_for_search)
        num_of_words = len(words_found)
        list_all_words = []
        for word_found in words_found:
            if type(word_found) is tuple:
                word_found = ' '.join(list(word_found))
            arr_mask = np.where(regex_list_array == word_found, True, False)
            list_all_words += list(map(lambda x: corr_dict[x], original_array[arr_mask].tolist()))
        all_words = '&'.join(list_all_words)
        return num_of_words, all_words
    
    def add_spaces_before_punc(self, text):
        if text is None or text != text:
            text = ''
        text = re.sub('\.', ' .', text)
        text = re.sub('\,', ' ,', text)
        text = re.sub('\?', ' ?', text)
        return text
    
    def prepare_text(self, text):
        if text is None or text != text:
            text = ''
        text = str(text)
        text = text.strip()
        text = text.lower()
        text = re.sub('[ё]', 'е', text)
        text = re.sub('-', ' ', text)
        text = re.sub('[^абвгдежзийклмнопрстуфхцчшщъыьэюя\s]', '', text)
        text = re.sub('[\r\n]', '', text)
        text = re.sub(' +', ' ', text)
        text = text.strip()
        return text
    
    
    def prepare_text_with_punc(self, text):
        if text is None or text != text:
            text = ''
        text = str(text)
        text = text.strip()
        text = text.lower()
        text = re.sub('[ё]', 'е', text)
        text = re.sub('-', ' ', text)
        text = re.sub('[^абвгдежзийклмнопрстуфхцчшщъыьэюя\?\.\,\s]', '', text)
        text = re.sub('[\r\n]', '', text)
        text = re.sub(' +', ' ', text)
        text = text.strip()
        return text
    
    
    def prepare_text_with_numbers(self, text):
        if text is None or text != text:
            text = ''
        text = str(text)
        text = text.strip()
        if len(text) > 0 and text[-1] == '.':
            text = text[:-1]
        text = text.lower()
        text = re.sub('[ё]', 'е', text)
        text = re.sub('-', ' ', text)
        text = re.sub('[^абвгдежзийклмнопрстуфхцчшщъыьэюя0123456789abcdefghijklmnopqrstuvwxyz\s]', '', text)
        text = re.sub('[\r\n]', '', text)
        text = re.sub(' +', ' ', text)
        text = text.strip()
        return text
    
    def remove_punc(self, text):
        if text is None or text != text:
            text = ''
        else:
            text = text.lower()
            text = re.sub('\.', '', text)
            text = re.sub('\,', '', text)
            text = re.sub('\?', '', text)
            
        return text    
    
    def plus_replace(self, text):
        text = re.sub('плюс ', '+', text)
        return text
    
    def symbols_per_min(self, text, duration):
        number_of_symbols = len(text)
        if number_of_symbols > 1: 
            return number_of_symbols / duration * 60, number_of_symbols
        else: 
            return np.nan, number_of_symbols
    
    def words_per_min(self, text, duration):
        number_of_words = len(text.split(' '))
        if number_of_words > 1:
            return number_of_words / duration * 60, number_of_words
        else: 
            return np.nan, number_of_words
    
    def counter_extracter(self, words_count):
        all_words  = []
        for key in words_count.keys():
            all_words.append(key + '({})'.format(str(words_count[key])))
        return all_words   