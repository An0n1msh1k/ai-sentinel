from setuptools import setup

setup(
    name="sentinel-cli",
    version="0.1.0",
    # Явно вказуємо всі наші Python-файли
    py_modules=["cli", "actor", "critic", "main", "models", "pipeline", "repo", "config"],
    install_requires=[
        "typer>=0.9.0",
        "rich>=13.0.0",
    ],
    entry_points={
        "console_scripts": [
            "sentinel=cli:app",
        ],
    },
    author="Developer",
    description="A global CLI tool for development, code checks, and reviews.",
    python_requires=">=3.8",
)
