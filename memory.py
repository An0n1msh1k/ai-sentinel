from datetime import datetime, timezone
from pathlib import Path

MEMORY_FILE = Path(".sentinel_memory.md")

STOP_WORDS = {
    "the", "and", "for", "that", "this", "with", "from", "your",
    "code", "file", "only", "more", "than", "when", "make", "like",
    "just", "what", "have", "does", "should", "need", "will", "into",
}


def save_to_memory(flaws: list[str], corrections: str) -> None:
    """Saves critical flaws to long-term memory for RAG context."""
    if not flaws and not corrections:
        return
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    memory_entry = f"\n### Failure at {timestamp}\n"
    if flaws:
        memory_entry += "**Flaws:**\n" + "\n".join(f"- {f}" for f in flaws) + "\n"
    if corrections:
        memory_entry += f"**Corrections Needed:**\n{corrections}\n"

    with open(MEMORY_FILE, "a", encoding="utf-8") as f:
        f.write(memory_entry)


def read_memory() -> str:
    """Reads and strips the long-term memory file if it exists, otherwise returns an empty string."""
    if not MEMORY_FILE.exists():
        return ""
    return MEMORY_FILE.read_text(encoding="utf-8").strip()


def extract_keywords(prompt: str) -> list[str]:
    """Extract keywords from a prompt, ignoring stop words."""
    words = prompt.split()
    keywords = [
        word for word in words
        if len(word) > 3 and word.lower() not in STOP_WORDS
    ]
    return keywords


def search_relevant_memory(keywords: list[str]) -> str:
    """Search for relevant memory entries based on keywords. Max 500 chars."""
    memory = read_memory()
    if not memory or not keywords:
        return ""
    relevant_lines = []
    for line in memory.splitlines():
        for keyword in keywords:
            if keyword.lower() in line.lower():
                relevant_lines.append(line)
                break
    return "\n".join(relevant_lines)[:500]


def build_prompt_with_memory(base_prompt: str) -> str:
    """Lightweight RAG: Inject past mistakes into the prompt if they exist."""
    keywords = extract_keywords(base_prompt)
    relevant_memory = search_relevant_memory(keywords)
    if relevant_memory:
        return f"{base_prompt}\n\n=== PAST MISTAKES TO AVOID ===\n{relevant_memory}"
    return base_prompt