import time
import sys
import logging
from watchdog.observers.polling import PollingObserver
from watchdog.events import FileSystemEventHandler
from formata_nginx_final import ConverterFile
from isolation_forest_nginx import process_data_from_csv_file
from sorting_classif import process_to_csv
import joblib
import pickle
import subprocess

class NewLinesHandler(FileSystemEventHandler):
    def __init__(self, file_path):
        super().__init__()
        print('Debut init')
        self.file_path = file_path
        self.file = open(file_path, 'r',encoding='utf-16-le')
        self.model = joblib.load("iso_forest_260k.pkl")
        print('modele chargé')
        with open('scaler.pkl', 'rb') as f:
            self.scaler = pickle.load(f)
        print('scaler chargé')
        self.file.seek(0, 2)  # Aller à la fin du fichier
        self.converter=ConverterFile(input_file='Ressources/Raw/nginx/serveur.log',batch_size=5)
        print('init fini')

    def on_modified(self, event):
        print("modif detectée")
        if event.src_path == self.file_path:
            self.actions_on_new_lines()

    def actions_on_new_lines(self):
        for line in self.file:
            cond = self.converter.stack_to_batch(line)
            print("debug_actions")
            if cond == True:
                print("debut_actions=true")
                process_data_from_csv_file("Ressources/Normalized/batch.csv",self.model)
                process_to_csv("Ressources/Result/anomalies_from_csv.csv")

if __name__ == "__main__":
    logging.basicConfig(filename='watchdog.log',level=logging.DEBUG,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')

    # sys.stdout = open('watchdog.log','a')
    # sys.stderr = open('watchdog.log','a')
    path_to_watch = 'Ressources/Raw/nginx/'
    file_to_watch = 'Ressources/Raw/nginx/serveur.log'

    event_handler = NewLinesHandler(file_to_watch)
    observer = PollingObserver()
    observer.schedule(event_handler, path=path_to_watch, recursive=False)
    observer.start()
    # Chemin vers le script bash
    bash_script = "./script.sh"
    # Donner les permissions d'exécution au script bash
    # subprocess.run(["chmod", "+x", bash_script])
    # process = subprocess.Popen(bash_script,shell=True)
    # print(f"Script exécuté avec PID : {process.pid}")

    result = subprocess.run(["powershell", "-File","hello.ps1"], capture_output=True, text=True)
    print('Pret')

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()