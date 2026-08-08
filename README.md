# 🛡️ AI Sentinel

Your ultimate local Python CLI tool for AI-assisted development, automated code linting, and Senior-level code review.

## 🏗 Architecture

The tool is packaged globally via `setuptools` and provides a unified CLI powered by `Typer` and `Rich`:

- `sentinel dev`: Interactive AI Coder (uses Aider) with safe rollbacks.
- `sentinel check`: Fast local linters and static analysis (`ruff`, `bandit`).
- `sentinel review`: Senior Critic that analyzes your code against specific strategies and provides actionable fixes.

## 📥 Installation & Setup

### 1. Clone and Environment

```bash
git clone https://github.com/your-username/ai-sentinel.git
cd ai-sentinel

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Configure API Keys (.env)

Sentinel requires API keys to interact with the LLMs. Create your environment file from the template:

```bash
cp .env.example .env
```

Open the `.env` file and insert your keys:

- **GEMINI_API_KEY**: Get it from [Google AI Studio](https://aistudio.google.com/)
- **GROQ_API_KEY**: Get it from [Groq Console](https://console.groq.com/)

### 3. Install the CLI Tool

Install the package globally within your virtual environment to make the `sentinel` command available everywhere:

```bash
pip install -e .
```

## 🚀 Usage

Once installed, you can use the `sentinel` command anywhere on your system while the `.venv` is active.

### Development (AI Coder)

Start an interactive development session:

```bash
sentinel dev
```

Or pass an instruction directly:

```bash
sentinel dev --instruction "Create a new async function for database connection"
```

_(If the AI fails or the API rate limits, Sentinel will safely ask if you want to rollback your changes)._

### Code Quality Check

Run static analysis (Ruff) and security checks (Bandit):

```bash
sentinel check
```

### AI Code Review

Perform a deep codebase review using the Senior Critic (runs interactively):

```bash
sentinel review
```
