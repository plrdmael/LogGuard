# Projet : Surveillance et Détection d'Anomalies dans les Logs Nginx

## Description

Ce projet implémente un système de surveillance des fichiers de log Nginx en temps réel. Il surveille un fichier spécifique, traite les nouvelles lignes ajoutées, et détecte les anomalies grâce à un modèle d'apprentissage automatique basé sur un **Isolation Forest**.

Le système repose sur la bibliothèque `watchdog` pour détecter les modifications dans les fichiers et sur des scripts Python pour normaliser, analyser et classifier les logs.

## Fonctionnalités principales

1. **Surveillance de fichiers de log en temps réel** :
   - Utilisation de `watchdog` pour détecter les nouvelles lignes ajoutées au fichier de log cible.
   
2. **Traitement par batch** :
   - Les nouvelles lignes de logs sont accumulées dans un batch pour une analyse groupée.

3. **Détection d'anomalies** :
   - Le traitement des batches utilise un modèle pré-entraîné `iso_forest_260k.pkl` et un scaler (`scaler.pkl`) pour identifier les anomalies dans les logs.

4. **Pipeline automatisé** :
   - Conversion et normalisation des données (avec `ConverterFile`).
   - Analyse et classification des anomalies (`isolation_forest_nginx.py`).
   - Exportation des résultats au format CSV (`sorting_classif.py`).

5. **Exécution de scripts supplémentaires** :
   - Intégration possible avec des scripts Bash ou PowerShell pour d'autres tâches automatisées.

## Prérequis

- **Python 3.x** installé.
- Bibliothèques Python suivantes :
  - `watchdog`
  - `joblib`
  - `pickle`
  - Autres dépendances spécifiques (voir [requirements.txt](#)).

- **Fichiers nécessaires** :
  - `iso_forest_260k.pkl` : modèle pré-entraîné pour la détection d'anomalies.
  - `scaler.pkl` : scaler pour la normalisation des données.

## Installation et utilisation

1. **Cloner le dépôt :**

   ```bash
   git clone <URL_du_dépôt>
   cd <nom_du_répertoire>
