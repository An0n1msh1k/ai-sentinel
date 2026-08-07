import subprocess
from pathlib import Path


def get_repo_map(root_dir: Path | None = None, max_files: int = 80) -> str:
    """Повертає чисту структуру Git-репозиторію (або звичайного каталогу)."""
    if root_dir is None:
        root_dir = Path.cwd()

    try:
        result = subprocess.run(
            ["git", "-C", str(root_dir), "ls-files", "-c", "-o", "--exclude-standard"],
            capture_output=True,
            text=True,
            check=True,
        )
        files = [f.strip() for f in result.stdout.strip().splitlines() if f.strip()]
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
                    files.append(str(p.relative_to(root_dir)))
        files.sort()

    if not files:
        return ""

    header = f"=== СТРУКТУРА ПРОЄКТУ (REPO-MAP: {root_dir.name}) ==="
    if len(files) > max_files:
        shown = "\n".join(f"  - {f}" for f in files[:max_files])
        footer = f"\n  ... (та ще {len(files) - max_files} файлів)"
        return f"{header}\n{shown}{footer}\n"

    shown = "\n".join(f"  - {f}" for f in files)
    return f"{header}\n{shown}\n"
