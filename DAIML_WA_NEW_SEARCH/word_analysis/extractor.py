from natasha.extractors import Extractor
from yargy.parser import Match
from yargy import rule, or_
from yargy.pipelines import morph_pipeline, caseless_pipeline
from yargy.interpretation import fact, const
from yargy.predicates import eq, caseless, normalized, type
import re

class NumberExtractor(Extractor):
    def __init__(self):
        super(NumberExtractor, self).__init__(NUMBER)
       

    def replace(self, text):
        """
        Замена чисел в тексте без их группировки

        Аргументы:
            text: исходный текст

        Результат:
            new_text: текст с замененными числами
        """
        if text:
            new_text = ""
            start = 0

            for match in self.parser.findall(text):
                if match.fact.multiplier:
                    num = match.fact.int * match.fact.multiplier
                else:
                    num = match.fact.int
                new_text += text[start: match.span.start] + str(num)
                start = match.span.stop
            new_text += text[start:]

            if start == 0:
                return text
            else:
                return new_text
        else:
            return None
    
    def replace_groups(self, text):
        """
        Замена сгруппированных составных чисел в тексте

        Аргументы:
            text: исходный текст

        Результат:
            new_text: текст с замененными числами
        """
        if text:
            start = 0
            matches = list(self.parser.findall(text))
            groups = []
            group_matches = []

            for i, match in enumerate(matches):
                if i == 0:
                    start = match.span.start
                if i == len(matches) - 1:
                    next_match = match
                else:
                    next_match = matches[i + 1]
                group_matches.append(match.fact)
                if text[match.span.stop: next_match.span.start].strip() or next_match == match:
                    groups.append((group_matches, start, match.span.stop))
                    group_matches = []
                    start = next_match.span.start
            
            new_text = ""
            start = 0
            
            for group in groups:
                pred_num = -1
                num = 0
                nums = [[]]
                new_text += text[start: group[1]]
                for match in group[0]:
                    curr_num = match.int * match.multiplier if match.multiplier else match.int
                    if len(str(curr_num)) >= len(str(pred_num)) and pred_num != -1:
                        if num > 0:
                            nums[-1].append(num)
                        nums.append([])
                        num = 0
                                       
                    if match.multiplier:
                        num = (num + match.int) * match.multiplier
                        nums[-1].append(num)
                        num = 0
                    elif num > curr_num or num == 0:
                        num += curr_num
                    else:
                        nums[-1].append(num)
                        num = 0
                    pred_num = curr_num
                if num > 0:
                    nums[-1].append(num)
               
                new_text += ' '.join([str(sum(nums_one)) for nums_one in nums])
                start = group[2]
            new_text += text[start:]

            if start == 0:
                return text
            else:
                return new_text
        else:
            return None
        
        
        
    def replace_groups_new(self, text):
        """
        Замена сгруппированных составных чисел в тексте

        Аргументы:
            text: исходный текст

        Результат:
            new_text: текст с замененными числами
        """
        if text is not None and len(text) > 0:
            
            for key in replace_dict_start.keys():
                text = re.sub(r"\b{}\b".format(key), '#' + replace_dict_start[key] + '#', text)
                
            start = 0
            matches = list(self.parser.findall(text))
            groups = []
            group_matches = []
            
            
            for i, match in enumerate(matches):
                if 'INT' in list(match)[0][-1]:
                    matches.pop(i)

            for i, match in enumerate(matches):
                if i == 0:
                    start = match.span.start
                if i == len(matches) - 1:
                    next_match = match
                else:
                    next_match = matches[i + 1]

                if match.fact.multiplier == None:
                    if 'ых' in text[match.span.start: match.span.stop].strip()[-2:]:
                        poryadok = 'х'
                    elif 'ый' in text[match.span.start: match.span.stop].strip()[-2:]:
                        poryadok = 'й'
                    elif 'ой' in text[match.span.start: match.span.stop].strip()[-2:]:
                        poryadok = 'й'
                    elif 'го' in text[match.span.start: match.span.stop].strip()[-2:]:
                        poryadok = 'го'
                    elif 'ое' in text[match.span.start: match.span.stop].strip()[-2:]:
                        poryadok = 'е'
                        
                    elif 'ум' in text[match.span.start: match.span.stop].strip()[-2:]:
                        poryadok = 'м'
                        
                    elif 'им' in text[match.span.start: match.span.stop].strip()[-2:]:
                        poryadok = 'м'
                        
                    elif 'ым' in text[match.span.start: match.span.stop].strip()[-2:]:
                        poryadok = 'м'
                        
                    elif 'ую' in text[match.span.start: match.span.stop].strip()[-2:]:
                        poryadok = 'ю'
                        
                    elif 'ью' in text[match.span.start: match.span.stop].strip()[-2:]:
                        poryadok = 'ю'
                        
                    elif 'ию' in text[match.span.start: match.span.stop].strip()[-2:]:
                        poryadok = 'ю'
                    else:
                        poryadok = ''
                else:
                    poryadok = ''
                
                group_matches.append((match.fact, poryadok))
             

                if text[match.span.stop: next_match.span.start].strip() or next_match == match:
                    groups.append((group_matches, start, match.span.stop))
                    group_matches = []
                    start = next_match.span.start
            
            new_text = ""
            start = 0
            
            for group in groups:
                pred_num = -1
                num = 0
                nums = [[]]
                pors = []
                new_text += text[start: group[1]]
                for match, por in group[0]:
                    curr_num = match.int * match.multiplier if match.multiplier else match.int
                    if pred_num != -1 and len(str(match.int)) >= len(str(pred_num)):
                        if num > 0:
                            nums[-1].append(num)
                            pors.append(por)
                        nums.append([])
                        num = 0
                    if match.multiplier:
                        num = (num + match.int) * match.multiplier
                        nums[-1].append(num)
                        pors.append(por)
                        num = 0
                    elif num > curr_num or num == 0:
                        num += curr_num
                    else:
                        nums[-1].append(num)
                        pors.append(por)
                        num = 0
                    pred_num = curr_num
                if num > 0:
                    nums[-1].append(num)
                    pors.append(por)
                new_text =  new_text + ' '.join([str(sum(nums_one)) + por_one for nums_one, por_one in zip(nums, pors)])
                start = group[2]
            new_text += text[start:]

            if start == 0:
                text = re.sub(r"#", '', text)
                text = re.sub(r"%", '0', text)
                return text
            else:
                new_text = re.sub(r"#", '', new_text)
                new_text = re.sub(r"%", '0', new_text)
                for key in replace_dict_finish.keys():
                    new_text = re.sub(r"\b{}\b".format(key), replace_dict_finish[key], new_text)
                return new_text
        else:
            return ''
        
        
        
        
        
      
Number = fact('Number', ['int', 'multiplier'])
#для нулей какая то непонятная проблема, поэтому специальные символы, а далее замена их на ноль
replace_dict_start = {"ноль" : "%", "нуль" : "%",
                      "один ноль" : "%", "один нуль" : "%", "одна единица": "1", "одна двойка": "2", "одна тройка": "3",
                      "одна четверка": "4", "одна пятерка": "5", "одна шестерка": "6", "одна семерка": "7", 
                      "одна восьмерка": "8", "одна девятка": "9",
                      "два ноля" : 2*"%", "два нуля" : 2*"%", "две единицы": 2*"1", "две двойки": 2*"2", "две тройки": 2*"3",
                      "две четверки": 2*"4", "две пятерки": 2*"5", "две шестерки": 2*"6", "две семерки": 2*"7", 
                      "две восьмерки": 2*"8", "две девятки": 2*"9",
                      "три ноля" : 3*"%", "три нуля" : 3*"%", "три единицы": 3*"1", "три двойки": 3*"2", "три тройки": 3*"3",
                      "три четверки": 3*"4", "три пятерки": 3*"5", "три шестерки": 3*"6", "три семерки": 3*"7", 
                      "три восьмерки": 3*"8", "три девятки": 3*"9",
                      "четыре ноля" : 4*"%", "четыре нуля" : 4*"%", "четыре единицы": 4*"1", "четыре двойки": 4*"2",
                      "четыре тройки": 4*"3",
                      "четыре четверки": 4*"4", "четыре пятерки": 4*"5", "четыре шестерки": 4*"6", "четыре семерки": 3*"7", 
                      "четыре восьмерки": 4*"8", "четыре девятки": 4*"9",
                      "пять нолей" : 5*"%", "пять нулей" : 5*"%", "пять единиц": 5*"1", "пять двоек": 5*"2",
                      "пять троек": 5*"3",
                      "пять четверок": 5*"4", "пять пятерок": 5*"5", "пять шестерок": 5*"6", "пять семерок": 5*"7", 
                      "пять восьмерок": 5*"8", "пять девяток": 5*"9",
                      "шесть нолей" : 6*"%", "шесть нулей" : 6*"%", "шесть единиц": 6*"1", "шесть двоек": 6*"2",
                      "шесть троек": 6*"3",
                      "шесть четверок": 6*"4", "шесть пятерок": 6*"5", "шесть шестерок": 6*"6", "шесть семерок": 6*"7", 
                      "шесть восьмерок": 6*"8", "шесть девяток": 6*"9",
                      "семь нолей" : 7*"%", "семь нулей" : 7*"%", "семь единиц": 7*"1", "семь двоек": 7*"2",
                      "семь троек": 7*"3",
                      "семь четверок": 7*"4", "семь пятерок": 7*"5", "семь шестерок": 7*"6", "семь семерок": 7*"7", 
                      "семь восьмерок": 7*"8", "семь девяток": 7*"9",
                      "восемь нолей" : 8*"%", "восемь нулей" : 8*"%", "восемь единиц": 8*"1", "восемь двоек": 8*"2",
                      "восемь троек": 8*"3",
                      "восемь четверок": 8*"4", "восемь пятерок": 8*"5", "восемь шестерок": 8*"6", "восемь семерок": 8*"7", 
                      "восемь восьмерок": 8*"8", "восемь девяток": 8*"9",
                      "девять нолей" : 9*"%", "девять нулей" : 9*"%", "девять единиц": 9*"1", "девять двоек": 9*"2",
                      "девять троек": 9*"3",
                      "девять четверок": 9*"4", "девять пятерок": 9*"5", "девять шестерок": 9*"6", "девять семерок": 9*"7", 
                      "девять восьмерок": 9*"8", "девять девяток": 9*"9",
                      "десять нолей" : 10*"%", "десять нулей" : 10*"%", "десять единиц": 10*"1", "десять двоек": 10*"2",
                      "десять троек": 10*"3",
                      "десять четверок": 10*"4", "десять пятерок": 10*"5", "десять шестерок": 10*"6",
                      "десять семерок": 10*"7", 
                      "десять восьмерок": 10*"8", "десять девяток": 10*"9"}

replace_dict_finish = {'во 1х': 'во первых',
                'во 2х': 'во вторых',
                'в 3х': 'в третьих',
                'в 4х': 'в четвертых'}
NUMS_RAW = {
    'ноль': 0,
    'нуль': 0,
    'один': 1, 
    'два': 2, 
    'три': 3, 
    'четыре': 4, 
    'пять': 5,
    'шесть': 6,
    'семь': 7,
    'восемь': 8,
    'девять': 9,
    'десять': 10,
    'одиннадцать': 11,
    'двенадцать': 12,
    'тринадцать': 13,
    'четырнадцать': 14,
    'пятнадцать': 15,
    'шестнадцать': 16,
    'семнадцать': 17,
    'восемнадцать': 18,
    'девятнадцать': 19,
    'двадцать': 20,
    'тридцать': 30,
    'сорок': 40,
    'пятьдесят': 50,
    'шестьдесят': 60,
    'семьдесят': 70,
    'восемьдесят': 80,
    'девяносто': 90,
    'сто': 100,
    'двести': 200,
    'триста': 300,
    'четыреста': 400,
    'пятьсот': 500,
    'шестьсот': 600,
    'семьсот': 700,
    'восемьсот': 800,
    'девятьсот': 900,
    'тысяча': 10**3,
    'миллион': 10**6,
    'миллиард': 10**9,
    'триллион': 10**12,
}
DOT = eq('.')
INT = type('INT')
THOUSANDTH = rule(caseless_pipeline(['тысячных', 'тысячная'])).interpretation(const(10**-3))
HUNDREDTH = rule(caseless_pipeline(['сотых', 'сотая'])).interpretation(const(10**-2))
TENTH = rule(caseless_pipeline(['десятых', 'десятая'])).interpretation(const(10**-1))
THOUSAND = or_(
    rule(caseless('т'), DOT),
    rule(caseless('тыс'), DOT.optional()),
    rule(normalized('тысяча')),
    rule(normalized('тыща'))
).interpretation(const(10**3))
MILLION = or_(
    rule(caseless('млн'), DOT.optional()),
    rule(normalized('миллион'))
).interpretation(const(10**6))
MILLIARD = or_(
    rule(caseless('млрд'), DOT.optional()),
    rule(normalized('миллиард'))
).interpretation(const(10**9))
TRILLION = or_(
    rule(caseless('трлн'), DOT.optional()),
    rule(normalized('триллион'))
).interpretation(const(10**12))
MULTIPLIER = or_(
    THOUSANDTH,
    HUNDREDTH,
    TENTH,
    THOUSAND,
    MILLION,
    MILLIARD,
    TRILLION
).interpretation(Number.multiplier)
NUM_RAW = rule(morph_pipeline(NUMS_RAW).interpretation(Number.int.normalized().custom(NUMS_RAW.get)))
NUM_INT = rule(INT).interpretation(Number.int.custom(int))
NUM = or_(
    NUM_RAW,
    NUM_INT
).interpretation(Number.int)
NUMBER = or_(
    rule(NUM, MULTIPLIER.optional())
).interpretation(Number)