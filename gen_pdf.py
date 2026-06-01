"""Генерация PDF-резюме на русском с QR-кодом"""
import os
from fpdf import FPDF

PDF_PATH = "/Users/evgenijmeskov/Documents/Современные любовные романы/Резюме_ML_PM.pdf"
FONT_PATH = "/Library/Fonts/Arial Unicode.ttf"

class ResumePDF(FPDF):
    def _setup_fonts(self):
        self.add_font('ArialUni', '', FONT_PATH, uni=True)
        self.add_font('ArialUni', 'B', FONT_PATH, uni=True)
        self.add_font('ArialUni', 'I', FONT_PATH, uni=True)

    def header(self):
        if self.page_no() == 1:
            self.set_draw_color(108, 92, 231)
            self.set_line_width(0.8)
            self.line(10, 28, 200, 28)

    def footer(self):
        self.set_y(-15)
        self.set_font('ArialUni', 'I', 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f'- {self.page_no()} -', align='C')

    def section_title(self, title):
        self.set_font('ArialUni', 'B', 11)
        self.set_text_color(108, 92, 231)
        self.cell(0, 7, title.upper(), new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(200, 200, 200)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(3)

    def bullet(self, text, bold_prefix=""):
        self.set_x(14)
        if bold_prefix:
            self.set_font('ArialUni', 'B', 9)
            self.cell(self.get_string_width(bold_prefix) + 1, 5, bold_prefix)
            self.set_font('ArialUni', '', 9)
            self.multi_cell(0, 5, text)
        else:
            self.set_font('ArialUni', '', 9)
            self.multi_cell(176, 5, "\u2022 " + text)
        self.ln(0.5)

    def body_text(self, text):
        self.set_x(14)
        self.set_font('ArialUni', '', 9)
        self.multi_cell(176, 5, text)
        self.ln(1)

    def key_value(self, key, value):
        self.set_x(14)
        self.set_font('ArialUni', 'B', 9)
        self.cell(35, 5, key)
        self.set_font('ArialUni', '', 9)
        self.cell(0, 5, value, new_x="LMARGIN", new_y="NEXT")
        self.ln(0.5)


pdf = ResumePDF()
pdf._setup_fonts()
pdf.set_auto_page_break(auto=True, margin=20)
pdf.add_page()

# === ЗАГОЛОВОК ===
pdf.set_font('ArialUni', 'B', 18)
pdf.set_text_color(26, 26, 46)
pdf.cell(0, 8, 'Мешков Евгений Александрович', new_x="LMARGIN", new_y="NEXT")

pdf.set_font('ArialUni', '', 11)
pdf.set_text_color(80, 80, 80)
pdf.cell(0, 6, 'AI Workflow Designer / Специалист по внедрению AI', new_x="LMARGIN", new_y="NEXT")

pdf.set_font('ArialUni', 'I', 9)
pdf.set_text_color(150, 150, 150)
pdf.cell(0, 5, 'Псевдоним: Арон Родович  |  English B2  |  01.03.1993  |  женат, есть ребёнок', new_x="LMARGIN", new_y="NEXT")
pdf.ln(4)

# === О СЕБЕ ===
pdf.set_fill_color(108, 92, 231)
pdf.set_text_color(255, 255, 255)
pdf.set_font('ArialUni', 'B', 10)
pdf.cell(0, 8, '  О СЕБЕ', fill=True, new_x="LMARGIN", new_y="NEXT")
pdf.ln(1)

pdf.set_text_color(60, 60, 60)
pdf.set_font('ArialUni', '', 9)
pdf.set_x(14)
pdf.multi_cell(176, 5,
    "Последний год проектирую мультиагентные AI-системы и пайплайны генерации контента. "
    "Специализируюсь на организации взаимодействия между моделями, управлении контекстом, "
    "RAG, tool calling и настройке процессов генерации. Быстро осваиваю новые инструменты "
    "и довожу прототипы до рабочего состояния."
)
pdf.ln(3)

# === КЛЮЧЕВЫЕ ПРОЕКТЫ ===
pdf.set_text_color(26, 26, 46)
pdf.section_title('Ключевые проекты')

pdf.set_font('ArialUni', 'B', 9.5)
pdf.set_text_color(26, 26, 46)
pdf.cell(0, 5, '1. Мультиагентная платформа для генерации прозы (2025–2026)', new_x="LMARGIN", new_y="NEXT")
pdf.set_text_color(80, 80, 80)
pdf.body_text(
    "Спроектировал архитектуру для 5 AI-агентов (писатель, канон, стилист, "
    "секретутка, менеджер), которые совместно пишут и проверяют главы художественных "
    "текстов. Пайплайн включает RAG, tool calling, SSE-стриминг."
)
pdf.bullet("скользящее окно из 5-6 глав + 4-5 RAW-дискуссий + суммаризация", "Контекст: ")
pdf.bullet("4 реальных инструмента — агенты создают файлы на диске", "Tool calling: ")
pdf.bullet("у каждого агента personal_rules.md вместо общей памяти", "Правила: ")
pdf.bullet("Personal Rules / Journal / Canon / Experience", "4 слоя данных: ")
pdf.ln(1)

pdf.set_font('ArialUni', 'B', 9.5)
pdf.set_text_color(26, 26, 46)
pdf.cell(0, 5, '2. Роман на 28 глав — AI без ручного редактирования (2025)', new_x="LMARGIN", new_y="NEXT")
pdf.set_text_color(80, 80, 80)
pdf.body_text(
    "Спроектировал пайплайн, который выдал готовый роман в жанре contemporary romance "
    "(28 глав) без единой правки текста человеком. Доступен под псевдонимом Арон Родович."
)
pdf.bullet("Deep prompt engineering для голоса персонажа через 28 глав")
pdf.bullet("Пайплайн: писатель → канон → стилист → секретутка")
pdf.bullet("Chistovik — автоочистка AI-маркеров, воды, повторов, клише")
pdf.bullet("Вывод: заставить AI писать хорошую прозу сложнее, чем хороший код")
pdf.ln(1)

pdf.set_font('ArialUni', 'B', 9.5)
pdf.set_text_color(26, 26, 46)
pdf.cell(0, 5, '3. Методология AI-письма и исследования (2025–2026)', new_x="LMARGIN", new_y="NEXT")
pdf.set_text_color(80, 80, 80)
pdf.bullet("Граф жанра: формализованные правила, тропы и биты для romance-серии")
pdf.bullet("3-слойный разбор текста (нарратив, события, NVAP-ядро)")
pdf.bullet("Когнитивный трекинг — контроль знаний персонажа по главам")
pdf.bullet("15+ экспериментов по качеству моделей, устойчивости контекста, мультиагентным архитектурам")
pdf.ln(1)

pdf.set_font('ArialUni', 'B', 9.5)
pdf.set_text_color(26, 26, 46)
pdf.cell(0, 5, '4. Распределённая GenAI-инфраструктура (2025–2026)', new_x="LMARGIN", new_y="NEXT")
pdf.set_text_color(80, 80, 80)
pdf.body_text("Двухмашинная распределённая система:")
pdf.key_value("MacBook M1:", "LM Studio — Gemma 4 E4B, Granite 4 H Tiny")
pdf.key_value("Windows R9:", "Ollama — Gemma 4 8B/26B, Qwen; OpenRouter — Owl-alpha, DeepSeek R1")
pdf.key_value("RAG:", "ChromaDB + all-MiniLM-L6-v2")
pdf.key_value("Интеграция:", "MCP, opencode, LFM proxy, OpenClaw gateway")
pdf.ln(2)

# === НАВЫКИ ===
pdf.set_text_color(26, 26, 46)
pdf.section_title('Навыки')

pdf.set_font('ArialUni', 'B', 9)
pdf.cell(30, 5, 'AI / LLM:')
pdf.set_font('ArialUni', '', 9)
pdf.set_text_color(80, 80, 80)
pdf.cell(0, 5, 'ChatGPT, Claude, Gemini, Gemma 4, Granite 4, Owl-alpha, DeepSeek R1, Qwen 3.5', new_x="LMARGIN", new_y="NEXT")
pdf.ln(0.5)

pdf.set_text_color(26, 26, 46)
pdf.set_font('ArialUni', 'B', 9)
pdf.cell(30, 5, 'AI Engineering:')
pdf.set_font('ArialUni', '', 9)
pdf.set_text_color(80, 80, 80)
pdf.cell(0, 5, 'RAG, Tool Calling, Context Management, Prompt Engineering, Multi-Agent Systems, SSE', new_x="LMARGIN", new_y="NEXT")
pdf.ln(0.5)

pdf.set_text_color(26, 26, 46)
pdf.set_font('ArialUni', 'B', 9)
pdf.cell(30, 5, 'Инфраструктура:')
pdf.set_font('ArialUni', '', 9)
pdf.set_text_color(80, 80, 80)
pdf.cell(0, 5, 'ChromaDB, API, Local LLM, Gateway, macOS + Windows, Git', new_x="LMARGIN", new_y="NEXT")
pdf.ln(0.5)

pdf.set_text_color(150, 150, 150)
pdf.set_font('ArialUni', 'I', 8)
pdf.cell(0, 5, '* код пишет AI — я проектирую архитектуру, ставлю задачи, отлаживаю, улучшаю', new_x="LMARGIN", new_y="NEXT")
pdf.ln(3)

# === ЧТО ПОНИМАЮ ПРО AI ===
pdf.set_text_color(26, 26, 46)
pdf.section_title('Что понимаю про AI (практика)')
pdf.bullet("Мультиагентные системы: архитектура ролей, оркестрация, tool loop (5 раундов, 8 вызовов)")
pdf.bullet("Управление контекстом LLM: скользящее окно, суммаризация, 4-слойное хранение")
pdf.bullet("RAG: ChromaDB, эмбеддинги, hybrid retrieval, тайминг данных")
pdf.bullet("Tool calling: structured output, multi-round loop")
pdf.bullet("Сравнительное тестирование LLM: поиск регрессий, подбор модели под сценарий")
pdf.bullet("Локальные модели: GGUF/MLX, kv-cache quantization")
pdf.bullet("API-модели: OpenRouter, multi-key ротация, подбор под стоимость/качество")
pdf.bullet("Prompt engineering: system prompts, few-shot, role-based, chain-of-thought")
pdf.bullet("AI-инфраструктура: macOS + Windows, прокси, gateway, автозапуск, мониторинг")
pdf.ln(2)

# === ОЖИДАНИЯ ===
pdf.set_text_color(26, 26, 46)
pdf.section_title('Ожидания')
pdf.key_value("Зарплата:", "от 150 000 руб.")
pdf.key_value("Формат:", "удалённо")
pdf.key_value("График:", "гибкий, полный день")
pdf.key_value("Техника:", "Windows (Ryzen 9) + MacBook Pro (M1) + мобильные устройства")
pdf.ln(4)

# === QR-КОД ===
pdf.set_fill_color(108, 92, 231)
pdf.set_text_color(255, 255, 255)
pdf.set_font('ArialUni', 'B', 10)
pdf.cell(0, 8, '  ИНТЕРАКТИВНАЯ ВЕРСИЯ', fill=True, new_x="LMARGIN", new_y="NEXT")
pdf.ln(3)

qr_path = '/tmp/qr_resume.png'
if os.path.exists(qr_path):
    pdf.image(qr_path, x=85, y=pdf.get_y(), w=40, h=40)
    pdf.ln(42)

pdf.set_x(10)
pdf.set_font('ArialUni', '', 9)
pdf.set_text_color(80, 80, 80)
pdf.cell(0, 5, 'Отсканируй QR-код или перейди по ссылке:', new_x="LMARGIN", new_y="NEXT", align='C')
pdf.set_font('ArialUni', 'U', 9)
pdf.set_text_color(108, 92, 231)
pdf.cell(0, 5, 'https://familybothelp.github.io/resume/', new_x="LMARGIN", new_y="NEXT", align='C')
pdf.ln(3)

pdf.set_text_color(100, 100, 100)
pdf.set_font('ArialUni', 'I', 8)
pdf.cell(0, 5, 'Интерактивная версия включает живой AI-чат (Owl-alpha).', new_x="LMARGIN", new_y="NEXT", align='C')

pdf.output(PDF_PATH)
print(f"PDF сохранён: {PDF_PATH}")
print(f"Размер: {os.path.getsize(PDF_PATH)} байт")
