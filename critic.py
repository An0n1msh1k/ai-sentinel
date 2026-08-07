import json
from pathlib import Path

import litellm

from config import CRITIC_MODEL
from models import Critique


def audit(question: str, draft: str, strategy_prompt: str) -> Critique:
    strategy_path = Path(__file__).parent / 'strategies' / f"{strategy_prompt}.md"
    if strategy_path.exists():
        strategy_prompt = strategy_path.read_text(encoding="utf-8", errors="replace")
    else:
        strategy_prompt = ""
    system_prompt = f"""
You are a strict red-team auditor.

Your job is to find factual errors, unsafe assumptions,
missing information, logical mistakes, and unsupported claims.

{strategy_prompt}

Return ONLY valid JSON with exactly these fields:
{{
    "score": 0,
    "fatal_flaws": [],
    "missing_info": [],
    "corrections": ""
}}

Rules:
- score must be an integer from 0 to 100.
- fatal_flaws must contain serious errors.
- missing_info: Use ONLY when input data from the USER is missing (e.g., OS not specified, disk UUID, file path, etc.), making it impossible to give a safe answer. Never write the Actor's errors in 'missing_info'.
- corrections: Must explain exactly what the Actor should fix. If the Actor made a technical error in the draft, forgot to specify a flag, security setting, or explanation — ALWAYS write this in 'corrections' or 'fatal_flaws' so the Actor can fix it on the 2nd attempt.
- All list fields MUST be JSON arrays [], never empty strings.
- Do not invent missing information.
- If the draft is correct and sufficiently supported, use score 100.
"""
    response = litellm.completion(
        model=CRITIC_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": (
                    f"QUESTION:\n{question}\n\n"
                    f"DRAFT ANSWER:\n{draft}"
                ),
            },
        ],
        temperature=0,
    )

    raw = response.choices[0].message.content.strip()

    start = raw.find("{")
    end = raw.rfind("}")

    if start == -1 or end == -1:
        return Critique(
            score=0,
            fatal_flaws=["Critic did not return valid JSON"],
            missing_info=[],
            corrections="Return the critique as valid JSON.",
        )

    try:
        data = json.loads(raw[start:end + 1])
        return Critique.model_validate(data)
    except json.JSONDecodeError as exc:
        return Critique(
            score=0,
            fatal_flaws=[f"Critic JSON parsing failed: {exc}"],
            missing_info=[],
            corrections="Return a valid JSON critique.",
        )
