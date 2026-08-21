#!/usr/bin/env bash
# Города: досчёт Алматы, затем прогон и досчёт Шымкента.
#
# Слияние на сайт НЕ делается автоматически. Оно меняет номера объектов
# (появляется приставка города), а к номерам привязаны разметка глазами и
# кэш доверификации. Такую замену надо смотреть глазами, а не получать
# утром свершившейся.
cd "$(dirname "$0")/.." || exit 1
PY=".venv/Scripts/python.exe"
say() { echo "[$(date +%H:%M:%S)] $*" | tee -a overnight.log; }

say "═══ цепочка 4: города ═══"

say "жду прогон Алматы"
bash scripts/wait_stable.sh run_almaty.log 180 180

if [ -f outputs_almaty/candidates_raw.geojson ]; then
  say "Алматы: сырых $(grep -o 'candidate_id' outputs_almaty/candidates_raw.geojson | wc -l)"
  say "досчёт Алматы"
  "$PY" scripts/finish_city.py almaty >> finish_almaty.log 2>&1 && say "Алматы досчитан" || say "ДОСЧЁТ АЛМАТЫ УПАЛ"
else
  say "Алматы: файла сырых кандидатов нет — прогон не дошёл"
fi

say "прогон Шымкента"
"$PY" scripts/run_city.py shymkent >> run_shymkent.log 2>&1 && say "Шымкент посчитан" || say "ПРОГОН ШЫМКЕНТА УПАЛ"

if [ -f outputs_shymkent/candidates_raw.geojson ]; then
  say "досчёт Шымкента"
  "$PY" scripts/finish_city.py shymkent >> finish_shymkent.log 2>&1 && say "Шымкент досчитан" || say "ДОСЧЁТ ШЫМКЕНТА УПАЛ"
fi

say "═══ цепочка 4 закончена — слияние ждёт решения ═══"
