# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Репозиторий

Презентация и рабочие материалы об опыте применения AI-агентов (Claude Code, расширение Superpowers) в корпоративной банковской среде. Целевой стек в описываемых задачах — Java/Spring, паттерн DAO, банковская доменная область.

## Сборка презентации

```bash
python3 build_presentation.py slides_skills.md
```

Генерирует `slides_skills.html` — автономную HTML-презентацию из markdown-файла. Зависимостей нет, только стандартная библиотека Python 3.

## Формат слайдов (slides_skills.md)

Markdown с собственным DSL:

- Заголовок презентации: ключи `title:`, `subtitle:`, `tag:` в начале файла
- Разделитель слайдов: `== SLIDE ==`
- Метаданные слайда: `title:`, `tag:`, `layout:`, `highlight:`, `prompt:`, `quote:`
- Layouts: `two-col`, `steps`, `case`, `plan`, `stats`, `bullets` (по умолчанию)
- Two-col секции: `[LEFT: label | style]` и `[RIGHT: label | style]`, style = `bad` / `good`
- Статистика: `stat: VALUE | label`
- Inline-разметка: `**bold**`, `` `code` ``

## Структура

- `slides_skills.md` — исходник презентации
- `build_presentation.py` — генератор HTML из markdown (парсер + рендер + CSS/JS)
- `slides_skills.html` — сгенерированный результат
- `.artifacts/` — вспомогательные материалы: экспорты сессий, заметки, скриншоты
