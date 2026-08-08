# AI Sentinel

Local AI assistant for code development, automated code review, and quality control.

## Architecture

```text
ai-sentinel/
├── dev-sentinel      # AI Coder & interactive code generation pipeline
├── sentinel-check    # Fast local linters and static analysis
└── sentinel          # Senior Critic (deep code and architecture review)
```

## Installation

```bash
git clone https://github.com/your-username/ai-sentinel.git
cd ai-sentinel
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

### 1. Development (AI Coder)
```bash
./dev-sentinel "Create an asynchronous file downloader" my_script.py
```

### 2. Linter Check
```bash
./sentinel-check
```

### 3. AI Code Review
```bash
./sentinel "Review changes for security and memory leaks" -d
```
