"""Справка для нового участника: PDF на две страницы.

Зачем отдельный документ, если есть README. README читают, когда уже
решили разбираться. Эту справку отправляют человеку, который ещё не
знает, что за проект и стоит ли в него влезать: ссылки, суть, список
задач — всё на двух страницах, без прокрутки по репозиторию.

Запуск:
    python scripts/make_handoff.py
Результат:
    docs/examples/VANTAGE_справка.pdf
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from vantage.act import register_cyrillic_font  # noqa: E402

REPO_URL = "https://github.com/k41270075-stack/hakathon"
SITE_URL = "https://hakathon-amber-three.vercel.app/"

# Палитра та же, что на сайте: бумага, чернила, охра
PAPER = (0.969, 0.957, 0.937)
INK = (0.086, 0.075, 0.059)
INK_2 = (0.29, 0.267, 0.235)
INK_3 = (0.522, 0.49, 0.447)
RUST = (0.722, 0.290, 0.122)
RULE = (0.867, 0.835, 0.784)


def build() -> Path:
    from reportlab.lib.colors import Color
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.pdfgen import canvas

    font, bold = register_cyrillic_font()
    out = REPO / "docs" / "examples" / "VANTAGE_справка.pdf"
    out.parent.mkdir(parents=True, exist_ok=True)

    width, height = A4
    pdf = canvas.Canvas(str(out), pagesize=A4)
    pdf.setTitle("VANTAGE — справка для нового участника")

    margin = 18 * mm
    right = width - margin
    state = {"y": height - margin}

    # ---------- примитивы ---------- #

    def paper_bg():
        pdf.setFillColor(Color(*PAPER))
        pdf.rect(0, 0, width, height, stroke=0, fill=1)

    def wrap(text: str, size: float, max_width: float, use_bold=False) -> list[str]:
        pdf.setFont(bold if use_bold else font, size)
        words, lines, cur = text.split(), [], ""
        for w in words:
            probe = f"{cur} {w}".strip()
            if pdf.stringWidth(probe, bold if use_bold else font, size) <= max_width:
                cur = probe
            else:
                if cur:
                    lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
        return lines

    def text(body: str, *, size=9.6, color=INK_2, gap=4.6, indent=0.0, use_bold=False):
        pdf.setFillColor(Color(*color))
        for line in wrap(body, size, right - margin - indent, use_bold):
            pdf.setFont(bold if use_bold else font, size)
            pdf.drawString(margin + indent, state["y"], line)
            state["y"] -= gap * mm
        state["y"] -= 0.8 * mm

    def heading(label: str, number: str = ""):
        state["y"] -= 3 * mm
        if number:
            pdf.setFillColor(Color(*RUST))
            pdf.setFont(bold, 8)
            pdf.drawString(margin, state["y"] + 4.6 * mm, number)
        pdf.setFillColor(Color(*INK))
        pdf.setFont(bold, 13)
        pdf.drawString(margin, state["y"], label)
        state["y"] -= 2.6 * mm
        pdf.setStrokeColor(Color(*INK))
        pdf.setLineWidth(1)
        pdf.line(margin, state["y"], right, state["y"])
        state["y"] -= 6 * mm

    def link_row(label: str, url: str):
        pdf.setFillColor(Color(*INK_3))
        pdf.setFont(font, 8.6)
        pdf.drawString(margin, state["y"], label)
        pdf.setFillColor(Color(*RUST))
        pdf.setFont(bold, 10)
        pdf.drawString(margin + 30 * mm, state["y"], url)
        pdf.linkURL(url, (margin + 30 * mm, state["y"] - 2, right, state["y"] + 10), relative=0)
        state["y"] -= 6.4 * mm

    def task(number: str, title: str, detail: str, where: str = "", blocking=False):
        box_top = state["y"] + 4 * mm
        pdf.setFillColor(Color(*(RUST if blocking else INK_3)))
        pdf.setFont(bold, 9)
        pdf.drawString(margin, state["y"], number)

        pdf.setFillColor(Color(*INK))
        pdf.setFont(bold, 9.8)
        pdf.drawString(margin + 8 * mm, state["y"], title)
        state["y"] -= 4.4 * mm

        pdf.setFillColor(Color(*INK_2))
        for line in wrap(detail, 8.8, right - margin - 8 * mm):
            pdf.setFont(font, 8.8)
            pdf.drawString(margin + 8 * mm, state["y"], line)
            state["y"] -= 3.9 * mm

        if where:
            pdf.setFillColor(Color(*INK_3))
            pdf.setFont(font, 8)
            pdf.drawString(margin + 8 * mm, state["y"], where)
            state["y"] -= 3.9 * mm

        if blocking:
            pdf.setStrokeColor(Color(*RUST))
            pdf.setLineWidth(1.6)
            pdf.line(margin - 2 * mm, box_top, margin - 2 * mm, state["y"] + 2 * mm)

        state["y"] -= 2.4 * mm

    def footer(page: int):
        pdf.setFillColor(Color(*INK_3))
        pdf.setFont(font, 7.4)
        pdf.drawString(margin, 12 * mm, "VANTAGE · Future Minds Hackathon 2026 · трек EcoFin · Астана")
        pdf.drawRightString(right, 12 * mm, f"{page} / 2")

    # ================= СТРАНИЦА 1 ================= #

    paper_bg()

    pdf.setFillColor(Color(*RUST))
    pdf.setFont(bold, 8)
    pdf.drawString(margin, state["y"], "СПРАВКА ДЛЯ НОВОГО УЧАСТНИКА")
    state["y"] -= 11 * mm

    pdf.setFillColor(Color(*INK))
    pdf.setFont(bold, 30)
    pdf.drawString(margin, state["y"], "VANTAGE")
    state["y"] -= 8 * mm
    pdf.setFont(font, 13)
    pdf.setFillColor(Color(*INK_2))
    pdf.drawString(margin, state["y"], "Поиск несанкционированных свалок по спутниковым снимкам")
    state["y"] -= 11 * mm

    pdf.setStrokeColor(Color(*RUST))
    pdf.setLineWidth(2)
    pdf.line(margin, state["y"], margin + 40 * mm, state["y"])
    state["y"] -= 9 * mm

    # ---- Ссылки ---- #
    link_row("Репозиторий", REPO_URL)
    link_row("Сайт", SITE_URL)
    state["y"] -= 2 * mm

    # ---- О чём проект ---- #
    heading("О чём проект", "01")
    text(
        "Вокруг любого города есть свалки, о которых власти не знают: их никто не считал, "
        "потому что никто не видел. Обойти степь пешком невозможно, дроны не покрывают такую площадь."
    )
    text(
        "Мы берём бесплатные спутниковые снимки за восемь лет и ищем места, где поверхность "
        "изменилась необратимо: растительность исчезла и не вернулась, появился открытый грунт. "
        "Для каждой находки считаем координаты, месяц возникновения, массу отходов, стоимость "
        "уборки в тенге и применимую статью КоАП — и складываем это в готовый черновик акта."
    )
    text(
        "Отдельно система предсказывает, где свалка появится в следующие 12 месяцев. "
        "Убрать свалку стоит миллионы; не дать ей появиться — стоит дорожного знака.",
        use_bold=True, color=INK,
    )

    # ---- Как отличаем ---- #
    heading("Главная сложность", "02")
    text(
        "На снимке с разрешением 10 метров свалка выглядит как серое пятно — ровно как карьер, "
        "стройплощадка или отвал грунта. Различает их не картинка, а комбинация пяти физических признаков:"
    )

    signals = [
        ("Падение NDVI без возврата", "растительность гибнет навсегда", "отсекает пашню: там NDVI возвращается весной"),
        ("Рост индекса открытого грунта", "поверхность становится минеральной", "отсекает застройку"),
        ("Отклик в коротковолновом ИК", "полимеры имеют характерное поглощение", "отсекает чистый грунт"),
        ("Нестабильность по радару", "поверхность меняется от съёмки к съёмке", "отсекает КАРЬЕР: его стенки стабильны"),
        ("Тепловая аномалия", "гниющая органика греет тело свалки", "отсекает СНЕГОСВАЛКУ: она холоднее фона"),
    ]
    for name, physics, cuts in signals:
        pdf.setFillColor(Color(*RUST))
        pdf.circle(margin + 1.4 * mm, state["y"] + 1 * mm, 1.1 * mm, stroke=0, fill=1)
        pdf.setFillColor(Color(*INK))
        pdf.setFont(bold, 9)
        pdf.drawString(margin + 5 * mm, state["y"], name)
        state["y"] -= 4 * mm
        pdf.setFillColor(Color(*INK_2))
        pdf.setFont(font, 8.4)
        pdf.drawString(margin + 5 * mm, state["y"], f"{physics} · {cuts}")
        state["y"] -= 5.6 * mm

    state["y"] -= 1 * mm
    text(
        "Модель не выдаёт вердикт «свалка / не свалка». Она показывает, какие признаки сработали "
        "и насколько сильно. Решение принимает человек.",
        use_bold=True, color=INK,
    )

    # ---- Состояние ---- #
    heading("В каком состоянии проект сейчас", "03")
    text(
        "Код написан целиком: 495 тестов, все модули на месте, сайт развёрнут. "
        "Но на карте сейчас ВЫДУМАННЫЕ объекты — генератор случайных точек для отладки интерфейса. "
        "Они помечены красной плашкой «демо-данные».",
        color=INK,
    )
    text(
        "Чтобы появились настоящие находки, нужно разметить обучающую выборку и запустить полный "
        "прогон по Астане. Это первые две задачи на следующей странице."
    )

    footer(1)
    pdf.showPage()

    # ================= СТРАНИЦА 2 ================= #

    paper_bg()
    state["y"] = height - margin

    pdf.setFillColor(Color(*RUST))
    pdf.setFont(bold, 8)
    pdf.drawString(margin, state["y"], "ЧТО НЕ СДЕЛАНО")
    state["y"] -= 9 * mm
    pdf.setFillColor(Color(*INK))
    pdf.setFont(bold, 18)
    pdf.drawString(margin, state["y"], "Задачи")
    state["y"] -= 6 * mm
    pdf.setFillColor(Color(*INK_2))
    pdf.setFont(font, 9.2)
    pdf.drawString(margin, state["y"], "Полный список с примерами кода — в файле docs/TODO.md")
    state["y"] -= 9 * mm

    pdf.setFillColor(Color(*RUST))
    pdf.setFont(bold, 9)
    pdf.drawString(margin, state["y"], "БЛОКИРУЕТ ВСЁ ОСТАЛЬНОЕ")
    state["y"] -= 7 * mm

    task("1", "Разметить обучающую выборку", blocking=True,
         detail="Часть меток берётся из OpenStreetMap автоматически: полигоны ТБО как положительные "
                "примеры, карьеры и стройки как отрицательные. Остальное надо просмотреть глазами "
                "и проставить 0 или 1.",
         where="src/vantage/labels.py · функция harvest_labels и manual_queue")

    task("2", "Запустить настоящий прогон по Астане", blocking=True,
         detail="Пайплайн собран, но полный прогон по области не запускался: нужна потайловая "
                "обработка. Метод AOI.tiles(20000) уже есть, оркестрации по плиткам нет.",
         where="src/vantage/pipeline.py")

    task("3", "Сделать страницу для ручной разметки",
         detail="Самое полезное, что можно добавить прямо сейчас: показывать два снимка «до и после», "
                "три кнопки — свалка, не свалка, непонятно — и писать результат в файл. "
                "Ускорит задачу 1 в разы.",
         where="новая страница в web/")

    state["y"] -= 2 * mm
    pdf.setFillColor(Color(*INK_3))
    pdf.setFont(bold, 9)
    pdf.drawString(margin, state["y"], "МОДУЛИ ГОТОВЫ, НО НЕ СОЕДИНЕНЫ В ЦЕПОЧКУ")
    state["y"] -= 7 * mm

    task("4", "Радар и тепло не влияют на решение",
         detail="Оба признака считаются, но детектор изменений использует только два оптических. "
                "Радар и тепло попадают только в панель объяснимости.",
         where="src/vantage/sar.py, thermal.py, change.py")

    task("5", "Доверификация не вызывается из пайплайна",
         detail="Модуль умеет тянуть снимки высокого разрешения от нескольких провайдеров и "
                "оценивать текстуру, но по-настоящему на реальных объектах не запускался.",
         where="src/vantage/verify.py")

    task("6", "Контроль устранения не получает данных",
         detail="Логика различения «убрали» и «засыпали грунтом» написана и покрыта тестами, "
                "но пайплайн не собирает историю наблюдений после даты обнаружения.",
         where="src/vantage/removal.py")

    state["y"] -= 2 * mm
    pdf.setFillColor(Color(*INK_3))
    pdf.setFont(bold, 9)
    pdf.drawString(margin, state["y"], "ДАННЫЕ, КОТОРЫЕ НЕ ДОБЫТЬ КОДОМ")
    state["y"] -= 7 * mm

    task("7", "Узнать тариф вывоза за тонну по Астане",
         detail="82% разброса в оценке ущерба даёт именно этот параметр. Один звонок оператору "
                "сузит все цифры сильнее, чем уточнение всех остальных величин вместе взятых. "
                "Сейчас стоит оценка, выведенная из тарифа Алматы.",
         where="config/economics_astana.yaml")

    task("8", "Съездить на найденную координату и снять видео",
         detail="Кадр «вот спутниковый снимок, а вот я стою на этой точке» — самый сильный слайд "
                "презентации. Три часа времени.")

    state["y"] -= 4 * mm
    pdf.setStrokeColor(Color(*RULE))
    pdf.setLineWidth(1)
    pdf.line(margin, state["y"], right, state["y"])
    state["y"] -= 7 * mm

    pdf.setFillColor(Color(*INK))
    pdf.setFont(bold, 11)
    pdf.drawString(margin, state["y"], "С чего начать")
    state["y"] -= 6 * mm
    text("1.  Открыть сайт по ссылке выше и пройти обучающий тур — пять минут, показывает всё.")
    text("2.  Прочитать docs/ARCHITECTURE.md — карта системы за десять минут.")
    text("3.  Открыть docs/TODO.md и взять задачу, отметив её галочкой прямо в файле.")
    text("4.  Установка: pip install -e \".[dev,ml,service]\" — подробности в README.")

    footer(2)
    pdf.showPage()
    pdf.save()
    return out


if __name__ == "__main__":
    path = build()
    print(f"Готово: {path}")
