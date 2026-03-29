# Universal Streamlit UI Template

Универсальный шаблон интерфейса на Streamlit для нескольких типов задач:

- tabular / табличные данные
- time series / временные ряды
- computer vision / компьютерное зрение
- NLP / работа с текстами

Основная цель шаблона — дать понятный и переносимый `.py` файл, в котором интерфейсные блоки снабжены комментариями и легко вставляются в другой проект.

## Состав

- `app.py` — основной Streamlit UI шаблон
- `requirements.txt` — минимальные зависимости для запуска UI и работы с ноутбуками
- `README.md` — краткая инструкция по запуску и адаптации

## Быстрый запуск

### 1. Создать и активировать виртуальное окружение

Windows CMD:

```bash
python -m venv .venv
.venv\Scripts\activate
```

PowerShell:

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Linux / macOS:

```bash
python -m venv .venv
source .venv/bin/activate
```

### 2. Установить зависимости

```bash
pip install -r requirements.txt
```

### 3. Запустить интерфейс

```bash
streamlit run app.py
```

После запуска Streamlit обычно открывает локальную страницу в браузере автоматически.

## Что уже есть в шаблоне

В `app.py` добавлены готовые UI-блоки:

- глобальная навигация и sidebar
- загрузка файлов
- конфигурация под разные классы задач
- предпросмотр данных
- базовые визуализации
- placeholder-блок запуска пайплайна
- комментарии, где именно подключать свою бизнес-логику

## Как переносить в другой проект

Обычно достаточно перенести один или несколько блоков:

1. блок `st.set_page_config(...)`
2. helper-функции (`safe_read_table`, `render_info_cards`, и т.д.)
3. sidebar-навигацию
4. нужный task-блок:
   - `Tabular`
   - `Time Series`
   - `Computer Vision`
   - `NLP / Text`
5. секцию `Run pipeline`, заменив placeholder на вызов своих функций

Практический совет:
- UI-логику оставляй в `app.py`
- обучение моделей, инференс, предобработку и фичи выноси в отдельные модули (`src/...`)

## Основные методы и паттерны Streamlit, которые используются

### 1. `st.set_page_config`
Настройка страницы: заголовок вкладки, ширина layout, иконка, состояние sidebar.

### 2. `st.sidebar`
Позволяет вынести элементы управления в боковую панель.

### 3. `st.file_uploader`
Используется для загрузки файлов пользователем.

### 4. `st.columns`
Позволяет строить адаптивный layout в несколько колонок.

### 5. `st.expander`
Сворачиваемые блоки для предпросмотра данных, подсказок и тех. деталей.

### 6. `st.dataframe`
Отображение таблиц pandas DataFrame.

### 7. `st.plotly_chart`, `st.line_chart`, `st.bar_chart`
Базовые методы визуализации.

### 8. `st.button`
Кнопка запуска, например для обучения, инференса или проверки.

### 9. `st.status`
Удобный способ показать последовательные шаги выполнения.

### 10. `@st.cache_data`
Кэширование данных и результатов, чтобы UI работал быстрее.

## Экспорт ноутбуков в HTML

В `requirements.txt` уже включены:
- `ipykernel`
- `jupyter`
- `notebook`
- `jupyterlab`
- `nbconvert`

Пример команды экспорта ноутбука в HTML:

```bash
jupyter nbconvert --to html notebook.ipynb
```

или

```bash
python -m nbconvert --to html notebook.ipynb
```

## Документация Streamlit

Официальная документация Streamlit:

- https://docs.streamlit.io/

Основной API reference:

- https://docs.streamlit.io/develop/api-reference

## Идеи расширения

В шаблон легко добавить:

- вкладки (`st.tabs`)
- формы (`st.form`)
- хранение состояния (`st.session_state`)
- загрузку моделей
- авторизацию
- логирование
- download-кнопки для csv/html/json результатов
