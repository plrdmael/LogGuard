import struct
import datetime
import re

def parse_date_from_binary(record):
    # Utiliser une expression régulière pour extraire la date du format spécifique dans le binaire
    match = re.search(rb'\d{2}/[A-Za-z]{3}/\d{4}:\d{2}:\d{2}:\d{2}', record)
    if match:
        datetime_str = match.group(0).decode('utf-8')
        date_time = datetime.datetime.strptime(datetime_str, '%d/%b/%Y:%H:%M:%S')
        return date_time
    else:
        return None

def combine_binary_files(file1, file2, output_file):
    records = []

    # Lire le contenu des deux fichiers binaires
    with open(file1, 'rb') as f1, open(file2, 'rb') as f2:
        # Lire et traiter les enregistrements de fichier 1
        while True:
            record = f1.read()
            if not record:
                break
            date_time = parse_date_from_binary(record)
            if date_time:
                records.append((date_time, record))
        
        # Lire et traiter les enregistrements de fichier 2
        while True:
            record = f2.read()
            if not record:
                break
            date_time = parse_date_from_binary(record)
            if date_time:
                records.append((date_time, record))

    # Trier les enregistrements par date et heure
    records.sort(key=lambda x: x[0])

    # Écrire le résultat dans le nouveau fichier binaire
    with open(output_file, 'wb') as out:
        for _, record in records:
            out.write(record)

# Usage
combine_binary_files('TO REPLACE your files', 'TO REPLCAE', 'nginx.log')
