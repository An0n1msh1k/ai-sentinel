import argparse
from pathlib import Path

from pipeline import run_pipeline
from repo import get_repo_diff, get_repo_map


def parse_args():
    """Parses command-line arguments."""
    parser = argparse.ArgumentParser(
        description="AI Sentinel — Verifier (Actor-Critic)"
    )
    parser.add_argument(
        "prompt",
        help="Task description or verification question"
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="Project files for analysis"
    )
    parser.add_argument(
        "-m", "--map",
        action="store_true",
        help="Include Git repository structure"
    )
    parser.add_argument(
        "-d", "--diff",
        action="store_true",
        help="Include git diff in context"
    )
    strategy_dir = Path(__file__).parent / 'strategies'
    strategies = [
        f.stem for f in strategy_dir.glob('*.md')
    ] + ['general']
    parser.add_argument(
        "-s", "--strategy",
        default="general",
        choices=strategies,
        help="Specialized verification strategy"
    )
    return parser.parse_args()


def build_context(
    prompt: str,
    file_paths: list[str],
    include_map: bool = False,
    include_diff: bool = False
) -> str:
    """Builds the overall context for execution."""
    context_parts = []
    if include_map:
        context_parts.append(get_repo_map())
    if include_diff:
        context_parts.append(get_repo_diff())

    if not file_paths:
        context_parts.append(prompt)
    else:
        context_parts.append(
            f"TASK: {prompt}\n\nPROJECT FILE CONTEXT:"
        )
        for fp in file_paths:
            path = Path(fp)
            if path.exists() and path.is_file():
                content = path.read_text(
                    encoding="utf-8", errors="replace"
                )
                context_parts.append(
                    f"--- FILE: {path.name} ---\n{content}\n"
                )
            else:
                print(
                    f"⚠️ Warning: File {fp} not found."
                )

    if include_map or include_diff:
        return "\n\n".join(context_parts)
    return "\n".join(context_parts)


def main():
    """Application entry point."""
    args = parse_args()
    full_prompt = build_context(
        args.prompt,
        args.files,
        include_map=args.map,
        include_diff=args.diff
    )

    print(
        f"🚀 [AI Sentinel] Running (Strategy: {args.strategy})..."
    )
    result = run_pipeline(
        full_prompt, strategy=args.strategy
    )

    print("\n==========================================")
    print("             VERIFIED RESULT              ")
    print("==========================================")
    print(result)


if __name__ == "__main__":
    main()
