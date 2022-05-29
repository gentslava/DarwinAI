import asyncio
import os, json, math
import traceback
import pytz
from datetime import datetime
import psycopg2
from DAIML_WA_NEW_SEARCH.main import InfoExtractor

basedir = '/home/ubuntu/DarwinAI/media/'
clients = {}
infoExtractor = InfoExtractor(with_punc = True)

def datetime_tz():
    timezone = pytz.utc
    return timezone.localize(datetime.today())

def notNan(dictionary):
    for key1 in list(dictionary.keys()):
        if (isinstance(dictionary[key1], dict)):
            for key2 in list(dictionary[key1].keys()):
                dictionary[key1][key2] = '-' if dictionary[key1][key2] != dictionary[key1][key2] else dictionary[key1][key2]
        else:
            dictionary[key1] = '-' if dictionary[key1] != dictionary[key1] else dictionary[key1]
    return dictionary

def make_connection():
    task = None
    file = open("/home/ubuntu/files_to_postanalyze.txt","r+")
    salts = file.readlines()
    if (len(salts) > 0):
        file.seek(0)
        file.truncate()
        file.close()
    task = asyncio.Task(handle_client(salts))
    
    clients[task] = (salts)

    def client_done(task):
        del clients[task]
        make_connection()

    task.add_done_callback(client_done)

@asyncio.coroutine
def handle_client(salts):
    if (len(salts) > 0):
        conn = psycopg2.connect(
            host="localhost",
            database="darwin",
            user="bassist",
            password="Rfrfie4rf"
        )
        for salt in salts:
            salt = salt.rstrip()
            record_dir = os.path.join('records', salt)
            file_path = os.path.join(basedir, 'decrypting', salt)
            print(file_path)
            cur = conn.cursor()
            try:
                wa_sent = datetime_tz()
                df_result, df_loud, df_additional, df_score, info = infoExtractor.extract(
                    file_path+'/speech.csv',
                    file_path+'/loud.csv',
                    file_path+'/clear.csv'
                )
                wa_arrived = datetime_tz()
                wa_spent = int((wa_arrived - wa_sent).total_seconds() * 1000)
#                 sql = 'SELECT size FROM calls_call WHERE record LIKE \'' + record_dir + '%\';'
#                 cur.execute(sql)
#                 size = cur.fetchone()[0]
#                 conn.commit()
#                 wa_spent = wa_spent * 1024 * 1024 / size
                
                df_result = df_result.fillna('‒')
                df_loud = df_loud.fillna(0)
                df_additional = df_additional.fillna({'pod':'‒'})
                df_additional = df_additional.fillna(0)
                df_score = df_score.fillna(100)
                info = notNan(info)
                df_result.to_csv(file_path+'/result.csv', index=False)
                df_loud.to_csv(file_path+'/loud-res.csv', index=False)
                df_additional.to_csv(file_path+'/additional.csv', index=False)
                df_score.to_csv(file_path+'/score.csv', index=False)
                file = open(file_path+'/info.txt', 'w')
                json.dump(info, file)
                status = 'Обработано'
                
            except FileNotFoundError as e:
                status = 'Ошибка'
                dir_full = os.path.join(basedir, record_dir)
                with open("/home/ubuntu/files_not_found.txt", 'a') as file:
                    file.write(str(datetime.now()) + "\n" + dir_full + "\n" + traceback.format_exc() + "\n")
            
            sql = ('UPDATE calls_call SET '
            'status = \'' + status + '\', '
            'debug_time_wa_sent = \'' + str(wa_sent) + '\', '
            'debug_time_wa_arrived = \'' + str(wa_arrived) + '\', '
            'debug_time_wa_spent = \'' + str(int(wa_spent)) + '\' '
            'WHERE record LIKE \'' + record_dir + '%\';')
            cur.execute(sql)
            conn.commit()
            cur.close()
            
        conn.close()

if __name__ == '__main__':
    asyncio.set_event_loop(asyncio.new_event_loop())
    loop = asyncio.get_event_loop()
    make_connection()
    loop.run_forever()