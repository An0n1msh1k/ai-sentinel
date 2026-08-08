import subprocess
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

def run_aider(prompt: str) -> int:
    """Run aider with the given prompt and handle errors."""
    console.print(f"[dim]Running aider with prompt: {prompt}[/dim]")
    try:
        result = subprocess.run(["aider", "--message", prompt], check=False)
        return result.returncode
    except FileNotFoundError:
        console.print("[bold red]❌ Error: 'aider' command not found. Please install it first.[/bold red]")
        return 1

def run_ruff() -> int:
    """Run ruff linter check and handle errors."""
    console.print("[dim]Running linter checks...[/dim]")
    try:
        result = subprocess.run(["ruff", "check", "."], check=False)
        return result.returncode
    except FileNotFoundError:
        console.print("[bold yellow]⚠ Warning: 'ruff' command not found. Skipping linting.[/bold yellow]")
        return 0

def handle_aider_failure(prompt: str):
    """Handle aider failure with a smart rollback option."""
    console.print("[bold yellow]⚠ Aider execution failed or was interrupted.[/bold yellow]")
    discard = typer.confirm("Do you want to discard partial changes?", default=False)
    if discard:
        try:
            subprocess.run(["git", "restore", "."], check=False)
            subprocess.run(["git", "clean", "-fd"], check=False)
            console.print("[bold green]✔ Partial changes discarded.[/bold green]")
        except FileNotFoundError:
            console.print("[bold red]❌ Error: 'git' command not found.[/bold red]")
    else:
        console.print("[bold blue]💡 Changes kept. You can resume later using:[/bold blue]")
        console.print(f"   [cyan]sentinel dev \"{prompt}\"[/cyan]")

@app.command(help="Run interactive development loop.")
def dev(
    instruction: str = typer.Argument(None, help="Optional instruction"),
):
    """Start the interactive dev loop or execute a single instruction."""
    check_env_file()
    
    if instruction:
        console.print("[bold blue]🚀 Starting Sentinel single instruction run...[/bold blue]")
        returncode = run_aider(instruction)
        if returncode != 0:
            handle_aider_failure(instruction)
            raise typer.Exit(code=returncode)
        run_ruff()
        return

    console.print("[bold blue]🚀 Starting Sentinel interactive dev loop...[/bold blue]")
    try:
        while True:
            prompt = typer.prompt("Enter your instruction (or 'exit' to quit)")
            if prompt.lower() in ("exit", "quit"):
                console.print("[bold green]Exiting dev loop. Goodbye![/bold green]")
                break
            
            returncode = run_aider(prompt)
            if returncode != 0:
                handle_aider_failure(prompt)
                continue
                
            run_ruff()
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
        ("Bandit (Security)", ["bandit", "-r", "-ll", "-ii", ".", "--exclude", "./.venv/*,./venv/*"]),
    ]
    for name, cmd in checks:
        console.print(f"\n[bold]Running {name}...[/bold]")
        try:
            result = subprocess.run(cmd, check=False)
            if result.returncode != 0:
                console.print(f"[bold red]❌ {name} failed.[/bold red]")
                failed = True
            else:
                console.print(f"[bold green]✅ {name} passed.[/bold green]")
        except FileNotFoundError:
            console.print(f"[bold red]❌ {name} failed: Command not found.[/bold red]")
            failed = True
            
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
    except Exception as e: # noqa: BLE001
        error_msg = str(e)
        if "429" in error_msg or "RateLimit" in error_msg or "Quota exceeded" in error_msg:
            console.print(Panel(
                "[bold yellow]⏳ Rate Limit Exceeded (429)[/bold yellow]\n\n"
                "The AI API has reached its request limit. The review cannot be completed right now.\n\n"
                "• [bold]Wait 15-60 seconds[/bold] and try again.\n"
                "• If you are committing code, bypass this check using:\n"
                "  [cyan]git commit --no-verify[/cyan]",
                title="API Quota Error",
                expand=False,
            ))
        else:
            console.print(f"[bold red]❌ Error: {error_msg}[/bold red]")
        raise typer.Exit(code=1)

@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """AI Sentinel CLI."""
    if ctx.invoked_subcommand is None:
        console.print(Panel("Run [bold cyan]sentinel --help[/bold cyan] for commands.", title="🛡️ AI Sentinel"))

if __name__ == "__main__":
    app()
