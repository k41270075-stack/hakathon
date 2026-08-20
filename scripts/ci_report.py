"""Прогнать тесты и выдать причины падений аннотациями GitHub.

Логи прогонов CI закрыты для тех, у кого нет доступа к репозиторию, а
аннотации публичного репозитория читаются через API без токена. Это
единственный канал, по которому текст упавшего assert доезжает до того,
кто чинит.

Строка ``::error::`` — не декорация: GitHub превращает её в аннотацию,
которая видна и в интерфейсе, и в API check-runs.
"""

import re
import subprocess
import sys

result = subprocess.run(
    [sys.executable, "-m", "pytest", *sys.argv[1:], "-q", "--tb=line", "--no-header"],
    capture_output=True,
    text=True,
    encoding="utf-8",
    errors="replace",
)
output = result.stdout + result.stderr
print(output)

# --tb=line даёт по строке на падение: "путь:строка: текст ошибки".
reasons = re.findall(r"^/.*?:\d+: (.+)$", output, flags=re.M)
reasons += re.findall(r"^[A-Za-z]:.*?:\d+: (.+)$", output, flags=re.M)
failed = re.findall(r"^FAILED (\S+)(?: - (.*))?$", output, flags=re.M)

seen = set()
for name, message in failed:
    short = name.replace("tests/", "")
    text = (message or "").strip()
    if not text and reasons:
        text = reasons.pop(0)
    line = f"{short} :: {text}"[:400]
    if line in seen:
        continue
    seen.add(line)
    # Переводы строк в аннотации недопустимы — GitHub обрежет сообщение.
    print("::error title=" + short + "::" + line.replace("
", " "))

sys.exit(result.returncode)
