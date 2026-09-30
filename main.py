"""Entry point: terminal chat with the product recommender agent."""
from backend.functions import profile, reset_profile
from backend.orchestrator import chat


def main():
    history = []
    print("Bot: Hi! What are you looking for today? (type 'quit' to exit, 'reset' to clear your saved preferences)")
    print("Bot: I have Jewellery and Home Decor items available.")
    if any(profile.values()):
        print("Bot: I remember your previous preferences:", profile)

    while True:
        user = input("You: ")
        if user.lower() == "quit":
            break
        if user.lower() == "reset":
            reset_profile()
            print("Bot: All preferences have been cleared!")
            continue

        reply = chat(user, history)
        print("Bot:", reply)
        print("[Profile]", profile)


if __name__ == "__main__":
    main()