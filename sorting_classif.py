import csv
import re
import urllib.parse
import os

# Liste de patterns pour différentes attaques
patterns = {
    'SQL Injection': re.compile(r"('|--|;|\/\*|\*\/|UNION|SELECT|DROP|INSERT|UPDATE|DELETE|%27|%23|%3B)", re.IGNORECASE),
    'XSS': re.compile(r"(<script>|%3Cscript|%3C\/script|<img|%3Cimg|javascript:|%3C|%3E)", re.IGNORECASE),
    'LFI': re.compile(r"(\/etc\/passwd|\/etc\/shadow|\/proc\/self|\.\/|\/\.\.|\/%2e\/|%2f%2e%2e%2f)", re.IGNORECASE),
    'RFI': re.compile(r"(http:\/\/|https:\/\/|ftp:\/\/|%3A%2F%2F)", re.IGNORECASE),
    'Command Injection': re.compile(r"(\||;|&|>|<|`|\\|%7C|%3B|%26|%3E|%3C|%60|%5C)", re.IGNORECASE),
    'Directory Traversal': re.compile(r"(\.\.\/|\.\.\\|%2e%2e%2f|%2e%2e%5c)", re.IGNORECASE)
}

def load_whitelist(path_to_file):
    with open(path_to_file,'r') as file:
        ip_whitelist = file.readlines()
    return ip_whitelist

# Fonction pour analyser une URL
def analyze_url(url):
    results = {}
    for attack, pattern in patterns.items():
        if pattern.search(url):
            results[attack] = True
        else:
            results[attack] = False
    return results

# Fonction pour déterminer si une alerte critique est nécessaire
def determine_critical_alert(results, http_status):
    # Vérifie si l'URL contient une attaque potentielle et le statut HTTP est un code 2xx
    return "Oui" if any(results.values()) and http_status.startswith('2') else "Non"

# Fonction pour obtenir les types d'attaque détectés
def get_attack_types(results):
    # Filtrer les types d'attaque détectés
    attack_types = [attack for attack, detected in results.items() if detected]
    return ', '.join(attack_types) if attack_types else 'Aucune'

# Fonction pour traiter une ligne de log
def process_log_row(row):
    try:
        url = urllib.parse.unquote(row[5])  # Supposant que l'URL est dans la 6ème colonne
        http_status = row[7]  # Supposant que le statut HTTP est dans la 8ème colonne
    except IndexError:
        raise ValueError("La ligne du CSV ne contient pas assez de colonnes pour l'URL ou le statut HTTP")

    results = analyze_url(url)
    critical_alert = determine_critical_alert(results, http_status)
    attack_types = get_attack_types(results)

    # Ajouter l'alerte critique et les types d'attaque à la ligne
    row.append(attack_types)
    row.append(critical_alert)
    return row

def process_to_csv(path_to_file,output='Ressources/Result/logs_nginx_sorted.csv'):
    treated_rows = []
    with open(path_to_file,'r',newline='') as file :
        reader = csv.reader(file)
        header = next(reader)
        for row in reader :
            try:
                treated_rows.append(process_log_row(row))
            except ValueError as e :
                print(f"Erreur lors du traitement de la ligne : {e}")
    
    with open(output,'a',newline='') as csvfile:
        fieldnames = header + ['Types d\'attaque','Alerte Critique']
        writer = csv.writer(csvfile)
        file_exists = os.path.isfile(output)
        write_header = not file_exists or os.path.getsize(output) == 0
        if write_header == True :
            writer.writerow(fieldnames)
        writer.writerows(treated_rows)
        print(f"Analysis results written to {output}")

# # Chemin du fichier CSV contenant les logs d'anomalies nginx
# csv_file_path = 'Ressources/Result/anomalies_from_csv.csv'
# output_csv_file_path = 'Ressources/Result/logs_nginx_sorted.csv'

# # Liste pour stocker toutes les lignes analysées
# analyzed_logs = []

# try:
#     # Lire les logs depuis le fichier CSV
#     with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
#         csvreader = csv.reader(csvfile)
#         header = next(csvreader)
#         for row in csvreader:
#             try:
#                 analyzed_row = process_log_row(row)
#                 analyzed_logs.append(analyzed_row)
#             except ValueError as e:
#                 print(f"Erreur lors du traitement de la ligne : {e}")

#     # Écrire les logs analysés dans un nouveau fichier CSV
#     with open(output_csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
#         fieldnames = header + ['Types d\'Attaque', 'Alerte Critique']
#         csvwriter = csv.writer(csvfile)
#         csvwriter.writerow(fieldnames)  # Écrire l'en-tête
#         csvwriter.writerows(analyzed_logs)  # Écrire toutes les lignes analysées

#     print(f"Analysis results written to {output_csv_file_path}")

# except FileNotFoundError:
#     print(f"Le fichier {csv_file_path} est introuvable.")
# except IOError as e:
#     print(f"Erreur lors de l'ouverture ou de l'écriture dans le fichier : {e}")
