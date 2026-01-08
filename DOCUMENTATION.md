# Documentation du Projet LLM - Portfolio avec IA

## Vue d'ensemble du projet

Ce projet implémente un portfolio intelligent utilisant un agent IA capable de répondre aux questions sur votre profil professionnel en utilisant la technique RAG (Retrieval-Augmented Generation).

### Architecture

```
Portfolio Markdown → Chunking → Upstash Vector (base vectorielle) → Agent OpenAI → Streamlit (interface)
```

## Structure du projet

```
projet-iut-potfolio/
├── data/                      # Fichiers Markdown du portfolio
│   ├── profil.md
│   ├── competences.md
│   ├── parcours.md
│   ├── projets.md
│   ├── bilan.md
├── tests/                     # Tests unitaires
│   ├── test_openai_agent.py
│   └── test_upstash_vector.py
├── chunk_markdown.py          # Script de découpage des documents
├── requirements.txt           # Dépendances Python
├── .env                       # Variables d'environnement (à créer)
└── .env.example              # Template des variables
```

## Installation et configuration

### 1. Prérequis
- Python 3.12 ou 3.13
- Git
- Compte Upstash (gratuit)
- Clé API OpenAI (fournie)

### 2. Configuration de l'environnement

```bash
# Créer un environnement virtuel
python -m venv .venv

# Activer l'environnement
.\.venv\Scripts\activate  # Windows PowerShell

# Installer les dépendances
pip install -r requirements.txt
```

### 3. Configuration des variables d'environnement

Créer un fichier `.env` à la racine du projet :

```env
OPENAI_API_KEY=votre_cle_openai
UPSTASH_VECTOR_REST_URL=https://votre-index.upstash.io
UPSTASH_VECTOR_REST_TOKEN=votre_token_upstash
```

### 4. Configuration Upstash Vector

1. Créer un compte sur [Upstash](https://console.upstash.com)
2. Créer un Vector Index avec :
   - **Région** : Ireland (eu-west-1)
   - **Type** : Hybrid
   - **Dense Embedding Model** : BAAI/bge-m3
   - **Metric** : COSINE
   - **Sparse Embedding Model** : BM25
3. Copier l'URL et le token dans `.env`

## Étapes réalisées

### ✅ 1. Préparation des données

Fichiers Markdown créés dans `data/` :
- **profil.md** : Identité, statut, présentation, centres d'intérêt
- **competences.md** : Compétences techniques, langues, soft skills
- **parcours.md** : Formation, certifications, expériences professionnelles
- **projets.md** : Projets académiques détaillés
- **bilan.md** : Bilan personnel et professionnel

Structure utilisée : titres hiérarchiques (`#`, `##`, `###`) pour faciliter le chunking.

### ✅ 2. Découpage des documents (Chunking)

**Script** : `chunk_markdown.py`

Le script découpe intelligemment les fichiers Markdown en chunks cohérents pour l'indexation vectorielle.

#### Fonctionnalités du chunker

- **Analyse de structure** : Détecte la hiérarchie des titres
- **Découpage intelligent** : Par paragraphes, puis par phrases si nécessaire
- **Overlap configurable** : Chevauchement entre chunks pour préserver le contexte
- **Métadonnées enrichies** : source, section_path, chunk_index, longueur

#### Utilisation (intégrée au flux d'indexation)

Le découpage se fait désormais à la volée directement depuis les fichiers Markdown lors de l'indexation (pas de fichier JSON intermédiaire requis).

Vous pouvez tout de même utiliser `chunk_markdown.py` seul pour tester le découpage, mais ce n'est pas nécessaire pour l'indexation.

### ✅ 3. Tests unitaires

Deux tests créés dans `tests/` :

#### Test OpenAI Agent (`test_openai_agent.py`)
Vérifie la connexion et le fonctionnement de l'agent OpenAI avec un test ping-pong simple.

```bash
pytest tests/test_openai_agent.py -s
```

#### Test Upstash Vector (`test_upstash_vector.py`)
Vérifie la connexion à Upstash et teste l'insertion/suppression de vecteurs.

```bash
pytest tests/test_upstash_vector.py -s
```

**Lancer tous les tests** :
```bash
pytest -s
```

## Prochaines étapes

### ✅ 3. Indexation dans Upstash

**Script** : `index_to_upstash.py`

Le script lit directement les fichiers Markdown du dossier `data/`, les découpe en mémoire, puis les indexe dans Upstash Vector.

#### Utilisation

```bash
python index_to_upstash.py --input data --max_chars 700 --overlap 100 --batch_size 100 --query "compétences en Python"
```

Le script effectue automatiquement :
1. Lecture des `.md` depuis `--input`
2. Découpage à la volée (`--max_chars`, `--overlap`)
3. Connexion à Upstash Vector via `.env`
4. Indexation par batch (`--batch_size`)
5. Test de recherche (`--query`)

#### Utilisation programmatique

```python
from upstash_vector import Index
import os

index = Index(
    url=os.getenv("UPSTASH_VECTOR_REST_URL"),
    token=os.getenv("UPSTASH_VECTOR_REST_TOKEN")
)

results = index.query(
    data="compétences en Python",
    top_k=3,
    include_metadata=True,
    include_data=True
)
for r in results:
    print(r.score, r.metadata.get("source"), r.data[:120])
```

## Prochaines étapes

### 🔲 4. Création de l'Agent IA

Créer un agent avec `openai-agents` :

```python
from agents import Agent, Runner, ModelSettings

agent = Agent(
    name="portfolio-assistant",
    instructions="Tu es un assistant qui répond aux questions sur le profil professionnel de Camille.",
    model="gpt-4.1-nano",
    model_settings=ModelSettings(temperature=0.7),
)

result = Runner.run_sync(agent, "Quelles sont mes compétences en Python ?")
print(result.final_output)
```

Documentation : [OpenAI Agents](https://openai.github.io/openai-agents-python/agents/)

### 🔲 5. Connexion Agent ↔ Vecteurs (RAG)

Ajouter une Tool pour interroger Upstash :

```python
def search_portfolio(query: str) -> str:
    """Recherche dans le portfolio."""
    results = index.query(
        data=query,
        top_k=3,
        include_metadata=True
    )
    # Formatter et retourner les résultats
    return "\n\n".join([r.metadata["text"] for r in results])

agent = Agent(
    name="portfolio-assistant",
    instructions="...",
    model="gpt-4.1-nano",
    functions=[search_portfolio]
)
```

Documentation : [OpenAI Agents Tools](https://openai.github.io/openai-agents-python/tools/)

### 🔲 6. Interface Streamlit

Créer une interface de chat :

```python
import streamlit as st

st.title("Mon Portfolio IA")

# Chat interface
if prompt := st.chat_input("Posez-moi une question"):
    st.chat_message("user").write(prompt)
    
    # Appeler l'agent
    result = Runner.run_sync(agent, prompt)
    
    st.chat_message("assistant").write(result.final_output)
```

Documentation : [Streamlit Chat Apps](https://docs.streamlit.io/develop/tutorials/chat-and-llm-apps/build-conversational-apps)

### 🔲 7. Déploiement Streamlit Cloud

1. Pousser le code sur GitHub
2. Connecter le dépôt sur [Streamlit Cloud](https://streamlit.io/cloud)
3. Configurer les secrets (variables d'environnement)
4. Déployer

Documentation : [Deploy Streamlit App](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy)

## Bonuses possibles

### Sauvegarde des conversations (Upstash Redis)
- Mémoriser l'historique des échanges
- Permettre des conversations multi-tours
- Documentation : [Upstash Redis](https://upstash.com/docs/redis/overall/getstarted)

### Tools supplémentaires
- Génération de CV au format PDF
- Envoi d'email de contact
- Recherche de projets similaires

## Commandes utiles

```bash
# Activer l'environnement virtuel
.\.venv\Scripts\activate

# Installer/mettre à jour les dépendances
pip install -r requirements.txt

# Générer les chunks
python chunk_markdown.py

# Lancer les tests
pytest -s

# Lancer l'application Streamlit (quand créée)
streamlit run app.py

# Git
git add .
git commit -m "message"
git push
```

## Dépendances (`requirements.txt`)

```
streamlit==1.52.2           # Interface utilisateur
openai-agents[redis]==0.6.5 # Agent IA OpenAI
upstash-vector==0.8.0       # Base de données vectorielle
pytest==9.0.2                # Tests unitaires
python-dotenv==1.2.1         # Gestion variables d'environnement
```

## Notes importantes

- **Modèle limité** : Seul `gpt-4.1-nano` est accessible avec la clé fournie
- **Pas de HTML** : Utiliser uniquement les composants natifs Streamlit
- **Clé temporaire** : La clé API sera désactivée après correction
- **Sécurité** : Ne jamais committer le fichier `.env` (déjà dans `.gitignore`)

## Troubleshooting

### Erreur de connexion OpenAI
- Vérifier `OPENAI_API_KEY` dans `.env`
- Vérifier que le modèle est bien `gpt-4.1-nano`

### Erreur Upstash
- Vérifier `UPSTASH_VECTOR_REST_URL` et `UPSTASH_VECTOR_REST_TOKEN`
- Vérifier la configuration de l'index (Hybrid, BAAI/bge-m3)

### Tests échouent
- Vérifier que `.env` est configuré
- Lancer avec `pytest -s` pour voir les outputs
- Vérifier la connexion internet

### Chunks incorrects
- Vérifier la structure des fichiers Markdown (titres, paragraphes)
- Ajuster `--max_chars` et `--overlap`
- Vérifier l'encoding UTF-8 des fichiers

## Support

- [Documentation OpenAI Agents](https://openai.github.io/openai-agents-python/)
- [Documentation Upstash Vector](https://upstash.com/docs/vector)
- [Documentation Streamlit](https://docs.streamlit.io/)
