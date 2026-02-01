from agents import Agent, Runner, function_tool
from upstash_vector import Index
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Initialiser l'index Upstash Vector
index = Index.from_env()

# Définirtion de la fonction Tool
@function_tool
def recherche_portfolio(query: str) -> str:
    """
    Recherche des informations dans le portfolio de l'étudiant.
    Args: query: La question ou requête de l'utilisateur sur le portfolio
    """

    # Interroger la base vectorielle avec la requête
    results = index.query(
        data=query,
        top_k=3,  
        include_metadata=True
    )
    
    # Réponse si aucun résultat n'est trouvé
    if not results or len(results) == 0:
        return "Aucune information trouvée dans le portfolio pour cette question."
    
    # Formater les résultats
    context = []
    for i, result in enumerate(results, 1):
        metadata = result.metadata
        score = result.score
        text = metadata.get('text', '')
        source = metadata.get('source_file', 'inconnu')
        
        context.append(f"[Source {i}: {source}, Pertinence: {score:.2f}]\n{text}\n")
    
    return "\n".join(context)


# 2. Création de l'agent avec la tool
mon_agent = Agent(
    name="Assistant Portfolio",
    model="gpt-4-nano",  
    instructions="""Tu es un assistant personnel qui aide à présenter le portfolio de Camille Delezinier.
    
    Utilise la fonction 'recherche_portfolio' pour répondre aux questions sur :
    - Mon profil
    - Mes compétences
    - Mon parcours académique et professionnel
    - Mes projets
    - Mon bilan de compétences
    
    Réponds de manière concise et professionnelle en t'appuyant sur les informations trouvées.
    Si l'information n'est pas dans le portfolio, dis-le clairement.""",
    tools=[recherche_portfolio], 
)


# 3. Fonction pour utiliser l'agent de manière synchrone (pour Streamlit)
def run_agent_sync(user_message: str) -> str:
    """
    Exécute l'agent de manière synchrone et retourne la réponse.
    Args: user_message: Le message de l'utilisateur   
    Returns: La réponse de l'agent sous forme de texte
    """
    # Exécuter l'agent avec le message utilisateur
    result = Runner.run_sync(mon_agent, user_message)
    
    # Retourner la réponse finale
    return result.final_output if result and result.final_output else "Désolé, je n'ai pas pu générer une réponse."


# 4. Lancement de la boucle d'interaction en mode console
if __name__ == "__main__":
    print("--- Assistant Portfolio Initialisé (tapez 'exit' pour quitter) ---")
    print("Posez vos questions sur le portfolio de l'étudiant!\n")
    Runner.run(mon_agent)
