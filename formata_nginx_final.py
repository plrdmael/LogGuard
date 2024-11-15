import re
import csv
from datetime import datetime
import os
import logging

class ConverterFile():
    CSV_RESULT_FILE = 'Ressources/Normalized/batch.csv'

    def __init__(self,input_file,batch_size=25):

        self.input_file=input_file
        self.BATCH_SIZE = batch_size
        self.batch = []
        self.batch_data=[]
        self.counter = 0
        self._reset_csv_file()

    def _reset_csv_file(self):
        try:
            os.remove(self.CSV_RESULT_FILE)
        except FileNotFoundError:
            pass

    def filter_lines_with_remote_address(self,line):
        # Cherche la sous-chaîne "RemoteAddress"
        start_index = line.find("RemoteAddress=")
        if start_index != -1:
            # Conserve la partie de la ligne à partir de "RemoteAddress"
            filtered_line = line[start_index:]
            return filtered_line
        else :
            return ''

    def parse_line(self, line_id, line_pre):
        line = self.filter_lines_with_remote_address(line_pre)
        matches = re.findall(r'"(?:\\.|[^\\"])*"|\S+', line)

        try : 
            if not matches or len(matches) > 18:
                with open('Ressources/error.log','a') as f :
                    f.write(f"{line_id}, {line_pre}\n")
                    
            else : 

                remote_addr = matches[0]
                remote_addr = re.sub(r'^RemoteAddress=','',remote_addr)
                remote_user = matches[1]
                time_local_str = matches[2]
                time_local_str = re.sub(r'^TimeLocal=', '', time_local_str)

                # Extract and validate status and size
                try:
                    size = matches[8]
                except ValueError:
                    logging.error(f"Skipping line with invalid status/size: {line}")
                    return False

                referer = matches[9]
                user_agent = matches[10]

                # Correctly parsing date and time with timezone
                time_local = datetime.strptime(time_local_str, '%d/%b/%Y:%H:%M:%S')

                return {
                    'id': line_id,
                    'RemoteAddress': remote_addr,
                    'RemoteUser': remote_user,
                    'TimeLocal': time_local,
                    'Request': matches[4],
                    'URL': matches[5],
                    'Version': matches[6],
                    'Status': matches[7],
                    'BodyBytesSent': size,
                    'Referer': referer,
                    'UserAgent': user_agent,
                    'token':matches[16]
                }

        except Exception as e:
            print(f"Error parsing line: {e}, Line: {line}, Matches: {matches}")
            return False
            
    def save(self):
        if os.path.exists(self.CSV_RESULT_FILE):
            os.remove(self.CSV_RESULT_FILE)

        for line_id, line in enumerate(self.batch,self.counter+1):
            data = self.parse_line(line_id,line)
            print(data)
            if data != None and data != False:
                self.batch_data.append(data)
        self.save_to_csv()
        return True

    def stack_to_batch(self, line):
        self.batch.append(line)
        if len(self.batch) >= self.BATCH_SIZE:
            #print(f'Converted {self.counter} records')
            self.save()
            return True
        else :
            return False

    def save_to_csv(self):
        # if not self.batch:
        #     return False

        with open(self.CSV_RESULT_FILE, 'a', newline='') as csvfile, open("Ressources/Normalized/dataNorm.csv","a",newline="") as datafile:
            print(self.batch_data)
            print(self.batch)
            writer = csv.DictWriter(csvfile, fieldnames=self.batch_data[0].keys())
            writer2 = csv.DictWriter(datafile, fieldnames=self.batch_data[0].keys())
            if csvfile.tell() == 0:
                writer.writeheader()
            if datafile.tell() == 0:
                writer2.writeheader()
            for record in self.batch_data:
                writer.writerow(self._clean_record(record))
                writer2.writerow(self._clean_record(record))

        self.counter += len(self.batch)
        self.batch = []
        self.batch_data=[]

        return True

    def _clean_record(self, record):
        cleaned = {}
        for k, v in record.items():
            if isinstance(v, str):
                v = ''.join(c for c in v if 32 <= ord(c) <= 126 or c in '\n\r\t')
                v = '"' + v.replace('"', '""') + '"'
            cleaned[k] = v
        return cleaned

def training(path_to_file):
    converter = ConverterFile(input_file=path_to_file,batch_size=260000)
    with open('Ressources/Raw/nginx/data_overfit2.log', mode='r', newline='', encoding='utf-8') as fichier:
        # Ajouter chaque ligne à la liste
        for ligne in fichier:
            converter.stack_to_batch(ligne)
        return True

# training('Ressources/Raw/nginx/data_overfit2.log')
