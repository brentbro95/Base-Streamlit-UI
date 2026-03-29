"""
Universal Streamlit UI template for common data tasks:
- Tabular data
- Time series
- Computer vision
- NLP / text

The file is intentionally verbose and heavily commented so individual UI blocks
can be moved into another project with minimal effort.
"""

from __future__ import annotations

from dataclasses import dataclass
from io import StringIO, BytesIO
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import streamlit as st

# Optional imports:
# These libraries are common, but the UI should still open even if some of them
# are unavailable in the runtime environment. This makes the template safer to
# reuse in lightweight projects.
try:
    from PIL import Image
except Exception:
    Image = None  # type: ignore

try:
    import plotly.express as px
except Exception:
    px = None  # type: ignore


# =============================================================================
# Page config and shared style
# =============================================================================
# This block is usually the first one you move into a new project.
# It defines the browser tab title, page width, and initial sidebar state.
st.set_page_config(
    page_title="Universal Data UI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("Universal Streamlit UI")
st.caption(
    "A reusable interface template for tabular data, time series, computer vision, and NLP tasks."
)


# =============================================================================
# Utility helpers
# =============================================================================
# These helpers keep the main layout code clean and easier to transplant.
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
    """Read CSV with a couple of safe fallbacks."""
    try:
        return pd.read_csv(file)
    except UnicodeDecodeError:
        file.seek(0)
        return pd.read_csv(file, encoding="latin-1")


def safe_read_table(file) -> pd.DataFrame:
    """
    Read the uploaded tabular file into a DataFrame.
    Extend this function when you want to support more formats.
    """
    name = file.name.lower()
    if name.endswith(".csv"):
        return safe_read_csv(file)
    if name.endswith(".xlsx"):
        return pd.read_excel(file)
    if name.endswith(".parquet"):
        return pd.read_parquet(file)
    raise ValueError(f"Unsupported file format: {file.name}")


@st.cache_data(show_spinner=False)
def build_demo_dataframe(task_type: str) -> pd.DataFrame:
    """
    A small built-in dataset so the UI is usable even without uploaded files.
    This is useful for quick UI tests and demonstrations.
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

    # For computer vision there is no default DataFrame.
    return pd.DataFrame()


def render_info_cards(df: pd.DataFrame) -> None:
    """Small KPI row reused by multiple tabs."""
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Rows", f"{len(df):,}")
    with c2:
        st.metric("Columns", f"{df.shape[1]:,}")
    with c3:
        missing = int(df.isna().sum().sum()) if not df.empty else 0
        st.metric("Missing values", f"{missing:,}")


def try_basic_plot(df: pd.DataFrame, x_col: str, y_col: str, title: str) -> None:
    """Plotly is optional. Fall back to line/bar tables if not available."""
    if px is not None:
        fig = px.line(df, x=x_col, y=y_col, title=title)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.line_chart(df.set_index(x_col)[y_col])


# =============================================================================
# Sidebar: global controls
# =============================================================================
# This whole block can be moved as the "navigation shell" into any project.
with st.sidebar:
    st.header("Navigation")
    task_type = st.selectbox(
        "Task type",
        options=["Tabular", "Time Series", "Computer Vision", "NLP / Text"],
        help="Choose the type of problem. The interface below will adapt to the selected mode.",
    )

    st.header("Input")
    uploaded_files = st.file_uploader(
        "Upload files",
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
        help="Upload one or multiple files. The exact usage depends on the chosen task type.",
    )

    use_demo = st.checkbox(
        "Use built-in demo data",
        value=(len(uploaded_files) == 0 and task_type != "Computer Vision"),
        help="Useful for a quick interface check before wiring in your real pipeline.",
    )

    st.header("Run")
    run_clicked = st.button("Run pipeline", type="primary", use_container_width=True)
    clear_outputs = st.button("Clear / refresh view", use_container_width=True)

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


# =============================================================================
# Top-level layout
# =============================================================================
# This layout pattern works well in most projects:
# - left side: configuration
# - right side: results / previews
config_col, result_col = st.columns([1, 1.2], gap="large")


# =============================================================================
# Configuration panel
# =============================================================================
with config_col:
    st.subheader("Configuration")

    if task_type in {"Tabular", "Time Series", "NLP / Text"}:
        # -----------------------------
        # Data loading block
        # -----------------------------
        # Reusable block: read uploaded table into a DataFrame.
        df: pd.DataFrame
        if use_demo:
            df = build_demo_dataframe(task_type)
            st.success("Demo data loaded.")
        elif uploaded_files:
            try:
                table_files = [
                    f for f in uploaded_files
                    if f.name.lower().endswith((".csv", ".xlsx", ".parquet"))
                ]
                if not table_files:
                    st.warning("No compatible table files uploaded yet.")
                    df = pd.DataFrame()
                else:
                    df = safe_read_table(table_files[0])
                    st.success(f"Loaded: {table_files[0].name}")
            except Exception as exc:
                st.error(f"Could not read file: {exc}")
                df = pd.DataFrame()
        else:
            df = pd.DataFrame()
            st.info("Upload a table file or enable demo data.")

        if not df.empty:
            render_info_cards(df)

        # -----------------------------
        # Shared column selectors
        # -----------------------------
        # These selectors are designed to be generic and can be reused
        # in almost any data project.
        if not df.empty:
            all_columns = list(df.columns)

            if task_type == "Tabular":
                app_state.selected_target = st.selectbox(
                    "Target column",
                    options=[None] + all_columns,
                    format_func=lambda x: "Not selected" if x is None else x,
                    help="Choose the target column for training or evaluation.",
                )

            if task_type == "Time Series":
                app_state.selected_time_column = st.selectbox(
                    "Time column",
                    options=[None] + all_columns,
                    format_func=lambda x: "Not selected" if x is None else x,
                    help="Choose the datetime column used for ordering the series.",
                )

                numeric_candidates = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
                ts_target = st.selectbox(
                    "Value column",
                    options=[None] + numeric_candidates,
                    format_func=lambda x: "Not selected" if x is None else x,
                    help="Choose the numeric series to model or visualize.",
                )
                app_state.selected_target = ts_target

            if task_type == "NLP / Text":
                app_state.selected_text_column = st.selectbox(
                    "Text column",
                    options=[None] + all_columns,
                    format_func=lambda x: "Not selected" if x is None else x,
                    help="Choose the column that contains the raw text.",
                )
                app_state.selected_target = st.selectbox(
                    "Label column",
                    options=[None] + all_columns,
                    format_func=lambda x: "Not selected" if x is None else x,
                    help="Choose the target label column if you plan to train a classifier.",
                )

        # -----------------------------
        # Task-specific settings
        # -----------------------------
        if task_type == "Tabular":
            st.markdown("### Tabular settings")
            st.checkbox("Show descriptive statistics", value=True)
            st.checkbox("Detect missing values", value=True)
            st.checkbox("Suggest feature types", value=True)
            st.caption("Replace these toggles with your actual preprocessing and modeling steps.")

        elif task_type == "Time Series":
            st.markdown("### Time series settings")
            st.selectbox("Forecast horizon", [7, 14, 30, 60], index=0)
            st.multiselect(
                "Dynamic features (safe by design)",
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
                help="Names intentionally reflect no-leakage construction using past values only.",
            )
            st.caption("In your own project, these controls can call feature-building functions.")

        elif task_type == "NLP / Text":
            st.markdown("### NLP settings")
            st.multiselect(
                "Preprocessing steps",
                options=["lowercase", "strip spaces", "remove punctuation", "remove digits"],
                default=["lowercase", "strip spaces", "remove punctuation"],
            )
            st.selectbox(
                "Baseline model",
                options=["TF-IDF + Logistic Regression", "TF-IDF + Linear SVM", "Naive Bayes"],
                index=0,
            )
            st.caption("This is a UI placeholder. Connect it to your own text pipeline.")

    else:
        # =============================================================================
        # Computer vision configuration
        # =============================================================================
        # This block is kept separate because CV usually works with images / folders / zips
        # rather than a single table.
        st.markdown("### Computer vision settings")

        app_state.selected_image_mode = st.radio(
            "CV mode",
            options=["Single image preview", "Batch review", "Detection/Classification pipeline"],
            help="Choose a high-level scenario for your computer vision task.",
        )

        model_name = st.selectbox(
            "Model family",
            options=["YOLO", "Torchvision classifier", "Custom model"],
            index=0,
        )
        conf_threshold = st.slider("Confidence threshold", 0.05, 0.95, 0.25, 0.05)

        st.caption(
            f"Selected model family: {model_name}. Confidence threshold: {conf_threshold:.2f}"
        )
        st.info(
            "Connect this block to your actual inference or training functions. "
            "The template focuses on reusable UI structure."
        )


# =============================================================================
# Results panel
# =============================================================================
with result_col:
    st.subheader("Workspace")

    if task_type in {"Tabular", "Time Series", "NLP / Text"}:
        # Recreate df in this scope to keep the result panel independent enough
        # for copy-paste into another script. This duplication is deliberate.
        if use_demo:
            df = build_demo_dataframe(task_type)
        elif uploaded_files:
            table_files = [f for f in uploaded_files if f.name.lower().endswith((".csv", ".xlsx", ".parquet"))]
            if table_files:
                try:
                    df = safe_read_table(table_files[0])
                except Exception:
                    df = pd.DataFrame()
            else:
                df = pd.DataFrame()
        else:
            df = pd.DataFrame()

        # -----------------------------
        # Preview block
        # -----------------------------
        # A highly reusable block: every data app usually needs a preview area.
        with st.expander("Data preview", expanded=True):
            if not df.empty:
                st.dataframe(df.head(50), use_container_width=True)
            else:
                st.info("No table data available yet.")

        # -----------------------------
        # Basic diagnostics / charts
        # -----------------------------
        if not df.empty:
            if task_type == "Tabular":
                with st.expander("Quick diagnostics", expanded=False):
                    st.write("Data types:")
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
                        hist_col = st.selectbox("Numeric column to inspect", numeric_cols)
                        st.bar_chart(df[hist_col].value_counts().sort_index())

            elif task_type == "Time Series":
                with st.expander("Series visualization", expanded=True):
                    if app_state.selected_time_column and app_state.selected_target:
                        plot_df = df[[app_state.selected_time_column, app_state.selected_target]].copy()
                        plot_df[app_state.selected_time_column] = pd.to_datetime(
                            plot_df[app_state.selected_time_column], errors="coerce"
                        )
                        plot_df = plot_df.dropna().sort_values(app_state.selected_time_column)
                        if not plot_df.empty:
                            try_basic_plot(
                                plot_df,
                                x_col=app_state.selected_time_column,
                                y_col=app_state.selected_target,
                                title="Time series",
                            )
                        else:
                            st.warning("Could not create a valid time series after parsing the selected columns.")
                    else:
                        st.info("Select time and value columns in the configuration panel.")

                with st.expander("No-leakage feature recipe", expanded=False):
                    st.code(
                        """
# Example: safe feature construction for forecasting
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

            elif task_type == "NLP / Text":
                with st.expander("Text preview", expanded=True):
                    if app_state.selected_text_column:
                        st.dataframe(
                            df[[app_state.selected_text_column] + ([app_state.selected_target] if app_state.selected_target else [])].head(20),
                            use_container_width=True,
                        )
                    else:
                        st.info("Select a text column in the configuration panel.")

                with st.expander("Reusable pipeline outline", expanded=False):
                    st.code(
                        """
# Simple reusable NLP pipeline sketch
# 1) Read data into df
# 2) Clean text into df["text_clean"]
# 3) Split into train/valid
# 4) Build baseline:
#       TfidfVectorizer(...)
#       LogisticRegression(...)
# 5) Evaluate
# 6) Save model / expose in app
                        """.strip(),
                        language="python",
                    )

        # -----------------------------
        # Run area
        # -----------------------------
        # In a real project this is where you call your pipeline code.
        st.markdown("### Pipeline run")
        if run_clicked:
            with st.status("Running...", expanded=True) as status:
                st.write("1. Reading inputs")
                st.write("2. Validating configuration")
                st.write("3. Calling your preprocessing / training / inference code")
                st.write("4. Preparing outputs for the interface")
                status.update(label="Done", state="complete")

            st.success("This is a UI template. Replace the placeholder run block with your actual logic.")

            if task_type == "Tabular":
                st.json(
                    {
                        "task_type": task_type,
                        "rows": int(len(df)) if not df.empty else 0,
                        "target": app_state.selected_target,
                        "next_step": "Connect model training or prediction function here.",
                    }
                )

            elif task_type == "Time Series":
                st.json(
                    {
                        "task_type": task_type,
                        "rows": int(len(df)) if not df.empty else 0,
                        "time_column": app_state.selected_time_column,
                        "target": app_state.selected_target,
                        "next_step": "Connect forecasting or anomaly detection function here.",
                    }
                )

            elif task_type == "NLP / Text":
                st.json(
                    {
                        "task_type": task_type,
                        "rows": int(len(df)) if not df.empty else 0,
                        "text_column": app_state.selected_text_column,
                        "label_column": app_state.selected_target,
                        "next_step": "Connect text preprocessing and model inference here.",
                    }
                )

        else:
            st.info("Adjust settings and click 'Run pipeline'.")

    else:
        # =============================================================================
        # Computer vision result workspace
        # =============================================================================
        with st.expander("Uploaded image preview", expanded=True):
            image_files = [
                f for f in uploaded_files
                if f.name.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".webp"))
            ]

            if not image_files:
                st.info("Upload image files to preview them here.")
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
                                st.warning(f"Could not open image: {exc}")
                        else:
                            st.caption("Pillow is not available in this environment.")

        with st.expander("Inference / training hooks", expanded=False):
            st.code(
                """
# Example wiring point
if run_clicked:
    # 1) Load image(s)
    # 2) Call your detector / classifier
    # 3) Convert outputs to DataFrame
    # 4) Show results in Streamlit
    pass
                """.strip(),
                language="python",
            )

        if run_clicked:
            st.success("UI run placeholder finished.")
            st.json(
                {
                    "task_type": task_type,
                    "uploaded_images": len(
                        [f for f in uploaded_files if f.name.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".webp"))]
                    ),
                    "cv_mode": app_state.selected_image_mode,
                    "next_step": "Connect this section to your CV inference or training script.",
                }
            )
        else:
            st.info("Upload images and click 'Run pipeline'.")


# =============================================================================
# Footer / developer notes
# =============================================================================
# This final block is intentionally educational.
st.markdown("---")
with st.expander("How to embed this UI into another project", expanded=False):
    st.markdown(
        """
1. **Copy the sidebar block** if you only need navigation and file upload.
2. **Copy a single task block** (`Tabular`, `Time Series`, `Computer Vision`, `NLP / Text`) into your script.
3. Replace the **placeholder run section** with calls to your own preprocessing / training / inference functions.
4. Keep the helper functions (`safe_read_table`, `build_demo_dataframe`, `render_info_cards`) if they are useful.
5. If you split your project into modules, move business logic into `src/...` and leave Streamlit for UI only.
        """
    )

st.caption("Template file: designed as a universal starting point for multiple task classes.")
