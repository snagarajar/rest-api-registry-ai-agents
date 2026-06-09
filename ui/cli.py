"""Command-line chat interface for the API Registry Agent."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from orchestrator.agent import orchestrate


def main():
    print("╔══════════════════════════════════════╗")
    print("║    REST API Registry Agent — CLI     ║")
    print("╚══════════════════════════════════════╝")
    print('Type your question or "exit" to quit.\n')

    while True:
        try:
            question = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not question:
            continue
        if question.lower() in ("exit", "quit"):
            print("Goodbye!")
            break

        print("\nAgent is thinking...\n")
        try:
            answer = orchestrate(question)
        except Exception as exc:
            answer = f"[Error] {exc}"
        print(f"Agent: {answer}\n")


if __name__ == "__main__":
    main()
