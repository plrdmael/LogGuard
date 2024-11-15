from sklearn.ensemble import IsolationForest
import pandas as pd
from sklearn.preprocessing import StandardScaler, LabelEncoder, OneHotEncoder
from sklearn.utils import resample
import pickle
from joblib import dump,load
import os
import numpy as np

def load_or_create_encoders(encoders_path):
    """
    Load encoders from file or create a new dictionary of encoders.
    
    Parameters:
    encoders_path (str): Path to the encoders file.
    
    Returns:
    dict: A dictionary of encoders.
    """
    if os.path.exists(encoders_path):
        with open(encoders_path, 'rb') as f:
            encoders = pickle.load(f)
    else:
        encoders = {}
    return encoders

def load_or_create_scaler(scaler_path):
    """
    Load scaler from file or create a new StandardScaler.
    
    Parameters:
    scaler_path (str): Path to the scaler file.
    
    Returns:
    StandardScaler: A StandardScaler object.
    """
    if os.path.exists(scaler_path):
        with open(scaler_path, 'rb') as f:
            scaler = pickle.load(f)
    else:
        scaler = StandardScaler()
    return scaler

def update_label_encoder(encoder, new_labels):
    """
    Update a LabelEncoder with new labels.
    
    Parameters:
    encoder (LabelEncoder): The LabelEncoder to update.
    new_labels (list): New labels to add to the encoder.
    
    Returns:
    LabelEncoder: Updated LabelEncoder.
    """
    existing_labels = set(encoder.classes_)
    combined_labels = existing_labels.union(new_labels)
    encoder = LabelEncoder()
    encoder.fit(list(combined_labels))
    return encoder

def save_encoders(encoders, encoders_path):
    """
    Save encoders to a file.
    
    Parameters:
    encoders (dict): Dictionary of encoders.
    encoders_path (str): Path to the encoders file.
    """
    with open(encoders_path, 'wb') as f:
        pickle.dump(encoders, f)

def encode_categorical_column_from_csv(df, columns, encoders_path="encoders.pkl"):
    encoders = load_or_create_encoders(encoders_path)
    
    for column in columns:
        if column not in encoders:
            # Create and fit new encoder if not already present
            encoders[column] = LabelEncoder()
            encoders[column].fit(df[column].astype(str))
        else:
            # Update existing encoder with new values
            current_labels = set(df[column].astype(str).unique())
            known_labels = set(encoders[column].classes_)
            new_labels = current_labels - known_labels
            
            if new_labels:
                print(f"Updating encoder for column '{column}' with new labels: {new_labels}")
                encoders[column] = update_label_encoder(encoders[column], new_labels)
        
        df[column] = encoders[column].transform(df[column].astype(str))
    
    # Save the updated encoders
    save_encoders(encoders, encoders_path)
    
    return df, encoders

def process_data_from_csv_file(path_to_file,model, output_score_file="Ressources/Result/anomalies_score_from_csv.csv", output_anomaly="Ressources/Result/anomalies_from_csv.csv"):
    # Charger les données depuis un fichier CSV
    data = pd.read_csv(path_to_file, sep=',')

    date_format = '%Y-%m-%d %H:%M:%S'

    # Convertir la colonne 'TimeLocal' en un format datetime
    data['TimeLocal'] = pd.to_datetime(data['TimeLocal'], format=date_format)

    if 'token' in data.columns:
        data["lenToken"] = data['token'].apply(lambda x: len(str(x)) if pd.notnull(x) else -1)
    else:
        data["lenToken"] = -1

    if 'URL' in data.columns:
        data["lenURL"] = data['URL'].apply(lambda x: len(str(x)))
    else:
        print("Warning: 'URL' column is missing from the data.")
        data["lenURL"] = -1

    # Keep a copy of the original data
    original_data = data.copy()
    # Encode categorical columns
    categorical_cols = data.select_dtypes(include=['object']).columns
    data, _ = encode_categorical_column_from_csv(data, list(categorical_cols))

    # Scale numeric columns
    scaler = StandardScaler()
    numeric_cols = data.select_dtypes(include=['int64', 'float64']).columns
    data[numeric_cols] = scaler.fit_transform(data[numeric_cols])

    # Sélection des features finales dynamiquement
    feature_columns = ['lenToken', 'lenURL','URL','RemoteAddress','token']
    if 'Request' in data.columns:
        features = data[feature_columns]
    else:
        features = data[['lenToken', 'lenURL','URL']]  # Ajuster si 'Request' est manquant

    # Modèle d'Isolation Forest
    original_data['anomaly'] = model.predict(features)
    original_data['anomaly_score'] = model.decision_function(features)

    mean_score = np.mean(original_data['anomaly_score'])
    std_score = np.std(original_data['anomaly_score'])


    threshold = mean_score*(1-(10*std_score))

    print(f"Mean anomaly score: {mean_score}, Std anomaly score: {std_score}, threshold : {threshold}, ")
    # Filter and output anomalies in original string format
    anomalies = original_data[(original_data['anomaly_score'] < threshold) & (original_data['anomaly_score'] < 0.09)]
    file_exists1 = os.path.isfile(output_anomaly)
    write_header1 = not file_exists1 or os.path.getsize(output_anomaly) == 0
    file_exists2 = os.path.isfile(output_score_file)
    write_header2 = not file_exists2 or os.path.getsize(output_score_file) == 0

    anomalies.to_csv(output_anomaly, sep=',', index=False,mode='a',header=write_header1)
    original_data.to_csv(output_score_file, sep=',', index=False,mode='a',header=write_header2)

    # # Save models and scalers
    #dump(model,"iso_forest_model.modele")
    # with open('scaler.pkl', 'wb') as f:
    #     pickle.dump(scaler, f)
    # with open('encoders.pkl', 'wb') as f:
    #     pickle.dump(encoders, f)

    # print("Model, scaler, and encoders saved successfully.")

#process_data_from_csv_file(path_to_file="Ressources/Normalized/data_training.csv",model = load("iso_forest_model.joblib"),output_score_file="Ressources/Result/training_score.csv",output_anomaly="Ressources/Result/training_anomalie.csv")

########################################################################################################################################

