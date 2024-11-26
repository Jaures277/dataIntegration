
**Student Loan Data Integration Project**
Ce projet vise à traiter les données des prêts étudiants en exploitant un pipeline de streaming basé sur Kafka, 
Spark et une base de données SQLite. L'objectif principal est d'extraire, transformer et charger des données issues de Kafka, tout en les stockant dans une base SQLite pour analyse et traitement.

**Prérequis**
Avant de commencer, assurez-vous d'avoir installé les éléments suivants :

**Docker et Docker Compose : pour exécuter les services nécessaires.**
Python 3.8+ : pour l'écriture de scripts d'intégration.
DB Browser for SQLite (optionnel) : pour visualiser les données de la base SQLite.

**Architecture**
Le projet utilise l'architecture suivante :

Kafka : pour le streaming de données des prêts étudiants.
Spark Streaming : pour lire les données en temps réel depuis Kafka et les écrire dans une base de données SQLite.
SQLite : pour stocker les données intégrées.
HDFS (futur) : pour la gestion des fichiers sources.
Control Center : pour surveiller Kafka et ses topics.
Installation et démarrage
Étape 1 : Configuration des services Docker
Clonez le dépôt du projet :

**bash**
Copier le code
git clone <url-du-repo>
cd student_loan_project
Vérifiez que le fichier docker-compose.yml est présent. Il contient la configuration des services suivants :

**.Zookeeper
.Kafka
.Schema Registry
.Spark
.Control Center**

**Démarrez les conteneurs avec :**

**bash**
Copier le code
docker-compose up -d
Vérifiez que les conteneurs sont opérationnels :

**bash**
Copier le code
docker ps
Étape 2 : Configuration de Spark Streaming
Assurez-vous que les fichiers nécessaires sont dans le répertoire ./app. Notamment :

spark_streaming_app.py : script Spark pour le traitement des données.
Vérifiez que le fichier sqlite-jdbc-3.46.1.2.jar est placé dans ./jars.

Étape 3 : Streaming des données avec Kafka et Spark
Lancez le producteur Kafka (génération de données de test) :

**bash**
Copier le code
docker exec -it student_loan_project-kafka-producer-1 python /datas/producer.py
L'application Spark est configurée pour lire les messages du topic Kafka student_loan_topic et les écrire dans la base SQLite. Assurez-vous que le conteneur Spark est actif :

**bash**
Copier le code
docker logs student_loan_project-spark-1
Étape 4 : Vérification des données intégrées
Les données sont stockées dans un fichier SQLite créé automatiquement dans le dossier /data. Pour visualiser les données, utilisez DB Browser for SQLite :

Montez le volume Docker pour accéder au fichier ou copiez-le depuis le conteneur :

**bash**
Copier le code
docker cp student_loan_project-spark-1:/tmp/data/student_loan_data.db ./data/
Chargez le fichier student_loan_data.db dans DB Browser pour examiner les tables.

**Structure des dossiers**
Dossier/Fichier	Description
app/	Contient les scripts Spark Streaming.
jars/	Bibliothèque JDBC pour SQLite.
datas/	Contient les fichiers de données sources et les scripts pour le producteur Kafka.
database/	Répertoire pour le stockage persistant de la base SQLite.
docker-compose.yml	Configuration des services Docker.


**Points à améliorer**
HDFS : Ajouter un support pour lire les fichiers FL_Dashboard... depuis HDFS.
Gestion des versions : Mettre en place une stratégie pour gérer différentes versions des données intégrées.
Documentation : Documenter les choix techniques et les solutions utilisées dans le pipeline.
Visualisation : Intégrer un outil comme Tableau ou Power BI pour visualiser les données.
