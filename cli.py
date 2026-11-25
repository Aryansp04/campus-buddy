import sys
import os

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent.campus_agent import CampusBuddyAgent

def main():
    print("=" * 65)
    print("   🎓 CAMPUS BUDDY - AGENTFORGE WORKSHOP EDITION")
    print("=" * 65)
    print("Welcome! I'm your college AI companion.")
    print("Ask me about class schedules, math/attendance, or campus info.")
    print("Type 'exit' or 'quit' to leave.\n")

    agent = CampusBuddyAgent()

    while True:
        try:
            query = input("Student > ").strip()
            if not query:
                continue
            if query.lower() in ("exit", "quit", "q"):
                print("\nCampus Buddy: Good luck with your classes! See you soon! 👋")
                break

            print("\n[Campus Buddy Agent Loop Thinking...]")
            result = agent.run(query)
            trace = result["trace"]

            if trace.tool_needed:
                print(f"  ↳ 🎯 Goal: {trace.goal}")
                print(f"  ↳ 🛠️ Tool: {trace.tool_name}")
                print(f"  ↳ 📥 Input: {trace.tool_input}")
                print(f"  ↳ 👁️ Observation: {str(trace.observation)[:120]}...")
            else:
                print("  ↳ 💬 Direct response (no tool needed)")

            print(f"\nCampus Buddy > {result['answer']}\n")
            print("-" * 65)

        except (KeyboardInterrupt, EOFError):
            print("\nCampus Buddy: Goodbye! 👋")
            break

if __name__ == "__main__":
    main()
