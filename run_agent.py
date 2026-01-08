import argparse
import os
import sys
from dotenv import load_dotenv
from agents import Agent, Runner, ModelSettings

load_dotenv(override=True)


def build_agent() -> Agent:
    """Create the portfolio assistant agent (step 4)."""
    return Agent(
        name="portfolio-assistant",
        instructions=(
            "Tu es un assistant utile et concis qui répond aux questions sur le profil professionnel de Camille. "
            "Réponds clairement en français. Si l'information précise n'est pas disponible, indique-le et propose "
            "de poser une question plus ciblée."
        ),
        model="gpt-4.1-nano",
        model_settings=ModelSettings(temperature=0.4),
    )


def chat_once(prompt: str) -> str:
    agent = build_agent()
    result = Runner.run_sync(agent, prompt)
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
        result = Runner.run_sync(agent, user)
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
