from sklearn.ensemble import IsolationForest
import pandas as pd
from sklearn.preprocessing import StandardScaler, LabelEncoder, OneHotEncoder
from sklearn.utils import resample
import pickle

#Encode Categorical Variables
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import IsolationForest
import pickle

class ExtendedLabelEncoder(LabelEncoder):
    def add_labels(self, new_labels):
        self.fit(list(set(self.classes_) | set(new_labels)))

def encode_categorical_column_from_csv(df, columns, encoders=None):
    if encoders is None:
        encoders = {}
    
    for column in columns:
        if column not in encoders:
            encoders[column] = ExtendedLabelEncoder()
            encoders[column].fit(df[column].astype(str))
        df[column] = encoders[column].transform(df[column].astype(str))
        print(encoders.keys())

    return df, encoders

def process_data_from_csv_file(path_to_file, output_score_file="Ressources/Result/anomalies_score_from_csv.csv", output_anomaly="Ressources/Result/anomalies_from_csv.csv"):
    # Charger les données depuis un fichier CSV
    data = pd.read_csv(path_to_file, sep=',')

    date_format = '%Y-%m-%d %H:%M:%S'

    # Convertir la colonne 'Date' en un format datetime
    data['TimeLocal'] = pd.to_datetime(data['TimeLocal'], format=date_format)

    if 'token' in data.columns:
        data["lenToken"] = data['token'].apply(lambda x: len(str(x)) if pd.notnull(x) else -1)  # Handle empty token
    else:
        data["lenToken"] = -1

    if 'URL' in data.columns:
        data["lenURL"] = data['URL'].apply(lambda x: len(str(x)))

    # Keep a copy of the original data
    original_data = data.copy()

    # Encode categorical columns
    categorical_cols = data.select_dtypes(include=['object']).columns
    data, encoders = encode_categorical_column_from_csv(data, categorical_cols)

    # Scale numeric columns
    scaler = StandardScaler()
    numeric_cols = data.select_dtypes(include=['int64', 'float64']).columns
    data[numeric_cols] = scaler.fit_transform(data[numeric_cols])

    # Selection des features finales dynamiquement
    feature_columns = ['lenToken', 'lenURL']
    if 'Request' in data.columns:
        feature_columns.append('Request')
    features = data[feature_columns]

    # Modèle d'Isolation Forest
    model = IsolationForest(contamination=0.0005, random_state=42)
    original_data['anomaly'] = model.fit_predict(features)
    original_data['anomaly_score'] = model.decision_function(features)

    # Filter and output anomalies in original string format
    anomalies = original_data[original_data['anomaly'] == -1]
    anomalies.to_csv(output_anomaly, sep=',', index=False)
    original_data.to_csv(output_score_file, sep=',', index=False)

    # Save models and scalers
    with open('iso_forest_model.pkl', 'wb') as f:
        pickle.dump(model, f)
    with open('scaler.pkl', 'wb') as f:
        pickle.dump(scaler, f)
    with open('encoders.pkl', 'wb') as f:
        pickle.dump(encoders, f)

process_data_from_csv_file("data.csv", "Ressources/Result/anomalies_score_from_csv.csv", "Ressources/Result/anomalies_from_csv.csv")


########################################################################################################################################


def encode_categorical_column_from_line(df, columns,encoder):
    if encoders is None:
        encoders = {}
    
    for column in columns:
        if column not in encoders:
            encoders[column] = ExtendedLabelEncoder()
            encoders[column].fit(df[column].astype(str))
        df[column] = encoders[column].transform(df[column].astype(str))

    return df,encoders

def process_new_data(new_data,model,scaler,encoder):
    # Convertir en DataFrame si nécessaire
    if not isinstance(new_data, pd.DataFrame):
        new_data = pd.DataFrame([new_data])

    original_data = new_data.copy()

    # Vérification de la présence de 'TimeLocal'
    if 'TimeLocal' not in new_data.columns:
        print(f"Erreur : 'TimeLocal' n'est pas présent dans les nouvelles données : {new_data}")
        return pd.DataFrame(), new_data
    
    # Convertir la colonne 'TimeLocal' en format datetime
    date_format = '%d/%b/%Y:%H:%M:%S'
    new_data['TimeLocal'] = pd.to_datetime(new_data['TimeLocal'], format=date_format)

    # Ajouter des fonctionnalités basées sur les longueurs de tokens et URLs
    new_data["lenToken"] = new_data['token'].apply(lambda x: len(str(x)) if pd.notnull(x) else -1) if 'token' in new_data.columns else -1
    new_data["lenURL"] = new_data['URL'].apply(lambda x: len(str(x))) 

    print("Before encoding:")
    print(new_data[["URL", "lenURL"]])

    # Encodage des colonnes catégorielles
    for col in new_data.select_dtypes(include=['object']).columns:
        new_data = encode_categorical_column_from_line(new_data, col,encoder)
    
    print("After encoding:")
    print(new_data[["URL","lenURL"]])

    # Normalisation des données numériques
    numeric_cols = new_data.select_dtypes(include=['int64', 'float64']).columns
    new_data[numeric_cols] = scaler.fit_transform(new_data[numeric_cols])

    # Sélection des features finales et réorganisation des colonnes
    feature_columns = ['URL','lenToken','lenURL','Request']
    missing_columns = [col for col in feature_columns if col not in new_data.columns]
    if missing_columns:
        print(f"Erreur : Les colonnes suivantes sont manquantes dans les nouvelles données : {missing_columns}")
        return pd.DataFrame(), new_data

    # Réorganiser les colonnes dans le bon ordre
    features = new_data[feature_columns]
    #print(features)

    # Prédiction des anomalies
    new_data['anomaly'] = model.predict(features)
    new_data['anomaly_score'] = model.decision_function(features)

    original_data['anomaly'] = new_data['anomaly']
    original_data['anomaly_score'] = new_data['anomaly_score']

    # Filtrage des anomalies
    anomalies = original_data[original_data['anomaly'] == -1]

    with open('Ressources/Result/anomalies_scores_nginx_realtime.csv','a',newline='') as csv:
        original_data.to_csv(csv,sep=',', index=False)
    with open('Ressources/Result/anomalies_nginx_realtime.csv','a',newline='') as csv:
        anomalies.to_csv(csv,sep=',', index=False)
    
    return anomalies, new_data

from formata_nginx_final import LineConverter

converter=LineConverter()

with open('iso_forest_model.pkl', 'rb') as f:
    model = pickle.load(f)
with open('scaler.pkl', 'rb') as f:
    scaler = pickle.load(f)
with open('encoder.pkl','rb') as f:
    encoder = pickle.load(f)
print(encoder)
