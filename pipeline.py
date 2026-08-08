import datetime
import json
import sys
from pathlib import Path

from actor import generate
from critic import audit
from models import Critique

MAX_RETRIES = 2
MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024

FORBIDDEN_NAMES = {
    ".env",
    "id_rsa",
    "id_dsa",
    "id_ed25519",
}

FORBIDDEN_EXTENSIONS = {
    ".pem",
    ".key",
    ".pfx",
    ".cer",
}


def run_pipeline(
    prompt: str,
    strategy: str = "general"
) -> str:
    """Executes the Actor-Critic verification pipeline."""
    print(
        f"🤖 [Actor] Generating draft (strategy: {strategy})..."
    )
    current_draft = generate(prompt, strategy_prompt=strategy)

    for attempt in range(1, MAX_RETRIES + 2):
        print(f"🔍 [Critic] Auditing attempt {attempt}...")
        critique: Critique = audit(
            prompt, current_draft, strategy
        )

        if critique.missing_info:
            print(
                "\n⚠️ [MISSING INFO] Critic requires data:"
            )
            for item in critique.missing_info:
                print(f"   - {item}")

            if not sys.stdin.isatty():
                print("⏩ Non-interactive mode: skipping...")
                user_input = ""
            else:
                try:
                    user_input = input(
                        "\n👉 Enter clarification: "
                    ).strip()
                except (KeyboardInterrupt, EOFError):
                    user_input = ""

            if not user_input:
                print("⏩ Ignoring information request...")
            else:
                if not (
                    user_input.startswith("@")
                    or Path(user_input).is_file()
                ):
                    prompt += (
                        f"\n\n[USER CLARIFICATION]: "
                        f"{user_input}"
                    )
                else:
                    file_path = Path(
                        user_input.lstrip("@")
                    )
                    if not file_path.is_file():
                        print(
                            f"⚠️ File {file_path} not found."
                        )
                        prompt += (
                            f"\n\n[CLARIFICATION]: {user_input}"
                        )
                    elif (
                        file_path.name.lower()
                        in FORBIDDEN_NAMES
                        or file_path.suffix.lower()
                        in FORBIDDEN_EXTENSIONS
                    ):
                        print(
                            f"\n🚨 [SECURITY] Blocked "
                            f"sensitive file: {file_path.name}"
                        )
                        continue
                    elif (
                        file_path.stat().st_size
                        > MAX_FILE_SIZE_BYTES
                    ):
                        print(
                            f"\n🚨 [SECURITY] File too large: "
                            f"{file_path.name}"
                        )
                        continue
                    else:
                        content = file_path.read_text(
                            encoding="utf-8",
                            errors="replace",
                        )
                        prompt += (
                            f"\n\n[USER FILE: "
                            f"{file_path.name}]:\n{content}"
                        )

                current_draft = generate(
                    prompt, strategy_prompt=strategy
                )
                continue

        if (
            critique.score >= 95
            and not critique.fatal_flaws
        ):
            print(
                f"✅ [Success] Verification passed! "
                f"(Score: {critique.score}/100)"
            )
            log_iteration(
                prompt,
                current_draft,
                critique,
                success=True,
            )
            return current_draft

        print(
            f"⚠️  [Attempt {attempt}] Score "
            f"{critique.score}/100. Issues found:"
        )
        for flaw in critique.fatal_flaws:
            print(f"   ✖ {flaw}")

        if attempt <= MAX_RETRIES:
            print("↻  [Actor] Fixing issues...")
            correction_instructions = "\n".join(
                critique.corrections
            )
            current_draft = generate(
                f"TASK: {prompt}\n\n"
                f"PREVIOUS DRAFT:\n{current_draft}\n\n"
                f"CRITIC INSTRUCTIONS:\n"
                f"{correction_instructions}",
                strategy_prompt=strategy,
            )
        else:
            print(
                f"⚠️ [BEST EFFORT] Best draft "
                f"(Score: {critique.score}/100):"
            )
            print(current_draft)
            log_iteration(
                prompt,
                current_draft,
                critique,
                success=False,
            )
            sys.exit(1)


def log_iteration(
    prompt: str,
    draft: str,
    critique: Critique,
    success: bool,
):
    """Saves execution results to a log file."""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    timestamp = datetime.datetime.now(
        datetime.timezone.utc
    ).strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"run_{timestamp}.json"

    log_data = {
        "timestamp": timestamp,
        "prompt": prompt,
        "success": success,
        "final_score": critique.score,
        "fatal_flaws": critique.fatal_flaws,
        "missing_info": critique.missing_info,
        "corrections": critique.corrections,
        "draft": draft,
    }
    log_file.write_text(
        json.dumps(log_data, indent=2, ensure_ascii=False)
    )


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(
            "Usage: python pipeline.py "
            "'<prompt>' [strategy]"
        )
        sys.exit(1)

    user_prompt = sys.argv[1]
    strat = (
        sys.argv[2] if len(sys.argv) > 2 else "general"
    )

    final_output = run_pipeline(user_prompt, strat)
    print("\n--- FINAL RESULT ---")
    print(final_output)
