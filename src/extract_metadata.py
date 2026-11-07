
import pandas as pd
from pathlib import Path

# 1. Définir les chemins
BASE_DIR = Path(__file__).resolve().parent.parent

# Adapter si ton dossier s'appelle "ressources"
RESOURCE_DIR = BASE_DIR / "ressources"
RESULT_DIR = BASE_DIR / "results"

CSV_FILE = RESOURCE_DIR / "Data_Entry_2017_v2020.csv"
TRAIN_FILE = RESOURCE_DIR / "train_val_list.txt"
TEST_FILE = RESOURCE_DIR / "test_list.txt"

RESULT_DIR.mkdir(exist_ok=True)

 
# 2. Vérifier la présence du CSV
if not CSV_FILE.exists():
    raise FileNotFoundError(f"Fichier introuvable : {CSV_FILE}")

# 3. Extraire les métadonnées
print("Lecture du fichier CSV...")

data = pd.read_csv(CSV_FILE)

print("Nombre de lignes :", len(data))

# 4. Sélectionner les informations utiles
columns = [
    "Image Index",
    "Finding Labels",
    "Patient ID",
    "Patient Age",
    "Patient Sex",
    "View Position"
]

metadata = data[columns].copy()

# 5. Nettoyer les données textuelles
metadata["Finding Labels"] = (
    metadata["Finding Labels"].fillna("").astype(str).str.strip()
)

# 6. Extraire les labels sous forme de listes
metadata["Finding Labels"] = metadata["Finding Labels"].apply(
    lambda labels: labels.split("|") if labels else []
)

# 7. Lire les listes train/validation et test
if TRAIN_FILE.exists():
    train_images = set(TRAIN_FILE.read_text().splitlines())
else:
    train_images = set()

if TEST_FILE.exists():
    test_images = set(TEST_FILE.read_text().splitlines())
else:
    test_images = set()

# 8. Identifier le groupe de chaque image
def get_split(image_name):
    if image_name in train_images:
        return "train_val"
    elif image_name in test_images:
        return "test"
    return "unknown"

metadata["Dataset Split"] = metadata["Image Index"].apply(get_split)

# 9. Créer une table avec une ligne par image et pathologie
labels_table = metadata.explode("Finding Labels")

# 10. Sauvegarder les résultats
metadata.to_csv(
    RESULT_DIR / "metadata_extracted.csv",
    index=False
)

labels_table.to_csv(
    RESULT_DIR / "image_labels.csv",
    index=False
)

print("\nCollecte terminée !")
print("Images extraites :", len(metadata))
print("Nombre de labels :", len(labels_table))
print("Images train/val :", (metadata["Dataset Split"] == "train_val").sum())
print("Images test :", (metadata["Dataset Split"] == "test").sum())
print("Images sans split :", (metadata["Dataset Split"] == "unknown").sum())
print("\nFichiers enregistrés dans :", RESULT_DIR)
