import asyncio
import pandas as pd
import os, json
import pytz
from datetime import datetime
import psycopg2

basedir = '/home/ubuntu/DarwinAI/media/'
clients = {}

def datetime_tz():
    timezone = pytz.utc
    return timezone.localize(datetime.today())

def make_connection(host, port):
    task = None
    file = open("/home/ubuntu/files_to_processing.txt","r+")
    links = file.readlines()
    if (len(links) > 0):
        file.seek(0)
        file.truncate()
        file.close()
    task = asyncio.Task(handle_client(links, host, port))
    
    clients[task] = (host, port)

    def client_done(task):
        del clients[task]
        make_connection(host, port)

    task.add_done_callback(client_done)

@asyncio.coroutine
def handle_client(links, host, port):
    if (len(links) > 0):
        conn = psycopg2.connect(
            host="localhost",
            database="darwin",
            user="bassist",
            password="Rfrfie4rf"
        )
        for link in links:
            print(link)
            client_reader, client_writer = yield from asyncio.open_connection(host, port)
            cur = conn.cursor()
            try:
                data = yield from asyncio.wait_for(client_reader.readline(), timeout=None)
        
                if data is None:
                    print("Didn't get READY-response")
                    return
        
                sdata = data.decode().rstrip()
                print("Received ", sdata)
                if sdata != "READY":
                    print("Expected READY, received '", sdata, "'")
                    return
                
                client_writer.write((link+"\n").encode())
                daiml_sent = datetime_tz()
                
                salt = link.split('/')[3]
                print(salt)
                file_path = os.path.join(basedir, 'decrypting', salt)
                print(file_path)
                record_dir = os.path.join('records', salt)
                
                message = yield from asyncio.wait_for(client_reader.readline(), timeout=None)
                if message is None:
                    print("Echo received None")
                    return
                daiml_arrived = datetime_tz()
                daiml_spent = (daiml_arrived - daiml_sent).total_seconds() * 1000
#                 sql = 'SELECT size FROM calls_call WHERE record LIKE \'' + record_dir + '%\';'
#                 cur.execute(sql)
#                 size = cur.fetchone()[0]
#                 conn.commit()
#                 daiml_spent = daiml_spent * 1024 * 1024 / size
                sdata = message.decode().rstrip()
                daiml_start = ''
                daiml_end = ''
                
                if sdata == 'ok':
                    count = yield from asyncio.wait_for(client_reader.readline(), timeout=None)
                    if count is None:
                        print("Echo received None")
                        return
                    sdata = count.decode().rstrip()
                    for i in range(int(sdata)):
                        names = yield from asyncio.wait_for(client_reader.readline(), timeout=None)
                        if names is None:
                            print("Echo received None")
                            return
                        sdata = names.decode().rstrip()
                        df = pd.DataFrame(columns = eval(sdata))
                    
                        count = yield from asyncio.wait_for(client_reader.readline(), timeout=None)
                        if count is None:
                            print("Echo received None")
                            return
                        sdata = count.decode().rstrip()
                    
                        for j in range(int(sdata)):
                            data = yield from asyncio.wait_for(client_reader.readline(), timeout=10.0)
                            sdata = data.decode().rstrip()
                            json_data = eval(sdata)
                            df = df.append(json_data, ignore_index=True)
                        
                        if not os.path.isdir(file_path):
                            os.makedirs(file_path)
                            
                        if i == 0: df.to_csv(file_path+'/speech.csv', index=False)
                        elif i == 1: df.to_csv(file_path+'/loud.csv', index=False)
                        elif i == 2: df.to_csv(file_path+'/clear.csv', index=False)
                        elif i == 3:
                            daiml_start = df.iloc[0]['time']
                            daiml_end = df.iloc[1]['time']
                else:
                    record_dir = os.path.join(basedir, 'records', salt)
                    if (sdata != 'ok'):
                        os.rename(record_dir, record_dir+"-"+sdata)
                        with open("/home/ubuntu/DAIM_errors.txt", 'a') as file:
                            file.write(str(datetime_tz()) + "\n" + record_dir + "/\n" + sdata + "\n")
                
                with open("/home/ubuntu/files_to_postanalyze.txt", 'a') as file:
                    file.write(salt + "\n")
                sql = ('UPDATE calls_call SET '
                'debug_time_daiml_sent = \'' + str(daiml_sent) + '\', '
                'debug_time_daiml_start = \'' + str(daiml_start) + '\', '
                'debug_time_daiml_end = \'' + str(daiml_end) + '\', '
                'debug_time_daiml_arrived = \'' + str(daiml_arrived) + '\', '
                'debug_time_daiml_spent = \'' + str(int(daiml_spent)) + '\' '
                'WHERE record LIKE \'' + record_dir + '%\';')
                cur.execute(sql)
                conn.commit()
            finally:
                client_writer.close()
                print("Disconnected from ", host, ":", port)
                cur.close()
                
        conn.close()

if __name__ == '__main__':
    asyncio.set_event_loop(asyncio.new_event_loop())
    loop = asyncio.get_event_loop()
    make_connection('3.123.70.241', 4316)
    loop.run_forever()