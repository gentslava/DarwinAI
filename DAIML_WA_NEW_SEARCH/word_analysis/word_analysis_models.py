import numpy as np
import re
import yaml
import pandas as pd
from DAIML_WA_NEW_SEARCH.word_analysis.extractor import NumberExtractor
import pymorphy2


class WordAnalysisModels:
    def __init__(self, args):
        self.load_and_prepare_replace_dict('/home/ubuntu/DarwinAI/DAIML_WA_NEW_SEARCH/word_analysis/SLOVAR.csv')
        self.number_extractor = NumberExtractor()
        self.morph = pymorphy2.MorphAnalyzer()
        self.score_treschold = args['score_treschold']
        self.blacklist_cap = args['blacklist_cap']
        self.replace_norm_form = args['replace_norm_form']
    
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
                word_new = parsed.normal_form
                if word_new in self.replace_norm_form.keys():
                    word_new = self.replace_norm_form[word_new]
                words_new.append(word_new)
            else:
                words_new.append(word)
                
              
   
        return ' '.join(words_new)
 
    
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
        #text = re.sub('плюс ', '+', text)
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
    

#метод для добавления ключевой фразы в ячейку

def add_key_word(s, key_words):
    results = ''
    for i, wort_example in enumerate(key_words):
        if i == 0:
            results = wort_example
        else:
            results = results + '&' + wort_example
 
    if s == '':
        return results
    else:
        return s + '&' + results

#метод для добавления первоначального слова в ячейку
def add_orig_word(s, word):
    if s == '':
        return word
    else:
        return s + '&' + word   

    
def not_replace_forward(text):
    return re.sub(r"\bне\s", "не'", text)
    
def not_replace_backward(text):
    return re.sub(r"\bне'", "не ", text)
    
"""метод для поиска ключевых фраз в таблице (только для одного канала!). 
имеется поиск составной фразы по частям сразу в нескольких частях диалога

Input: 
df - таблица без ключевых слов
key_prepared_array - массив из ключевых фраз нормализованных
key_original_array - массив из ключевых фраз первоначальных
words_array_prepared - массив из всех слов диалога из таблицы нормализованных
words_array_original - массив из всех слов диалога из таблицы первоначальных
positions_phrases_array - позиции слов в диалогах, длина как у words_array_prepared
all_text_prepared - полный текст диалога из таблицы нормализованный
name_key_word - название ключевого слова
len_of_neigh - область по которой нужно искать ключевые фразы с несколькими словами (колво слов справа и слева)
script - bool, True если задан скрипт в виде двойного листа
corresponging_dict - если script == True, то необходимо также задать словарь соответствия фраз

Return:
df - обработанная таблица с тремя новыми столбцами

"""

def search_key_words(df, key_prepared_array, key_original_array, words_array_prepared,
                     words_array_original, positions_phrases_array, all_text_prepared,
                     name_key_word='script', len_of_neigh=5, script=False, corresponging_dict=None,
                     search_type='dynamic'):
    
    #нужно понять, какие ключевые фразы вообще есть в тексте, чтобы не искать лишние
    #чтобы не было повторений, используем set
    #ищем с помощью re.search (поиск до первого совпадаения, выдает None если не найдено)
    #фразы из нескольких слов ищутся по словам
    words_searched = set()
    
    if key_prepared_array.shape[0] == 0 or key_original_array.shape[0] == 0:
        df['num_' + name_key_word] = np.nan
        df[name_key_word] = np.nan
        df['orig_' + name_key_word] = np.nan
        return df
    
    for key_word in key_prepared_array:
        parts_key_word = key_word.split(' ')
        for i, part_key_word in enumerate(parts_key_word):
            res = re.search(r'\b{}\b'.format(part_key_word), all_text_prepared)
            if res is None:
                break
            else:
                if i == len(parts_key_word) - 1:
                    words_searched.add(key_word)
        
    words_searched = list(words_searched)
    
    #три столбца:
    #первый - общее количество сказанных ключевых фраз в одной фразе
    #второй - перечисление ключевых фраз через &, сказанных во фразе.
    #если ключевая фраза произносится в течение нескольких фраз, то ключевая фраза пишется в самой ранней фразе
    #третий - первончальные слова, которые соответствуют ключевой фразе для выделения
    df['num_' + name_key_word] = 0
    df[name_key_word] = ''
    df['orig_' + name_key_word] = ''
    if script == True and corresponging_dict is not None:
        df['child_' + name_key_word] = ''
    
    #цикл по найденным фразам
    for word in words_searched:
        #ищем не цельную составную фразу, а по словам
        parts_word = word.split(' ')
        #тк нашли по нормализованной ключевой фразе, а нам нужна первоначальная, ищем соответствие
        orig_key_word = key_original_array[np.where(key_prepared_array == word)[0]]
        if len(parts_word) == 1:
            ids = np.where(words_array_prepared == word)[0]
            words_original = words_array_original[ids]
            #ищем позиции в диалоге
            poses = positions_phrases_array[ids]
            
            #заполняем столбцы таблицы
            for i, pos in enumerate(poses):
                df.at[pos, 'num_' + name_key_word] = df.at[pos, 'num_' + name_key_word] + 1
                df.at[pos, 'orig_' + name_key_word] = add_orig_word(df.iloc[pos]['orig_' + name_key_word], words_original[i])
                if script == True and corresponging_dict is not None:
                    df.at[pos, 'child_' + name_key_word] = add_key_word(df.iloc[pos]['child_' + name_key_word], orig_key_word)
                    orig_key_parent = np.array([corresponging_dict[w] for w in orig_key_word])
                    df.at[pos, name_key_word] = add_key_word(df.iloc[pos][name_key_word], orig_key_parent)
    
                else:
                    df.at[pos, name_key_word] = add_key_word(df.iloc[pos][name_key_word], orig_key_word)
            
        else:
            #если ключевая фраза состоит из нескольких слов, то ищем каждое следующее слово в окретности пред. слова
            #остальное примерно одинаково
            
            #ставим возможное количество слов между ключевыми словами динамическое, то есть при 2 слов между ними может быть 3
            #для трех - 4, для четырех - 5
            if search_type == 'dynamic':
                if name_key_word == 'script':
                    len_of_neigh = len(parts_word) + 3
                else:
                    len_of_neigh = len(parts_word) + 2
            else:
                len_of_neigh = len_of_neigh
            
            
            ids_first = np.where(words_array_prepared == parts_word[0])[0]
            seqs_all = []
            blocked_indexes = []
            for id_first in ids_first:
                seqs = []
                seqs.append(id_first)
                id_best = id_first
                for i in range(1, len(parts_word)):
                    start_s = max(0, id_best - len_of_neigh)
                    end_s = min(len(words_array_prepared), id_best + len_of_neigh)
                    
                    if words_array_prepared[id_best] == 'не':
                        if words_array_prepared[id_best + 1] != parts_word[i]:
                            break
                        else:
                            id_best = id_best + 1
                            seqs.append(id_best)
                    else:
                        
                        id_temporal = np.where(words_array_prepared[start_s : end_s] == parts_word[i])[0]
                        id_temporal = id_temporal + start_s
                        mask = np.isin(id_temporal, blocked_indexes)
                        id_temporal = id_temporal[mask==False]
                        
                        if id_temporal.shape[0] == 0:
                            break
                        else:
                            if id_temporal[id_temporal > id_best].shape[0] > 0:
                                id_best_new = np.min(id_temporal[id_temporal > id_best])
                            else:
                                id_best_new =  np.min(id_temporal)
                            if id_best_new != id_best:
                                id_best = id_best_new
                                seqs.append(id_best)
                 
                        
                if len(seqs) == len(parts_word):
                    blocked_indexes += seqs
                    seqs_all.append(seqs)
                      
            for seq in seqs_all:
                words_original = words_array_original[seq]
                poses_one_phrase = positions_phrases_array[seq]
                poses_one_phrase_first = poses_one_phrase.min()
                df.at[poses_one_phrase_first, 'num_' + name_key_word] = df.at[poses_one_phrase_first,'num_'+name_key_word] + 1
                
                if script == True and corresponging_dict is not None:
                    df.at[poses_one_phrase_first,'child_'+name_key_word] = add_key_word(df.iloc[poses_one_phrase_first]['child_' + name_key_word], orig_key_word)
                    orig_key_parent = np.array([corresponging_dict[w] for w in orig_key_word])
                    df.at[poses_one_phrase_first, name_key_word] = add_key_word(df.iloc[poses_one_phrase_first][name_key_word],
                                                                                orig_key_parent)
    
                else:
                    df.at[poses_one_phrase_first, name_key_word] = add_key_word(df.iloc[poses_one_phrase_first][name_key_word],
                                                                                orig_key_word)
                
                pos_sorted = poses_one_phrase[np.array(seq).argsort()]
                word_sorted = words_original[np.array(seq).argsort()]
                
                #проверка, находятся ли все слова в одной фразе в диалоге
                if pos_sorted.std() == 0:
                    df.at[pos_sorted[0], 'orig_'+name_key_word] = add_orig_word(df.iloc[pos_sorted[0]]['orig_'+ name_key_word],
                                                                          ' '.join(word_sorted))
                else:
                    unique_pos, counts_pos = np.unique(pos_sorted, return_counts=True)
                    j_word = 0
                    for uniq, count in zip(unique_pos, counts_pos):
                        df.at[uniq, 'orig_' + name_key_word] = add_orig_word(df.iloc[uniq]['orig_' + name_key_word],
                                                              ' '.join(word_sorted[j_word: j_word+count]))
                        j_word += count
    
    
    return df