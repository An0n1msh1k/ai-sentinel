import datetime
import json
import sys
from pathlib import Path

from actor import generate
from critic import audit
from models import Critique

MAX_RETRIES = 2


def run_pipeline(prompt: str, strategy: str = "general") -> str:
    print(f"🤖 [Actor] Генерація першої чернетки (стратегія: {strategy})...")
    current_draft = generate(prompt, strategy_prompt=strategy)
    
    for attempt in range(1, MAX_RETRIES + 2):
        print(f"🔍 [Critic] Аудит спроби {attempt}...")
        critique: Critique = audit(prompt, current_draft, strategy)
        
        # Обробка відсутньої інформації (Pre-Flight Check)
        if critique.missing_info:
            print("\n⚠️ [ЗАПИТ УТОЧНЕННЯ] Критик потребує додаткових даних:")
            for item in critique.missing_info:
                print(f"   - {item}")
            
            if sys.stdin.isatty():
                try:
                    user_input = input("\n👉 Введіть уточнення (або натисніть Enter, щоб пропустити і продовжити): ").strip()
                except (KeyboardInterrupt, EOFError):
                    user_input = ""
            else:
                print("⏩ Неінтерактивний режим (CI/CD): пропускаємо запит уточнення...")
                user_input = ""
            
            if user_input:
                if user_input.startswith("@") or Path(user_input).is_file():
                    file_path = Path(user_input.lstrip("@"))
                    if file_path.is_file():
                        # Перевірка безпеки заборонених імен / розширень
                        forbidden_names = {".env", "id_rsa"}
                        forbidden_extensions = {".pem"}
                        if file_path.name.lower() in forbidden_names or file_path.suffix.lower() in forbidden_extensions:
                            print(f"\n🚨 [ПОПЕРЕДЖЕННЯ БЕЗПЕКИ] Спроба зчитати чутливий файл ({file_path.name}) заблокована через ризик витоку секретів!")
                        else:
                            content = file_path.read_text(encoding="utf-8", errors="replace")
                            prompt += f"\n\n[ДОДАТКОВИЙ ФАЙЛ ВІД КОРИСТУВАЧА: {file_path.name}]:\n{content}"
                    else:
                        print(f"⚠️ Файл {file_path} не знайдено, передаємо як звичайний текст.")
                        prompt += f"\n\n[УТОЧНЕННЯ]: {user_input}"
                else:
                    prompt += f"\n\n[УТОЧНЕННЯ ВІД КОРИСТУВАЧА]: {user_input}"
                
                current_draft = generate(prompt, strategy_prompt=strategy)
                continue
            else:
                print("⏩ Ігноруємо запит інформації та продовжуємо аудит...")
            
        # УСПІХ: Якщо бал високий і немає фатальних помилок
        if critique.score >= 95 and not critique.fatal_flaws:
            print(f"✅ [Успіх] Перевірку пройдено! (Оцінка: {critique.score}/100)")
            log_iteration(prompt, current_draft, critique, success=True)
            return current_draft
            
        # ПЕРЕГЕНЕРАЦІЯ: Якщо бал < 95, Критик повертає правки Актору
        print(f"⚠️  [Спроба {attempt}] Оцінка {critique.score}/100. Знайдено проблеми:")
        for flaw in critique.fatal_flaws:
            print(f"   ✖ {flaw}")
            
        if attempt <= MAX_RETRIES:
            print("↻  [Actor] Виправлення помилок на основі зауважень Критика...")
            correction_instructions = "\n".join(critique.corrections)
            current_draft = generate(
                f"ЗАВДАННЯ: {prompt}\n\nПОПЕРЕДНЯ ЧЕРНЕТКА:\n{current_draft}\n\nВКАЗІВКИ КРИТИКА ДЛЯ ВИПРАВЛЕННЯ:\n{correction_instructions}",
                strategy_prompt=strategy
            )
        else:
            print(f"⚠️ [BEST EFFORT] Не вдалося досягти 95%, але ось найкраща чернетка (Оцінка: {critique.score}/100):")
            print(current_draft)
            print("\nНерозв'язані проблеми:")
            for flaw in critique.fatal_flaws:
                print(f"   ✖ {flaw}")
            log_iteration(prompt, current_draft, critique, success=False)
            sys.exit(1)


def log_iteration(prompt: str, draft: str, critique: Critique, success: bool):
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"run_{timestamp}.json"
    
    log_data = {
        "timestamp": timestamp,
        "prompt": prompt,
        "success": success,
        "final_score": critique.score,
        "fatal_flaws": critique.fatal_flaws,
        "missing_info": critique.missing_info,
        "corrections": critique.corrections,
        "draft": draft
    }
    log_file.write_text(json.dumps(log_data, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Використання: python pipeline.py '<промпт>' [стратегія]")
        sys.exit(1)
    
    user_prompt = sys.argv[1]
    strat = sys.argv[2] if len(sys.argv) > 2 else "general"
    
    final_output = run_pipeline(user_prompt, strat)
    print("\n--- ФІНАЛЬНИЙ РЕЗУЛЬТАТ ---")
    print(final_output)
