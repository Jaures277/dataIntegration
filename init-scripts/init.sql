-- Création de la base de données
CREATE DATABASE pret_etudiant_db;

-- Suppression de la table si elle existe déjà
DROP TABLE IF EXISTS pret_etudiant;

-- Création de la table
CREATE TABLE pret_etudiant (
    nan_ope_id BIGINT,
    nan_school TEXT,
    nan_state TEXT,
    nan_zip_code TEXT,
    nan_school_type TEXT,
    subsidized_recipients INTEGER,
    subsidized_loans_originated_count INTEGER,
    subsidized_loans_originated_amount BIGINT,
    subsidized_disbursements_count INTEGER,
    subsidized_disbursements_amount BIGINT,
    unsubsidized_recipients INTEGER,
    unsubsidized_loans_originated_count INTEGER,
    unsubsidized_loans_originated_amount BIGINT,
    unsubsidized_disbursements_count INTEGER,
    unsubsidized_disbursements_amount BIGINT,
    parent_plus_recipients INTEGER,
    parent_plus_loans_originated_count INTEGER,
    parent_plus_loans_originated_amount BIGINT,
    parent_plus_disbursements_count INTEGER,
    parent_plus_disbursements_amount BIGINT,
    grad_plus_recipients INTEGER,
    grad_plus_loans_originated_count INTEGER,
    grad_plus_loans_originated_amount BIGINT,
    grad_plus_disbursements_count INTEGER,
    grad_plus_disbursements_amount BIGINT,
    processed_timestamp TIMESTAMP,
    source_files_count INTEGER
);

