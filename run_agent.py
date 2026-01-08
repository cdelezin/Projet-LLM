import argparse
import os
import sys
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
            context_parts.append(f"Source: {source} | {section}\n{text}")
        
        return "\n\n---\n\n".join(context_parts)
    except Exception as e:
        return f"[Erreur: {e}]"


def build_agent() -> Agent:
    """Create the portfolio assistant agent."""
    return Agent(
        name="portfolio-assistant",
        instructions=(
            "Tu es un assistant qui répond aux questions sur le profil professionnel de Camille Delezinier. "
            "Réponds de manière claire, concise et en français en te basant sur le contexte fourni."
        ),
        model="gpt-4.1-nano",
        model_settings=ModelSettings(temperature=0.3),
    )


def chat_once(prompt: str) -> str:
    agent = build_agent()
    # Enrichir avec le contexte RAG
    context = search_portfolio(prompt)
    augmented_prompt = f"""Contexte du portfolio:
{context}

Question: {prompt}

Réponds en te basant sur le contexte ci-dessus."""
    
    result = Runner.run_sync(agent, augmented_prompt)
    return result.final_output


def interactive_chat():
    print("Assistant prêt. Tapez 'exit' pour quitter.\n")
    agent = build_agent()
    while True:
        try:
            user = input("Vous: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            break
        if user.lower() in {"exit", "quit", ":q"}:
            print("Bye!")
            break
        if not user:
            continue
        
        # Enrichir avec le contexte RAG
        context = search_portfolio(user)
        augmented = f"""Contexte:
{context}

Question: {user}

Réponds en français de manière concise."""
        
        result = Runner.run_sync(agent, augmented)
        print("Assistant:", result.final_output.strip(), "\n")


def main():
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  OPENAI_API_KEY non défini dans .env — l'agent ne pourra pas répondre.")
    parser = argparse.ArgumentParser(description="Lancer l'agent IA du portfolio")
    parser.add_argument("--prompt", help="Question à poser une seule fois")
    args = parser.parse_args()

    if args.prompt:
        print(chat_once(args.prompt).strip())
    else:
        interactive_chat()


if __name__ == "__main__":
    main()
