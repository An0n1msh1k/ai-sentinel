import subprocess
import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel

app = typer.Typer(
    help="CLI tool for AI development, linting, and review.",
    add_completion=False,
)
console = Console()

def check_env_file():
    """Proactive .env checker that verifies environment variables."""
    env_path = Path(".env")
    if not env_path.exists():
        console.print(
            Panel(
                "[bold red]⚠ Missing .env file![/bold red]\n\n"
                "Sentinel requires a [cyan].env[/cyan] file to configure API keys.\n\n"
                "[bold]How to fix:[/bold]\n"
                "1. Create a file named [cyan].env[/cyan] in the root directory.\n"
                "2. Add your required API keys (e.g., [green]GEMINI_API_KEY=key[/green]).\n\n"
                "[bold]Where to get API keys:[/bold]\n"
                "• [link=https://aistudio.google.com/]Google AI Studio (Gemini)[/link]",
                title="[bold yellow]Environment Setup Required[/bold yellow]",
                expand=False,
            )
        )
        raise typer.Exit(code=1)

@app.command(help="Run interactive development loop.")
def dev():
    """Start the interactive dev loop."""
    check_env_file()
    console.print("[bold blue]🚀 Starting Sentinel interactive dev loop...[/bold blue]")
    try:
        while True:
            prompt = typer.prompt("Enter your instruction (or 'exit' to quit)")
            if prompt.lower() in ("exit", "quit"):
                console.print("[bold green]Exiting dev loop. Goodbye![/bold green]")
                break
            console.print(f"[dim]Running aider with prompt: {prompt}[/dim]")
            subprocess.run(["aider", "--message", prompt], check=False)
            console.print("[dim]Running linter checks...[/dim]")
            subprocess.run(["ruff", "check", "."], check=False)
    except (KeyboardInterrupt, EOFError):
        console.print("\n[bold green]Exiting dev loop. Goodbye![/bold green]")
        raise typer.Exit(code=0)

@app.command(help="Run static analysis and tests.")
def check():
    """Run code quality checks."""
    console.print("[bold cyan]🔍 Running project health checks...[/bold cyan]")
    failed = False
    checks = [
        ("Ruff (Linting)", ["ruff", "check", "."]),
        ("Bandit (Security)", ["bandit", "-r", "-ll", "-ii", "."]),
    ]
    for name, cmd in checks:
        console.print(f"\n[bold]Running {name}...[/bold]")
        result = subprocess.run(cmd, check=False)
        if result.returncode != 0:
            console.print(f"[bold red]❌ {name} failed.[/bold red]")
            failed = True
        else:
            console.print(f"[bold green]✅ {name} passed.[/bold green]")
    if failed:
        raise typer.Exit(code=1)
    else:
        console.print("\n[bold green]🎉 All checks passed successfully![/bold green]")

@app.command(help="Run audit using critic.py.")
def review(
    question: str = typer.Option(..., prompt="Task context"),
    draft: str = typer.Option(..., prompt="Draft code/text"),
    strategy: str = typer.Option("general", help="Strategy prompt file"),
):
    """Perform an audit."""
    check_env_file()
    console.print("[bold magenta]🕵 Initiating codebase review...[/bold magenta]")
    try:
        import critic
        if hasattr(critic, "audit"):
            critique = critic.audit(question=question, draft=draft, strategy_prompt=strategy)
            score_color = "green" if critique.score >= 80 else ("yellow" if critique.score >= 50 else "red")
            console.print(Panel(
                f"[bold]Score:[/bold] [{score_color}]{critique.score}/100[/{score_color}]\n\n"
                f"[bold]Fatal Flaws:[/bold]\n" + ("\n".join(f"• {f}" for f in critique.fatal_flaws) if critique.fatal_flaws else "None") + "\n\n"
                f"[bold]Corrections:[/bold]\n{critique.corrections}",
                title="[bold magenta]Audit Results[/bold magenta]",
                expand=False,
            ))
        else:
            console.print("[bold red]❌ critic.py has no 'audit' function.[/bold red]")
            raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[bold red]❌ Error: {e}[/bold red]")
        raise typer.Exit(code=1)

@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """AI Sentinel CLI."""
    if ctx.invoked_subcommand is None:
        console.print(Panel("Run [bold cyan]sentinel --help[/bold cyan] for commands.", title="🛡️ AI Sentinel"))

if __name__ == "__main__":
    app()
