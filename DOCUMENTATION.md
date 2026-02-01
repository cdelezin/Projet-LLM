
# Projet LLM - Portfolio interactif

Ce projet est réalisé dans le cadre de ma 3e année du BUT Science des Données. Il transforme un portfolio statique en portfolio interactif via un chatbot RAG capable de répondre sur mon parcours, mes compétences et mes expériences professionnelles.

## Pré-requis / Installation : 
- Python 3.11, 3.12 ou 3.13
- Un environnement virtuel (venv)
- Un compte OpenAI avec une clé API valide
- Un compte Upstash Vector avec URL + token
- Une installation des dépendances de requirements.txt

## Lancement du pojet
Ce projet est une application Streamlit basée sur l'architecture RAG pour interroger mon portfolio. Voici les étapes pour lancer le projet localement :

1. Cloner le dépôt
	- git clone https://github.com/cdelezin/Projet-LLM.git

2. Configurer les variables d'environnement
Créez un fichier .env à la racine du projet et ajoutez les clés :
	  - OPENAI_API_KEY=votre_cle_ici
	  - UPSTASH_VECTOR_REST_URL=votre_url
	  - UPSTASH_VECTOR_REST_TOKEN=votre_token

3. Indexer les données dans Upstach (a ne faire qu'une seule fois)
	- python indexation.py

4. Lancer l'application
	- streamlit run application.py (http://localhost:8501/)


## Programmes / maintenance : 
Le projet suit cet ordre :

1. FICHIER chunk.py : Découpage des fichiers Markdown 

Explication de la fonction : def get_chunks() 

Cette fonction parcourt le dossier "data" à la recherche de fichiers Markdown (.md). 
Elle découpe ensuite le contenu de chaque fichier à chaque titre (format ##). 
Pour chaque morceau obtenu "chunk", elle crée un objet "dictionnaire" qui regroupe le nom du fichier d'origine, sa position dans le document et son contenu. 
Enfin, elle renvoie une liste structurée contenant tous ces objets.

2. FICHIER indexation.py : Indexation dans Upstash Vector 

Explication de la fonction : def index_chunks(chunks:list) -> str:

Cette fonction récupère les "chunks" générés précédemment par le fichier chunk.py. 
Pour chaque objet, elle crée un identifiant unique et formate les données en associant le texte brut aux métadonnées. 
Elle effectue ensuite le transfert vers le serveur "Upstash Vector", ce qui permettra à une IA de consulter et de retrouver ces informations par la suite.

3. Agent RAG -> agentAI.py 

Explication de la fonction : def recherche_portfolio(query: str) -> str:

C’est l'outil de recherche de l'IA : le "RAG". 
Lorsqu'un utilisateur pose une question, cette fonction interroge la base vectorielle "Upstash" pour extraire les trois passages les plus pertinents de mon portfolio. 
Elle organise ces informations (texte, source et score de fiabilité) pour les transmettre à l'agent. 
Ce contexte est ensuite renvoyé à l’agent, qui s’en sert pour produire une réponse. 
Si aucun résultat n’est trouvé, la fonction retourne un message indiquant que l’information n’est pas disponible.


Explication de la fonction : def run_agent_sync(user_message: str) -> str:

Cette fonction sert de lien entre l'interface utilisateur  et l'agent IA. 
Elle reçoit le message de l'utilisateur, lance l'exécution de l'agent et attend qu'il termine sa recherche pour récupérer la réponse. 
La fonction centralise l'envoi de la question et la réception de la réponse, tout en prévoyant un message de secours si l'agent ne parvient pas à répondre.


4. Interface web Streamlit -> application.py 

Ce code crée l'interface web de dialogue Streamlit qui permet l'intéraction entre l'utilisateur et l'agent. 
Il gère l'affichage d'un historique de chat pour que la conversation reste fluide et utilise une barre de saisie pour récupérer les questions de l'utilisateur. 
Lorsqu'un message est envoyé, le script appelle la fonction de l'agent IA et affiche un indicateur de chargement pendant la recherche. 
Une fois la réponse générée, elle est affichée à l'écran et sauvegardée dans la mémoire de la session.

## Auteurs
- Camille Delezinier


