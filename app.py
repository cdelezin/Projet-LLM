import os
import streamlit as st
from dotenv import load_dotenv
from agents import Agent, Runner, ModelSettings
from upstash_vector import Index

load_dotenv(override=True)


def search_portfolio(query: str) -> str:
    """Recherche dans Upstash Vector et retourne le contexte."""
    try:
        index = Index(
            url=os.getenv("UPSTASH_VECTOR_REST_URL"),
            token=os.getenv("UPSTASH_VECTOR_REST_TOKEN")
        )
        
        results = index.query(
            data=query,
            top_k=3,
            include_metadata=True,
            include_data=True
        )
        
        if not results:
            return "[Aucune information trouvée]"
        
        context_parts = []
        for r in results:
            source = r.metadata.get("source", "?")
            section = r.metadata.get("section_path", "")
            text = r.data if r.data else "[vide]"
            context_parts.append(f"**Source:** {source} | {section}\n\n{text}")
        
        return "\n\n---\n\n".join(context_parts)
    except Exception as e:
        return f"[Erreur: {e}]"


def build_agent() -> Agent:
    """Create the portfolio assistant agent."""
    return Agent(
        name="portfolio-assistant",
        instructions=(
            "Tu es un assistant qui répond aux questions sur le profil professionnel de Camille Delezinier. "
            "Réponds de manière claire, concise et en français en te basant sur le contexte fourni. "
            "Si le contexte ne contient pas l'information, dis-le poliment."
        ),
        model="gpt-4.1-nano",
        model_settings=ModelSettings(temperature=0.3),
    )


def get_response(user_message: str) -> str:
    """Get agent response with RAG context."""
    agent = build_agent()
    
    # Enrichir avec le contexte RAG
    context = search_portfolio(user_message)
    augmented_prompt = f"""Contexte du portfolio:
{context}

Question: {user_message}

Réponds en te basant sur le contexte ci-dessus."""
    
    result = Runner.run_sync(agent, augmented_prompt)
    return result.final_output


# Configuration de la page
st.set_page_config(
    page_title="Portfolio IA - Camille Delezinier",
    page_icon="💼",
    layout="centered"
)

st.title("💼 Portfolio IA - Camille Delezinier")
st.caption("Posez vos questions sur mon profil professionnel")

# Initialiser l'historique des messages
if "messages" not in st.session_state:
    st.session_state.messages = []

# Afficher l'historique des messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input utilisateur
if prompt := st.chat_input("Posez votre question..."):
    # Ajouter le message utilisateur à l'historique
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Afficher le message utilisateur
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Obtenir et afficher la réponse de l'assistant
    with st.chat_message("assistant"):
        with st.spinner("Recherche en cours..."):
            response = get_response(prompt)
        st.markdown(response)
    
    # Ajouter la réponse à l'historique
    st.session_state.messages.append({"role": "assistant", "content": response})

# Sidebar avec informations
with st.sidebar:
    st.header("À propos")
    st.markdown("""
    Cet assistant utilise l'IA pour répondre aux questions sur le profil professionnel de **Camille Delezinier**.
    
    **Exemples de questions :**
    - Quel est mon parcours académique ?
    - Quelles sont mes compétences en Python ?
    - Parle-moi de mon expérience chez Enedis
    - Quels projets ai-je réalisés ?
    """)
    
    if st.button("🗑️ Effacer l'historique"):
        st.session_state.messages = []
        st.rerun()
