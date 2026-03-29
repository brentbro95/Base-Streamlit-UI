"""
Универсальный шаблон Streamlit UI для типовых задач:
- табличные данные
- временные ряды
- компьютерное зрение
- NLP / текст

Файл специально написан подробно и с большим количеством комментариев.
Его удобно использовать как конструктор:
можно брать отдельные блоки интерфейса и переносить в другой проект.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import pandas as pd
import streamlit as st

# ============================================================
# Необязательные зависимости
# ============================================================
# Эти библиотеки не критичны для запуска интерфейса.
# Даже если их нет в окружении, UI всё равно откроется.
# Это удобно для повторного использования шаблона в облегчённых проектах.

try:
    from PIL import Image
except Exception:
    Image = None  # type: ignore

try:
    import plotly.express as px
except Exception:
    px = None  # type: ignore


# ============================================================
# БЛОК 1. БАЗОВАЯ НАСТРОЙКА СТРАНИЦЫ
# ============================================================
# Подключать почти всегда.
# Это первый блок, который обычно переносят в новый Streamlit-проект.
# Он отвечает за:
# - заголовок вкладки браузера
# - иконку
# - ширину страницы
# - стартовое состояние боковой панели

st.set_page_config(
    page_title="Универсальный Data UI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("Универсальный Streamlit UI")
st.caption(
    "Шаблон интерфейса для задач по табличным данным, временным рядам, компьютерному зрению и NLP."
)


# ============================================================
# БЛОК 2. СЛУЖЕБНЫЕ СТРУКТУРЫ И ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================================
# Подключать, если нужен:
# - безопасный импорт данных
# - демо-данные
# - общие KPI-карточки
# - служебные функции для графиков
#
# Можно отключить целиком, если в проекте уже есть свои функции загрузки данных.

@dataclass
class AppState:
    task_type: str
    uploaded_files_count: int
    run_clicked: bool
    selected_target: Optional[str]
    selected_text_column: Optional[str]
    selected_time_column: Optional[str]
    selected_image_mode: Optional[str]


def safe_read_csv(file) -> pd.DataFrame:
    """Безопасное чтение CSV с запасным вариантом кодировки."""
    try:
        return pd.read_csv(file)
    except UnicodeDecodeError:
        file.seek(0)
        return pd.read_csv(file, encoding="latin-1")


def safe_read_table(file) -> pd.DataFrame:
    """
    Чтение табличного файла в DataFrame.

    Поддерживаются:
    - CSV
    - XLSX
    - Parquet

    Эту функцию удобно расширять под свои форматы.
    """
    name = file.name.lower()

    if name.endswith(".csv"):
        return safe_read_csv(file)

    if name.endswith(".xlsx"):
        return pd.read_excel(file)

    if name.endswith(".parquet"):
        return pd.read_parquet(file)

    raise ValueError(f"Неподдерживаемый формат файла: {file.name}")


@st.cache_data(show_spinner=False)
def build_demo_dataframe(task_type: str) -> pd.DataFrame:
    """
    Небольшие встроенные данные для демонстрации интерфейса.
    Полезно, когда нужно быстро проверить UI без реальных файлов.
    """
    if task_type == "Tabular":
        return pd.DataFrame(
            {
                "feature_num_1": [10, 12, 13, 15, 9, 7, 18, 20],
                "feature_num_2": [1.2, 1.0, 1.8, 2.1, 0.9, 0.7, 2.5, 2.9],
                "feature_cat": ["A", "A", "B", "B", "A", "C", "B", "C"],
                "target": [0, 0, 1, 1, 0, 0, 1, 1],
            }
        )

    if task_type == "Time Series":
        dates = pd.date_range("2024-01-01", periods=120, freq="D")
        values = [100 + (i * 0.25) + (5 if i % 7 == 0 else 0) for i in range(len(dates))]
        return pd.DataFrame({"timestamp": dates, "value": values})

    if task_type == "NLP / Text":
        return pd.DataFrame(
            {
                "text": [
                    "Delivery was quick and the item works well",
                    "The service was slow and support did not help",
                    "Excellent quality and clear documentation",
                    "Bad packaging but the product is acceptable",
                    "Support answered quickly and solved the issue",
                    "The interface is confusing and hard to use",
                ],
                "label": ["positive", "negative", "positive", "negative", "positive", "negative"],
            }
        )

    # Для Computer Vision таблица по умолчанию не нужна.
    return pd.DataFrame()


def render_info_cards(df: pd.DataFrame) -> None:
    """
    Небольшие KPI-карточки.
    Удобный универсальный блок для:
    - количества строк
    - количества столбцов
    - числа пропусков
    """
    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("Строки", f"{len(df):,}")

    with c2:
        st.metric("Столбцы", f"{df.shape[1]:,}")

    with c3:
        missing = int(df.isna().sum().sum()) if not df.empty else 0
        st.metric("Пропуски", f"{missing:,}")


def try_basic_plot(df: pd.DataFrame, x_col: str, y_col: str, title: str) -> None:
    """
    Универсальный блок построения графика.
    Если установлен Plotly — строим через него.
    Если нет — используем стандартный line_chart.
    """
    if px is not None:
        fig = px.line(df, x=x_col, y=y_col, title=title)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.line_chart(df.set_index(x_col)[y_col])


# ============================================================
# БЛОК 3. БОКОВАЯ ПАНЕЛЬ (НАВИГАЦИЯ + ВХОДНЫЕ ДАННЫЕ)
# ============================================================
# Подключать почти всегда.
# Это главный "каркас" интерфейса.
#
# Если тебе нужен только быстрый UI-скелет в другом проекте,
# чаще всего достаточно взять:
# - БЛОК 1
# - БЛОК 3
# - БЛОК 10 (запуск пайплайна)
#
# Этот блок отвечает за:
# - выбор типа задачи
# - загрузку файлов
# - кнопку запуска
# - сброс состояния

with st.sidebar:
    st.header("Навигация")

    task_type = st.selectbox(
        "Тип задачи",
        options=["Tabular", "Time Series", "Computer Vision", "NLP / Text"],
        help="Выберите тип задачи. Ниже интерфейс адаптируется под выбранный режим.",
    )

    st.header("Входные данные")

    uploaded_files = st.file_uploader(
        "Загрузите файлы",
        type=[
            "csv",
            "xlsx",
            "parquet",
            "txt",
            "json",
            "png",
            "jpg",
            "jpeg",
            "bmp",
            "webp",
            "zip",
        ],
        accept_multiple_files=True,
        help="Можно загрузить один или несколько файлов. Использование зависит от выбранного типа задачи.",
    )

    use_demo = st.checkbox(
        "Использовать встроенные демо-данные",
        value=(len(uploaded_files) == 0 and task_type != "Computer Vision"),
        help="Удобно для быстрой проверки интерфейса до подключения реального пайплайна.",
    )

    st.header("Запуск")

    run_clicked = st.button("Запустить пайплайн", type="primary", use_container_width=True)
    clear_outputs = st.button("Очистить / обновить экран", use_container_width=True)

if clear_outputs:
    st.cache_data.clear()
    st.rerun()

app_state = AppState(
    task_type=task_type,
    uploaded_files_count=len(uploaded_files),
    run_clicked=run_clicked,
    selected_target=None,
    selected_text_column=None,
    selected_time_column=None,
    selected_image_mode=None,
)


# ============================================================
# БЛОК 4. ОСНОВНОЙ МАКЕТ СТРАНИЦЫ
# ============================================================
# Подключать, если нужен привычный формат:
# - слева настройки
# - справа результаты
#
# Можно отключить, если ты хочешь свой layout:
# например tabs, expander-only или multipage-приложение.

config_col, result_col = st.columns([1, 1.2], gap="large")


# ============================================================
# БЛОК 5. ПАНЕЛЬ НАСТРОЕК ДЛЯ TABULAR / TIME SERIES / NLP
# ============================================================
# Подключать, если работаешь с таблицами / текстами / временными рядами.
# Можно отключить целиком для CV-only проекта.
#
# Внутри есть:
# - загрузка DataFrame
# - выбор колонок
# - task-specific настройки

with config_col:
    st.subheader("Настройки")

    if task_type in {"Tabular", "Time Series", "NLP / Text"}:
        # ----------------------------------------------------
        # БЛОК 5.1. ЗАГРУЗКА ТАБЛИЧНЫХ ДАННЫХ
        # ----------------------------------------------------
        # Подключать, если:
        # - входом являются csv/xlsx/parquet
        # - нужна единая точка загрузки в DataFrame
        #
        # Можно отключить, если данные приходят:
        # - из БД
        # - из API
        # - из заранее подготовленного DataFrame

        df: pd.DataFrame

        if use_demo:
            df = build_demo_dataframe(task_type)
            st.success("Загружены демо-данные.")

        elif uploaded_files:
            try:
                table_files = [
                    f for f in uploaded_files
                    if f.name.lower().endswith((".csv", ".xlsx", ".parquet"))
                ]

                if not table_files:
                    st.warning("Пока не загружено ни одного совместимого табличного файла.")
                    df = pd.DataFrame()
                else:
                    df = safe_read_table(table_files[0])
                    st.success(f"Загружен файл: {table_files[0].name}")
            except Exception as exc:
                st.error(f"Не удалось прочитать файл: {exc}")
                df = pd.DataFrame()
        else:
            df = pd.DataFrame()
            st.info("Загрузите табличный файл или включите демо-данные.")

        if not df.empty:
            render_info_cards(df)

        # ----------------------------------------------------
        # БЛОК 5.2. ОБЩИЕ СЕЛЕКТОРЫ КОЛОНОК
        # ----------------------------------------------------
        # Подключать, если нужен универсальный интерфейс выбора:
        # - target
        # - text column
        # - time column
        #
        # Можно брать только нужные части:
        # - для tabular оставить target
        # - для ts оставить time + value
        # - для nlp оставить text + label

        if not df.empty:
            all_columns = list(df.columns)

            if task_type == "Tabular":
                app_state.selected_target = st.selectbox(
                    "Целевая колонка",
                    options=[None] + all_columns,
                    format_func=lambda x: "Не выбрано" if x is None else x,
                    help="Выберите target-колонку для обучения или оценки.",
                )

            if task_type == "Time Series":
                app_state.selected_time_column = st.selectbox(
                    "Колонка времени",
                    options=[None] + all_columns,
                    format_func=lambda x: "Не выбрано" if x is None else x,
                    help="Выберите datetime-колонку, по которой будет упорядочен ряд.",
                )

                numeric_candidates = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]

                ts_target = st.selectbox(
                    "Колонка значения",
                    options=[None] + numeric_candidates,
                    format_func=lambda x: "Не выбрано" if x is None else x,
                    help="Выберите числовую колонку для моделирования или визуализации.",
                )

                app_state.selected_target = ts_target

            if task_type == "NLP / Text":
                app_state.selected_text_column = st.selectbox(
                    "Текстовая колонка",
                    options=[None] + all_columns,
                    format_func=lambda x: "Не выбрано" if x is None else x,
                    help="Выберите колонку с исходным текстом.",
                )

                app_state.selected_target = st.selectbox(
                    "Колонка метки",
                    options=[None] + all_columns,
                    format_func=lambda x: "Не выбрано" if x is None else x,
                    help="Выберите колонку с классом / меткой, если планируется обучение модели.",
                )

        # ----------------------------------------------------
        # БЛОК 5.3. НАСТРОЙКИ ДЛЯ TABULAR
        # ----------------------------------------------------
        # Подключать только для задач по табличным данным.
        # Можно отключить для TS / NLP / CV.

        if task_type == "Tabular":
            st.markdown("### Настройки tabular")

            st.checkbox("Показать описательную статистику", value=True)
            st.checkbox("Проверить пропуски", value=True)
            st.checkbox("Предложить типы признаков", value=True)

            st.caption("Замените эти переключатели на свои реальные шаги предобработки и обучения.")

        # ----------------------------------------------------
        # БЛОК 5.4. НАСТРОЙКИ ДЛЯ TIME SERIES
        # ----------------------------------------------------
        # Подключать только для временных рядов.
        # Здесь специально даны признаки без дата-лика.
        # Удобно переносить в проекты с forecasting / anomaly detection.

        elif task_type == "Time Series":
            st.markdown("### Настройки временных рядов")

            st.selectbox("Горизонт прогноза", [7, 14, 30, 60], index=0)

            st.multiselect(
                "Динамические признаки (без дата-лика)",
                options=[
                    "lag_1",
                    "lag_7",
                    "rolling_mean_7_shift1",
                    "rolling_std_7_shift1",
                    "expanding_mean_shift1",
                    "ewm_mean_shift1",
                    "calendar_features",
                ],
                default=["lag_1", "lag_7", "rolling_mean_7_shift1", "calendar_features"],
                help="Названия признаков отражают безопасное построение только по прошлым значениям.",
            )

            st.caption("В реальном проекте здесь можно вызывать функции построения признаков.")

        # ----------------------------------------------------
        # БЛОК 5.5. НАСТРОЙКИ ДЛЯ NLP
        # ----------------------------------------------------
        # Подключать только для текстовых задач.
        # Можно оставить как есть и просто заменить опции на свои.

        elif task_type == "NLP / Text":
            st.markdown("### Настройки NLP")

            st.multiselect(
                "Шаги предобработки",
                options=["lowercase", "strip spaces", "remove punctuation", "remove digits"],
                default=["lowercase", "strip spaces", "remove punctuation"],
            )

            st.selectbox(
                "Базовая модель",
                options=["TF-IDF + Logistic Regression", "TF-IDF + Linear SVM", "Naive Bayes"],
                index=0,
            )

            st.caption("Это UI-заглушка. Подключите к своему текстовому пайплайну.")

    else:
        # ====================================================
        # БЛОК 6. ПАНЕЛЬ НАСТРОЕК ДЛЯ COMPUTER VISION
        # ====================================================
        # Подключать только для CV-задач.
        # Можно отключить целиком, если приложение не работает с изображениями.
        #
        # В этом блоке обычно удобно держать:
        # - режим работы
        # - выбор модели
        # - confidence threshold

        st.markdown("### Настройки computer vision")

        app_state.selected_image_mode = st.radio(
            "Режим CV",
            options=["Просмотр одного изображения", "Пакетный просмотр", "Детекция / классификация"],
            help="Выберите общий сценарий работы для CV-задачи.",
        )

        model_name = st.selectbox(
            "Семейство модели",
            options=["YOLO", "Torchvision classifier", "Custom model"],
            index=0,
        )

        conf_threshold = st.slider("Порог confidence", 0.05, 0.95, 0.25, 0.05)

        st.caption(
            f"Выбрано семейство модели: {model_name}. Порог confidence: {conf_threshold:.2f}"
        )

        st.info(
            "Подключите этот блок к своей логике инференса или обучения. "
            "Шаблон фокусируется на структуре интерфейса."
        )


# ============================================================
# БЛОК 7. РЕЗУЛЬТАТЫ ДЛЯ TABULAR / TIME SERIES / NLP
# ============================================================
# Подключать, если нужен:
# - предпросмотр данных
# - быстрые графики
# - диагностические блоки
#
# Можно отключить частично:
# - оставить только preview
# - оставить только run-блок
# - оставить только визуализацию

with result_col:
    st.subheader("Рабочая область")

    if task_type in {"Tabular", "Time Series", "NLP / Text"}:
        # ----------------------------------------------------
        # БЛОК 7.1. ПОВТОРНАЯ ЗАГРУЗКА DF В ОБЛАСТИ РЕЗУЛЬТАТОВ
        # ----------------------------------------------------
        # Этот код дублируется специально.
        # Так удобнее переносить result-блок отдельно от config-блока.
        # Если хочешь сделать код короче — можно вынести в одну общую функцию.

        if use_demo:
            df = build_demo_dataframe(task_type)
        elif uploaded_files:
            table_files = [
                f for f in uploaded_files if f.name.lower().endswith((".csv", ".xlsx", ".parquet"))
            ]

            if table_files:
                try:
                    df = safe_read_table(table_files[0])
                except Exception:
                    df = pd.DataFrame()
            else:
                df = pd.DataFrame()
        else:
            df = pd.DataFrame()

        # ----------------------------------------------------
        # БЛОК 7.2. PREVIEW ДАННЫХ
        # ----------------------------------------------------
        # Подключать почти всегда.
        # Это один из самых полезных переносимых блоков.
        #
        # Можно отключить, если данные большие и ты не хочешь
        # отображать таблицу в UI.

        with st.expander("Предпросмотр данных", expanded=True):
            if not df.empty:
                st.dataframe(df.head(50), use_container_width=True)
            else:
                st.info("Табличные данные пока недоступны.")

        # ----------------------------------------------------
        # БЛОК 7.3. БЫСТРАЯ ДИАГНОСТИКА TABULAR
        # ----------------------------------------------------
        # Подключать только для tabular-задач.
        # Удобно для baseline-решений и быстрого EDA.

        if not df.empty:
            if task_type == "Tabular":
                with st.expander("Быстрая диагностика", expanded=False):
                    st.write("Типы данных:")

                    st.dataframe(
                        pd.DataFrame(
                            {
                                "column": df.columns,
                                "dtype": [str(t) for t in df.dtypes],
                                "missing": df.isna().sum().values,
                            }
                        ),
                        use_container_width=True,
                    )

                    numeric_cols = df.select_dtypes(include="number").columns.tolist()

                    if numeric_cols:
                        hist_col = st.selectbox("Числовая колонка для просмотра", numeric_cols)
                        st.bar_chart(df[hist_col].value_counts().sort_index())

            # ------------------------------------------------
            # БЛОК 7.4. ВИЗУАЛИЗАЦИЯ TIME SERIES
            # ------------------------------------------------
            # Подключать только для временных рядов.
            # Можно брать отдельно от всего остального кода.

            elif task_type == "Time Series":
                with st.expander("Визуализация ряда", expanded=True):
                    if app_state.selected_time_column and app_state.selected_target:
                        plot_df = df[[app_state.selected_time_column, app_state.selected_target]].copy()

                        plot_df[app_state.selected_time_column] = pd.to_datetime(
                            plot_df[app_state.selected_time_column],
                            errors="coerce",
                        )

                        plot_df = plot_df.dropna().sort_values(app_state.selected_time_column)

                        if not plot_df.empty:
                            try_basic_plot(
                                plot_df,
                                x_col=app_state.selected_time_column,
                                y_col=app_state.selected_target,
                                title="Временной ряд",
                            )
                        else:
                            st.warning("Не удалось построить корректный ряд после преобразования выбранных колонок.")
                    else:
                        st.info("Выберите колонку времени и колонку значения в панели настроек.")

                # --------------------------------------------
                # БЛОК 7.5. ШПАРГАЛКА ПО ПРИЗНАКАМ БЕЗ ДАТА-ЛИКА
                # --------------------------------------------
                # Подключать, если хочешь прямо в интерфейсе
                # показывать пользователю / себе шаблон безопасных признаков.
                # Удобно для конкурсных и baseline-решений.

                with st.expander("Шпаргалка: признаки без дата-лика", expanded=False):
                    st.code(
                        """
# Пример безопасного построения признаков для прогноза
df = df.sort_values("timestamp").copy()
df["lag_1"] = df["value"].shift(1)
df["lag_7"] = df["value"].shift(7)
df["rolling_mean_7_shift1"] = df["value"].shift(1).rolling(7).mean()
df["rolling_std_7_shift1"] = df["value"].shift(1).rolling(7).std()
df["expanding_mean_shift1"] = df["value"].shift(1).expanding().mean()
df["ewm_mean_shift1"] = df["value"].shift(1).ewm(alpha=0.3, adjust=False).mean()
                        """.strip(),
                        language="python",
                    )

            # ------------------------------------------------
            # БЛОК 7.6. ПРЕДПРОСМОТР И СХЕМА NLP-ПАЙПЛАЙНА
            # ------------------------------------------------
            # Подключать только для текстовых задач.
            # Удобно для базовой классификации текстов.

            elif task_type == "NLP / Text":
                with st.expander("Предпросмотр текста", expanded=True):
                    if app_state.selected_text_column:
                        columns_to_show = [app_state.selected_text_column]
                        if app_state.selected_target:
                            columns_to_show.append(app_state.selected_target)

                        st.dataframe(df[columns_to_show].head(20), use_container_width=True)
                    else:
                        st.info("Выберите текстовую колонку в панели настроек.")

                with st.expander("Шаблон NLP-пайплайна", expanded=False):
                    st.code(
                        """
# Простой переиспользуемый NLP pipeline
# 1) Считать данные в df
# 2) Очистить текст в df["text_clean"]
# 3) Разделить данные на train/valid
# 4) Построить baseline:
#       TfidfVectorizer(...)
#       LogisticRegression(...)
# 5) Оценить качество
# 6) Сохранить модель / подключить в приложение
                        """.strip(),
                        language="python",
                    )

        # ----------------------------------------------------
        # БЛОК 7.7. ЗАПУСК ПАЙПЛАЙНА ДЛЯ TABULAR / TS / NLP
        # ----------------------------------------------------
        # Подключать почти всегда.
        # Это точка входа в твою бизнес-логику.
        #
        # Обычно именно этот блок заменяется на:
        # - preprocess(...)
        # - train(...)
        # - predict(...)
        # - evaluate(...)

        st.markdown("### Запуск пайплайна")

        if run_clicked:
            with st.status("Выполнение...", expanded=True) as status:
                st.write("1. Чтение входных данных")
                st.write("2. Проверка конфигурации")
                st.write("3. Вызов предобработки / обучения / инференса")
                st.write("4. Подготовка результатов для интерфейса")
                status.update(label="Готово", state="complete")

            st.success("Сейчас это шаблон UI. Замените блок запуска на свою реальную логику.")

            if task_type == "Tabular":
                st.json(
                    {
                        "task_type": task_type,
                        "rows": int(len(df)) if not df.empty else 0,
                        "target": app_state.selected_target,
                        "next_step": "Подключите сюда функцию обучения или предсказания.",
                    }
                )

            elif task_type == "Time Series":
                st.json(
                    {
                        "task_type": task_type,
                        "rows": int(len(df)) if not df.empty else 0,
                        "time_column": app_state.selected_time_column,
                        "target": app_state.selected_target,
                        "next_step": "Подключите сюда прогнозирование или детекцию аномалий.",
                    }
                )

            elif task_type == "NLP / Text":
                st.json(
                    {
                        "task_type": task_type,
                        "rows": int(len(df)) if not df.empty else 0,
                        "text_column": app_state.selected_text_column,
                        "label_column": app_state.selected_target,
                        "next_step": "Подключите сюда предобработку текста и модель.",
                    }
                )
        else:
            st.info("Настройте параметры и нажмите 'Запустить пайплайн'.")

    else:
        # ====================================================
        # БЛОК 8. РЕЗУЛЬТАТЫ ДЛЯ COMPUTER VISION
        # ====================================================
        # Подключать только для CV.
        # Можно брать отдельно даже без всей табличной логики.
        #
        # Внутри:
        # - preview изображений
        # - место подключения инференса / обучения
        # - результат запуска

        with st.expander("Предпросмотр загруженных изображений", expanded=True):
            image_files = [
                f for f in uploaded_files
                if f.name.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".webp"))
            ]

            if not image_files:
                st.info("Загрузите изображения, чтобы увидеть их здесь.")
            else:
                preview_cols = st.columns(3)

                for idx, file in enumerate(image_files[:6]):
                    with preview_cols[idx % 3]:
                        st.write(file.name)

                        if Image is not None:
                            try:
                                img = Image.open(file)
                                st.image(img, use_container_width=True)
                            except Exception as exc:
                                st.warning(f"Не удалось открыть изображение: {exc}")
                        else:
                            st.caption("Библиотека Pillow недоступна в этом окружении.")

        # ----------------------------------------------------
        # БЛОК 8.1. КРЮЧОК ДЛЯ CV-ИНФЕРЕНСА ИЛИ ОБУЧЕНИЯ
        # ----------------------------------------------------
        # Это специальное место, куда удобно подключать:
        # - detect(...)
        # - classify(...)
        # - train_yolo(...)
        # - validate(...)
        #
        # Если у тебя проект только по инференсу, можно оставить
        # только этот блок и preview выше.

        with st.expander("Точка подключения инференса / обучения", expanded=False):
            st.code(
                """
# Пример точки подключения
if run_clicked:
    # 1) Загрузить изображение(я)
    # 2) Вызвать детектор / классификатор
    # 3) Преобразовать результаты в DataFrame
    # 4) Показать результаты в Streamlit
    pass
                """.strip(),
                language="python",
            )

        # ----------------------------------------------------
        # БЛОК 8.2. ЗАПУСК ДЛЯ CV
        # ----------------------------------------------------
        # Подключать, если нужно запускать обработку по кнопке.
        # Можно заменить своей логикой инференса или обучения.

        if run_clicked:
            st.success("Шаблонный запуск UI завершён.")

            st.json(
                {
                    "task_type": task_type,
                    "uploaded_images": len(
                        [f for f in uploaded_files if f.name.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".webp"))]
                    ),
                    "cv_mode": app_state.selected_image_mode,
                    "next_step": "Подключите сюда скрипт инференса или обучения для CV.",
                }
            )
        else:
            st.info("Загрузите изображения и нажмите 'Запустить пайплайн'.")


# ============================================================
# БЛОК 9. ПОДСКАЗКА ПО ВСТРАИВАНИЮ В ДРУГОЙ ПРОЕКТ
# ============================================================
# Подключать по желанию.
# Это чисто пояснительный блок, который помогает быстро понять,
# какие части файла переносить в другой проект.

st.markdown("---")

with st.expander("Как встраивать этот UI в другой проект", expanded=False):
    st.markdown(
        """
### Минимальный набор для быстрого старта
Подключите:
- **БЛОК 1** — базовая настройка страницы
- **БЛОК 3** — боковая панель
- **БЛОК 7.7** или **БЛОК 8.2** — запуск пайплайна

### Если проект по tabular
Подключите:
- **БЛОК 5**
- **БЛОК 7.2**
- **БЛОК 7.3**
- **БЛОК 7.7**

### Если проект по time series
Подключите:
- **БЛОК 5.4**
- **БЛОК 7.2**
- **БЛОК 7.4**
- **БЛОК 7.5**
- **БЛОК 7.7**

### Если проект по NLP
Подключите:
- **БЛОК 5.5**
- **БЛОК 7.2**
- **БЛОК 7.6**
- **БЛОК 7.7**

### Если проект по computer vision
Подключите:
- **БЛОК 6**
- **БЛОК 8**
- **БЛОК 8.1**
- **БЛОК 8.2**

### Общий принцип
Логику модели лучше держать отдельно:
- `src/preprocess.py`
- `src/train.py`
- `src/predict.py`

А в `app.py` оставлять только UI и вызовы этих функций.
        """
    )

st.caption("Шаблон: универсальная стартовая точка для нескольких классов задач.")
