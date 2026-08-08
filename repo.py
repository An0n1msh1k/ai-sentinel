import subprocess
from functools import lru_cache
from pathlib import Path


def get_repo_map(
    root_dir: Path | None = None,
    max_files: int = 80
) -> str:
    """Повертає чисту структуру Git-репозиторію."""
    if root_dir is None:
        root_dir = Path.cwd()

    try:
        result = subprocess.run(
            [
                "git",
                "-C",
                str(root_dir),
                "ls-files",
                "-c",
                "-o",
                "--exclude-standard",
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        files = [
            f.strip()
            for f in result.stdout.strip().splitlines()
            if f.strip()
        ]
    except (subprocess.CalledProcessError, FileNotFoundError):
        files = []
        for p in root_dir.rglob("*"):
            if p.is_file():
                rel_parts = p.relative_to(root_dir).parts
                if not any(
                    part.startswith(".")
                    or part in ("__pycache__", "logs", "node_modules")
                    for part in rel_parts
                ):
                    files.append(
                        str(p.relative_to(root_dir))
                    )
        files.sort()

    if not files:
        return ""

    header = f"=== СТРУКТУРА ПРОЄКТУ (REPO-MAP: {root_dir.name}) ==="
    if len(files) > max_files:
        shown = "\n".join(
            f"  - {f}" for f in files[:max_files]
        )
        footer = (
            f"\n  ... (та ще {len(files) - max_files} файлів)"
        )
        return f"{header}\n{shown}{footer}\n"

    shown = "\n".join(f"  - {f}" for f in files)
    return f"{header}\n{shown}\n"


@lru_cache(maxsize=32)
def get_repo_diff(
    root_dir: Path | None = None,
    max_lines: int = 500
) -> str:
    """Повертає git diff для контексту перевірки коду."""
    if root_dir is None:
        root_dir = Path.cwd()

    try:
        result = subprocess.run(
            ["git", "-C", str(root_dir), "diff", "--cached"],
            capture_output=True,
            text=True,
            check=True,
        )
        diff_text = result.stdout.strip()

        if not diff_text:
            result = subprocess.run(
                ["git", "-C", str(root_dir), "diff"],
                capture_output=True,
                text=True,
                check=True,
            )
            diff_text = result.stdout.strip()

        if not diff_text:
            return "Активних змін (git diff) не знайдено."

        header = f"=== GIT DIFF ({root_dir.name}) ==="
        lines = diff_text.splitlines()

        if len(lines) > max_lines:
            shown = "\n".join(lines[:max_lines])
            return f"{header}\n{shown}\n... (обрізано)"

        return f"{header}\n{diff_text}"
    except (subprocess.SubprocessError, FileNotFoundError):
        return "Помилка отримання git diff."
