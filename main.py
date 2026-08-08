import argparse
from pathlib import Path

from pipeline import run_pipeline
from repo import get_repo_diff, get_repo_map


def parse_args():
    parser = argparse.ArgumentParser(
        description="AI Sentinel — Локальний інженерний верифікатор (Actor-Critic)"
    )
    parser.add_argument(
        "prompt",
        help="Опис задачі або питання для верифікації"
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="Файли проєкту для аналітика (необов'язково)"
    )
    parser.add_argument(
        "-m", "--map",
        action="store_true",
        help="Додати структуру Git-репозиторію (repo-map) у контекст запиту"
    )
    parser.add_argument(
        "-d", "--diff",
        action="store_true",
        help="Додати git diff у контекст для Code Review"
    )
    strategy_dir = Path(__file__).parent / 'strategies'
    strategies = [f.stem for f in strategy_dir.glob('*.md')] + ['general']
    parser.add_argument(
        "-s", "--strategy",
        default="general",
        choices=strategies,
        help="Спеціалізована стратегія перевірки (за замовчуванням: general)"
    )
    return parser.parse_args()

def build_context(
    prompt: str,
    file_paths: list[str],
    include_map: bool = False,
    include_diff: bool = False
) -> str:
    context_parts = []
    if include_map:
        context_parts.append(get_repo_map())
    if include_diff:
        context_parts.append(get_repo_diff())

    if not file_paths:
        context_parts.append(prompt)
    else:
        context_parts.append(f"ЗАВДАННЯ: {prompt}\n\nКОНТЕКСТ ФАЙЛІВ ПРОЄКТУ:")
        for fp in file_paths:
            path = Path(fp)
            if path.exists() and path.is_file():
                content = path.read_text(encoding="utf-8", errors="replace")
                context_parts.append(f"--- ФАЙЛ: {path.name} ---\n{content}\n")
            else:
                print(f"⚠️ Попередження: Файл {fp} не знайдено, пропускаємо.")

    return "\n\n".join(context_parts) if (include_map or include_diff) else "\n".join(context_parts)

def main():
    args = parse_args()
    full_prompt = build_context(
        args.prompt,
        args.files,
        include_map=args.map,
        include_diff=args.diff
    )

    print(f"🚀 [AI Sentinel] Запуск пайплайну (Стратегія: {args.strategy})...")
    result = run_pipeline(full_prompt, strategy=args.strategy)

    print("\n==========================================")
    print("           ВЕРИФІКОВАНИЙ РЕЗУЛЬТАТ        ")
    print("==========================================")
    print(result)

if __name__ == "__main__":
    main()
