import os
import pandas as pd
import re
from hdfs import InsecureClient

# === Configuration ===
DOSSIER_XLS = "data"
FICHIER_CSV = "FL_Dashboard_merged.csv"
HDFS_URL = "http://namenode:9870"
HDFS_USER = "root"
CHEMIN_HDFS = f"/data/{FICHIER_CSV}"

# === Fonction de standardisation des noms de colonnes ===
def standardiser_colonnes(df):
    """
    Standardise les noms de colonnes selon les règles NSLDS
    """
    print("🔧 Standardisation des noms de colonnes...")
    
    # Mapping des colonnes de base
    column_mapping = {
        'OPE ID': 'ope_id',
        'School': 'school_name',
        'State': 'state_code',
        'Zip Code': 'zip_code',
        'School Type': 'school_type'
    }
    
    # Types de prêts et leurs codes
    loan_types_mapping = {
        'FFEL SUBSIDIZED': 'subsidized',
        'FFEL UNSUBSIDIZED': 'unsubsidized',
        'FFEL PARENT PLUS': 'parent_plus',
        'FFEL GRAD PLUS': 'grad_plus',
        'DIRECT SUBSIDIZED': 'direct_subsidized',
        'DIRECT UNSUBSIDIZED': 'direct_unsubsidized',
        'DIRECT PARENT PLUS': 'direct_parent_plus',
        'DIRECT GRAD PLUS': 'direct_grad_plus'
    }
    
    # Métriques et leurs codes
    metrics_mapping = {
        'Recipients': 'recipients',
        '# of Loans Originated': 'loans_originated_count',
        '$ of Loans Originated': 'loans_originated_amount',
        '# of Disbursements': 'disbursements_count',
        '$ of Disbursements': 'disbursements_amount'
    }
    
    # Construction du mapping complet
    nouvelles_colonnes = {}
    
    for col in df.columns:
        col_str = str(col).strip()
        nouvelle_colonne = None
        
        # Colonnes de base
        if col_str in column_mapping:
            nouvelle_colonne = column_mapping[col_str]
        else:
            # Colonnes de prêts (format: "TYPE_METRIC" ou "TYPE METRIC")
            for loan_type, loan_code in loan_types_mapping.items():
                for metric, metric_code in metrics_mapping.items():
                    # Patterns possibles
                    patterns = [
                        f"{loan_type}_{metric}",
                        f"{loan_type} {metric}",
                        f"{loan_type}_{metric}",
                        f"{loan_type}.{metric}"
                    ]
                    
                    for pattern in patterns:
                        if col_str == pattern or col_str.replace('\n', ' ').replace('\t', ' ') == pattern:
                            nouvelle_colonne = f"{loan_code}_{metric_code}"
                            break
                    
                    if nouvelle_colonne:
                        break
                if nouvelle_colonne:
                    break
        
        # Si pas de mapping trouvé, standardisation générique
        if nouvelle_colonne is None:
            nouvelle_colonne = col_str.lower()
            nouvelle_colonne = re.sub(r'[^a-z0-9]', '_', nouvelle_colonne)
            nouvelle_colonne = re.sub(r'_+', '_', nouvelle_colonne)
            nouvelle_colonne = nouvelle_colonne.strip('_')
            
            # Remplacements spécifiques
            nouvelle_colonne = nouvelle_colonne.replace('__of_', '_')
            nouvelle_colonne = nouvelle_colonne.replace('_of_', '_')
            nouvelle_colonne = nouvelle_colonne.replace('number_of', 'count')
            nouvelle_colonne = nouvelle_colonne.replace('amount_of', 'amount')
        
        nouvelles_colonnes[col] = nouvelle_colonne
    
    # Application du renommage
    df_renamed = df.rename(columns=nouvelles_colonnes)
    
    print(f"✅ {len(nouvelles_colonnes)} colonnes standardisées")
    
    # Affichage des changements
    print("\n📋 Mapping des colonnes:")
    for ancien, nouveau in list(nouvelles_colonnes.items())[:10]:  # Afficher les 10 premiers
        print(f"   '{ancien}' → '{nouveau}'")
    if len(nouvelles_colonnes) > 10:
        print(f"   ... et {len(nouvelles_colonnes) - 10} autres")
    
    return df_renamed

# === Fonction de nettoyage rapide des données ===
def nettoyer_donnees(df):
    """
    Effectue un nettoyage rapide des données
    """
    print("🧹 Nettoyage rapide des données...")
    
    df_clean = df.copy()
    
    # Suppression des lignes entièrement vides
    df_clean.dropna(how="all", inplace=True)
    
    # Nettoyage des colonnes numériques (montants et compteurs)
    numeric_patterns = ['amount', 'count', 'recipients', 'disbursements', 'loans']
    
    for col in df_clean.columns:
        if any(pattern in col.lower() for pattern in numeric_patterns):
            # Nettoyage des valeurs monétaires et numériques
            if pd.api.types.is_object_dtype(df_clean[col]):
                df_clean[col] = df_clean[col].astype(str)
                df_clean[col] = df_clean[col].str.replace(r'[$,]', '', regex=True)
                df_clean[col] = df_clean[col].str.replace(r'[^0-9.-]', '', regex=True)
                df_clean[col] = df_clean[col].replace('', '0')
                df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce').fillna(0)
    
    # Nettoyage des colonnes texte
    text_columns = ['school_name', 'state_code', 'school_type']
    for col in df_clean.columns:
        if any(text_col in col.lower() for text_col in text_columns):
            if col in df_clean.columns:
                df_clean[col] = df_clean[col].astype(str).str.strip().str.upper()
    
    # Standardisation OPE ID
    if 'ope_id' in df_clean.columns:
        df_clean['ope_id'] = df_clean['ope_id'].astype(str).str.zfill(8)
    
    print(f"✅ Nettoyage terminé: {len(df_clean)} lignes conservées")
    return df_clean

# === Lecture et fusion des fichiers .xls ===
fichiers = sorted([f for f in os.listdir(DOSSIER_XLS) if f.endswith(".xls")])
dfs = []

for fichier in fichiers:
    chemin = os.path.join(DOSSIER_XLS, fichier)
    print(f"📄 Lecture : {fichier}")
    try:
        # Lire les deux lignes d’en-tête à partir de la 5e ligne (index 4)
        header_rows = pd.read_excel(chemin, skiprows=4, nrows=2, header=None).T.fillna(method="ffill")
        
        # Construction des noms de colonnes fusionnées
        colonnes_concat = header_rows[0].astype(str).str.strip() + " " + header_rows[1].astype(str).str.strip()
        colonnes_concat = colonnes_concat.str.replace(r'\s+', ' ', regex=True).str.strip()
        
        # Lecture réelle des données (à partir de la ligne 7)
        df_data = pd.read_excel(chemin, skiprows=6, header=None)
        df_data.columns = colonnes_concat
        dfs.append(df_data)

    except Exception as e:
        print(f"❌ Erreur lors de la lecture de {fichier} : {e}")


# === Fusion ===
final_df = pd.concat(dfs, ignore_index=True)
print(f"\n✅ Fusion terminée : {len(final_df)} lignes")

# === Standardisation des colonnes ===
final_df = standardiser_colonnes(final_df)

# === Nettoyage des données ===
final_df = nettoyer_donnees(final_df)

# === Ajout de métadonnées ===
final_df['processed_timestamp'] = pd.Timestamp.now()
final_df['source_files_count'] = len(fichiers)

print(f"\n📊 DataFrame final:")
print(f"   - Lignes: {len(final_df)}")
print(f"   - Colonnes: {len(final_df.columns)}")
print(f"   - Colonnes standardisées: {list(final_df.columns[:5])}...")

# === Sauvegarde CSV ===
final_df.to_csv(FICHIER_CSV, index=False)
print(f"✅ Fichier CSV généré : {FICHIER_CSV}")

# === Envoi vers HDFS ===
try:
    print(f"\n⬆️ Envoi de {FICHIER_CSV} vers HDFS...")
    client = InsecureClient(HDFS_URL, user=HDFS_USER)
    with open(FICHIER_CSV, "rb") as f:
        client.write(CHEMIN_HDFS, f, overwrite=True)
    print(f"✅ Fichier envoyé vers HDFS à : {CHEMIN_HDFS}")
except Exception as e:
    print(f"❌ Erreur lors de l'envoi vers HDFS : {e}")

# === Sauvegarde du mapping des colonnes ===
try:
    print("\n💾 Sauvegarde du schéma des colonnes...")
    schema_info = {
        'total_columns': len(final_df.columns),
        'column_names': list(final_df.columns),
        'data_types': final_df.dtypes.to_dict(),
        'processing_date': pd.Timestamp.now().isoformat()
    }
    
    import json
    with open('schema_info.json', 'w') as f:
        json.dump(schema_info, f, indent=2, default=str)
    
    print("✅ Schéma sauvegardé dans 'schema_info.json'")
    
except Exception as e:
    print(f"❌ Erreur lors de la sauvegarde du schéma : {e}")