import re
import csv
import time
from datetime import datetime
import os
import random

class Converter:
    CSV_RESULT_FILE = 'data.csv'
    BATCH_SIZE = 500

    def __init__(self):
        self.batch = []
        self.counter = 0
        self._reset_csv_file()

    def _reset_csv_file(self):
        try:
            os.remove(self.CSV_RESULT_FILE)
        except FileNotFoundError:
            pass

    def parse_line(self, line_id, line):
        matches = re.findall(r'"(?:\\.|[^\\"])*"|\S+', line)

        if not matches or len(matches) < 12:  # Checking if matches contain enough elements
            print(f"Skipping malformed line: {line}")
            return False

        try:
            remote_addr = matches[0]
            remote_user = matches[2]
            time_local_str = matches[3][1:] + ' ' + matches[4][:-1]
            request = matches[5:8]
            status = int(matches[8])
            size = int(matches[9])
            referer = matches[10][1:-1]
            user_agent = matches[11][1:-1]

            if len(request) < 3 or request[0] not in ['"GET', '"POST', '"PUT', '"PATCH', '"DELETE', '"HEAD', '"OPTIONS']:
                request = ['', '', '']

            request = request + [''] * (3 - len(request))
            request_path = re.sub(r'\\(.)', r'\1', request[1])
            
            # Parsing correct de la date et heure avec fuseau horaire
            time_local = int(time.mktime(datetime.strptime(time_local_str, '%d/%b/%Y:%H:%M:%S %z').timetuple()))

        except Exception as e:
            print(f"Error parsing line: {e}")
            print(f"Line: {line}")
            print(f"Matches: {matches}")
            return False

        return {
            'id': line_id,
            'remote_addr': remote_addr,
            'remote_user': remote_user,
            'runtime': random.randint(100, 10000),
            'time_local': time_local,
            'request_type': request[0][1:],
            'request_path': request_path,
            'request_protocol': request[2][:-1],
            'status': status,
            'size': size,
            'referer': referer,
            'user_agent': user_agent
        }

    def save(self):
        if os.path.exists(self.CSV_RESULT_FILE):
            print("CSV results exist. Skipping conversion")
            return False

        with open("TO REPLACE with your file", 'r') as file:
            for line_id, line in enumerate(file, 1):
                data = self.parse_line(line_id, line)
                if data:
                    self.stack_to_batch(data)

        self.save_to_csv()
        return True

    def stack_to_batch(self, line):
        self.batch.append(line)
        if len(self.batch) >= self.BATCH_SIZE:
            self.save_to_csv()
            print(f'Converted {self.counter} records')

    def save_to_csv(self):
        if not self.batch:
            return False

        with open(self.CSV_RESULT_FILE, 'a', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.batch[0].keys())
            if csvfile.tell() == 0:
                writer.writeheader()
            for record in self.batch:
                writer.writerow(self._clean_record(record))

        self.counter += len(self.batch)
        self.batch = []
        return True

    def _clean_record(self, record):
        cleaned = {}
        for k, v in record.items():
            if isinstance(v, str):
                v = ''.join(c for c in v if 32 <= ord(c) <= 126 or c in '\n\r\t')
                v = '"' + v.replace('"', '""') + '"'
            cleaned[k] = v
        return cleaned

if __name__ == "__main__":
    random.seed(1)
    converter = Converter()
    converter.save()
