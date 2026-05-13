"""
Joshitha's chatbot
------------------
A simple multi-turn chatbot powered by Claude claude-sonnet-4-6 (falls back to GPT-4o).

Usage:
    python main.py

Commands during chat:
    reset   — clear conversation history and start fresh
    quit    — exit the chatbot
    exit    — exit the chatbot
    /help   — show available commands
"""

from chatbot import TerminalChatbot

HELP_TEXT = """
Commands:
  reset   — start a new conversation
  /help   — show this message
  quit    — exit
"""


def make_banner(provider: str, model: str) -> str:
    # Dynamically size the banner so provider/model text is always centered cleanly.
    label = f"Provider: {provider}  Model: {model}"
    width = max(40, len(label) + 4)
    border = "-" * width
    return (
        f"\n+{border}+\n"
        f"|{"Joshitha's chatbot":^{width}}|\n"
        f"|{label:^{width}}|\n"
        f"|{'Type /help for available commands':^{width}}|\n"
        f"+{border}+\n"
    )


def format_usage(usage, provider: str) -> str:
    # Normalize token usage output across providers for a consistent terminal footer.
    if provider == "anthropic":
        cached = getattr(usage, "cache_read_input_tokens", 0) or 0
        created = getattr(usage, "cache_creation_input_tokens", 0) or 0
        parts = [f"in:{usage.input_tokens}", f"out:{usage.output_tokens}"]
        if cached:
            parts.append(f"cache_read:{cached}")
        if created:
            parts.append(f"cache_write:{created}")
    else:
        parts = [f"in:{usage.prompt_tokens}", f"out:{usage.completion_tokens}"]
    return "  ".join(parts)


def main() -> None:
    try:
        bot = TerminalChatbot()
    except EnvironmentError as exc:
        print(f"\n[Error] {exc}")
        print("Set ANTHROPIC_API_KEY or OPENAI_API_KEY and try again.\n")
        return

    print(make_banner(bot.provider, bot.model))

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue

        command = user_input.lower()

        if command in ("quit", "exit"):
            print("Goodbye!")
            break

        if command == "reset":
            bot.reset()
            print("── Conversation reset ──\n")
            continue

        if command == "/help":
            print(HELP_TEXT)
            continue

        try:
            # send() handles provider-specific API calls and updates conversation history.
            reply, usage = bot.send(user_input)
            print(f"\nJoshitha's chatbot: {reply}")
            print(f"\n[turn {bot.turn_count} | {format_usage(usage, bot.provider)}]\n")
        except Exception as exc:
            print(f"\n[Error] {exc}\n")


if __name__ == "__main__":
    main()
