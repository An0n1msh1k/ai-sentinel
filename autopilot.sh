#!/bin/bash
# AI Sentinel Autopilot — безперервний цикл самопокращення
# Зупинити: Ctrl+C

TASKS=(
    "Перевір cli.py на наявність мертвого коду та невикористовуваних імпортів. Видали все зайве."
    "Додай у cli.py логування кожної операції з таймстемпами у файл sentinel.log"
    "Спрости функцію auto_critic() — винеси дубльований код у окремі функції"
    "Додай перевірку на наявність .git перед операціями git"
    "Оптимізуй memory.py: обмеж розмір .sentinel_memory.md до 100 рядків, старі видаляй"
)

for task in "${TASKS[@]}"; do
    echo "=== $(date): $task ==="
    sentinel dev "$task"
    if [ $? -ne 0 ]; then
        echo "🛑 Circuit breaker or error — stopping."
        break
    fi
    echo "--- Чекаємо 10 секунд ---"
    sleep 10
done

echo "=== Автопілот завершено ==="