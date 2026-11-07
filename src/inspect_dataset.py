
import pandas as pd

# Chemin du fichier CSV
csv_path = "ressources/Data_Entry_2017_v2020.csv"

# Charger les métadonnées
data = pd.read_csv(csv_path)

# Afficher les premières lignes
print("Premières lignes du dataset :")
print(data.head())

# Afficher les colonnes
print("\nColonnes disponibles :")
print(data.columns.tolist())

# Afficher le nombre de lignes
print("\nNombre d'images :", len(data))
