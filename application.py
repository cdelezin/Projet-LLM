import streamlit as st
from agentIA import run_agent_sync

st.title("Assistant Portfolio de Camille")

# Initialiser l'historique
if "messages" not in st.session_state:
    st.session_state.messages = []

# Afficher l'historique
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Traiter les nouveaux messages
if prompt := st.chat_input("Posez votre question sur mon portfolio..."):
    # Afficher le message utilisateur
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Générer et afficher la réponse
    with st.chat_message("assistant"):
        with st.spinner("Recherche dans le portfolio..."):
            response = run_agent_sync(prompt)
            st.markdown(response)
    
    # Sauvegarder la réponse
    st.session_state.messages.append({"role": "assistant", "content": response})