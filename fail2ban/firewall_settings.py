import csv
import paramiko

################### Détecter les adresses malicieuses ###########################################

# Fonction pour charger les adresses IP déjà bloquées depuis un fichier
def load_blocked_ips(file_path="fail2ban/blocked_ips.txt"):
    blocked_ips = set()
    try:
        with open(file_path, 'r') as file:
            for line in file:
                blocked_ips.add(line.strip())
    except FileNotFoundError:
        # Si le fichier n'existe pas, nous le créons
        open(file_path, 'w').close()
    return blocked_ips

# Fonction pour enregistrer une adresse IP bloquée dans un fichier
def save_blocked_ip(ip_address, file_path):
    with open(file_path, 'a') as file:
        file.write(ip_address + '\n')

# Fonction pour lire le fichier CSV et extraire les adresses IP
def read_csv_and_process(file_path):
    blocked_ips = load_blocked_ips()
    with open(file_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            ip_address = row['RemoteAddress']
            if ip_address not in blocked_ips:
                print(ip_address)
                save_blocked_ip(ip_address,blocked_ips_path)
                blocked_ips.add(ip_address)


# TO REPLACE your files
blocked_ips_path = 'fail2ban/blocked_ips.txt'
blocked_ips_file = 'blocked_ips.txt'
load_blocked_ips(blocked_ips_path)
read_csv_and_process("Ressources/Result/logs_nginx_sorted.csv")

###################### Envoie du fichier aux serveurs concernés ############################################

servers = [
    {'ip': 'TO REPLACE yourIP', 'username': 'kali', 'password': 'kali'}]

def send_blocked_ips_file():
    for server in servers:
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(server['ip'], username=server['username'], password=server['password'])

            sftp = ssh.open_sftp()
            remote_path = f'/home/kali/Desktop/{blocked_ips_file}'
            print(f"Tentative d'envoi du fichier vers : {remote_path}")
            sftp.put(blocked_ips_path, remote_path)
            print(f"Fichier {blocked_ips_file} envoyé avec succès à {server['ip']}.")
            sftp.close()
            ssh.close()
        except Exception as e:
            print(f"Erreur lors de l'envoi du fichier à {server['ip']} : {e}")

send_blocked_ips_file()

############# Pour Bannir les adresses IP ##################################################

import subprocess

def ban_ip(ip_address):
    command = ["sudo", "fail2ban-client", "set", "sshd", "banip", ip_address]
    result = subprocess.run(command, check=True, capture_output=True, text=True)
    print(result.stdout)

def unban_ip(ip_address):
    command = ["sudo", "fail2ban-client", "set", "sshd", "unbanip", ip_address]
    result = subprocess.run(command, check=True, capture_output=True, text=True)
    print(result.stdout)

# if __name__ == "__main__":
#     ip_to_ban = ""
#     ban_ip(ip_to_ban)

#     # Pour débloquer l'IP
#     # unban_ip(ip_to_ban)
