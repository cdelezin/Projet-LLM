# PROJET LLM

Pour la réalisation de ce projet, vous pouvez utiliser l’IDE de votre choix (le plus connu : [Visual Studio Code](https://code.visualstudio.com/)). Je vous conseille aussi d’installer l’une de ces versions de Python : 3.12 ou 3.13 ([Download Python | Python.org](https://www.python.org/downloads/)).

## Création de la base de données vectorielle

Pour réaliser le projet, vous allez avoir besoin d’un index pour stocker vos informations :
* Créer un compte [Signup - Upstash](https://console.upstash.com/signup)
* Aller dans l’outil « **Vector** »
* Créer un « **Vector Index** »
* Configurer l’index : 
    * **Nom** : Ce que vous voulez
    * **Région** : Ireland (eu-west-1)
    * **Type** : Hybrid
    * **Dense Embedding Model** : BAAI/bge-m3
    * **Metric** : COSINE
    * **Sparse Embedding Model** : BM25
  
![Configuration Upstash](assets/configuration_index_upstash.png)
* **Plan** : Free

## OpenAI

Je vous transmettrais la clé API via UPdago

## Tests

Avant de commencer le projet, nous allons vérifier que tout fonctionne bien (pas de blocage proxy…), pour cela :
* Créer un `.venv` et installer les packages du fichier requirements via la commande : `pip install -r requirements.txt`
* Créer un fichier `.env` et copier les variables du fichier `.env.example` dans le fichier `.env` puis compléter les valeurs des variables
* Ouvrir un terminal et lancer les tests via la commande : `pytest -s`


## À vous de jouer !

### 1. Préparation des données
Pour commencer, vous devez créer plusieurs fichiers Markdown (`.md`) dans le dossier `data`. Chaque fichier doit correspondre à une section de votre profil (Expériences, Projets, Compétences, etc.).
* **Conseil** : Reprenez les informations de votre portfolio existant.
* **Structure** : Utilisez des titres clairs (`#`, `##`) pour faciliter le futur découpage (chunking) des documents.

### 2. Découpage des documents (Chunking)
Afin que l'IA puisse retrouver précisément l'information, vous devez diviser vos fichiers Markdown en petits morceaux cohérents.

### 3. Indexation dans Upstash
Une fois vos documents découpés, vous devez les envoyer dans votre index Upstash Vector.
* [Documentation : SDK Python Upstash Vector](https://upstash.com/docs/vector/sdks/py/gettingstarted)

### 4. Création de l'Agent IA
Développez votre agent en utilisant la bibliothèque `openai-agents`.
* [Documentation : Introduction aux Agents](https://openai.github.io/openai-agents-python/agents/)
* [Documentation : Comment lancer un Agent](https://openai.github.io/openai-agents-python/running_agents/)

### 5. Connexion Agent ↔ Vecteurs (RAG)
Ajoutez une **Tool** (fonction) à votre agent pour lui permettre d'interroger votre base de données vectorielle lorsqu'une question est posée sur votre profil.
* [Documentation : Utilisation des Tools](https://openai.github.io/openai-agents-python/tools/)

### 6. Interface Utilisateur (Streamlit)
Créez une interface de chat pour permettre aux utilisateurs d'interagir avec votre agent.
* [Tutoriel : Créer une application de chat avec Streamlit](https://docs.streamlit.io/develop/tutorials/chat-and-llm-apps/build-conversational-apps)
