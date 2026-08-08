import litellm

from config import ACTOR_MODEL


def generate(
    question: str,
    strategy_prompt: str = ""
) -> str:
    """Генерує чернетку відповіді за допомогою актора."""
    messages = [
        {
            "role": "system",
            "content": (
                strategy_prompt
                or "You are a precise technical assistant. Never guess when information is missing."
            ),
        },
        {
            "role": "user",
            "content": question,
        },
    ]

    response = litellm.completion(
        model=ACTOR_MODEL,
        messages=messages,
        temperature=0.2,
    )

    return response.choices[0].message.content
