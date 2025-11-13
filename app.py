import streamlit as st
try:
    from streamlit.runtime.scriptrunner import get_script_run_ctx
except Exception:
    get_script_run_ctx = None
if get_script_run_ctx is None or get_script_run_ctx() is None:
    import sys
    print("请使用命令运行：streamlit run d:/Code/app.py")
    raise SystemExit(0)
import pandas as pd
import altair as alt

st.set_page_config(page_title="CSV Explorer", layout="wide")
st.title("CSV Explorer")
st.markdown(
    """
    <style>
    :root { --card-radius: 0.5rem; }
    div[data-testid="stFileUploader"] { border: 1px solid #e5e7eb; border-radius: var(--card-radius); padding: 0.5rem; }
    div[data-testid="stDataFrame"] { border-radius: var(--card-radius); overflow: hidden; }
    div[data-testid="stMetric"] { background: #fafafa; padding: 0.5rem; border-radius: var(--card-radius); }
    .stSelectbox, .stTextInput { border-radius: var(--card-radius) !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

uploaded = st.file_uploader("Upload a CSV file", type=["csv"]) 
opts_col1, opts_col2 = st.columns(2)
has_header = opts_col1.checkbox("File has header row", value=True)
delimiter = opts_col2.text_input("Delimiter (blank=auto)", "")

if uploaded:
    sep_val = None if delimiter.strip() == "" else delimiter
    header_val = 0 if has_header else None
    df = pd.read_csv(uploaded, sep=sep_val, engine="python", header=header_val)
    df.columns = [c.strip() for c in df.columns]

    st.subheader("Overview")
    col1, col2, col3 = st.columns(3)
    col1.metric("Rows", len(df))
    col2.metric("Columns", df.shape[1])
    col3.metric("Duplicates", int(df.duplicated().sum()))

    st.subheader("Data Types")
    st.dataframe(pd.DataFrame(df.dtypes, columns=["dtype"]))

    st.subheader("Missing Values")
    miss = df.isna().sum().rename("missing").to_frame()
    miss["missing_pct"] = (miss["missing"] / len(df)).round(4)
    st.dataframe(miss)

    st.subheader("Preview")
    st.dataframe(df.head(20))

    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    all_cols = df.columns.tolist()
    st.subheader("Chart")
    if len(numeric_cols) >= 1:
        c1, c2, c3 = st.columns(3)
        x = c1.selectbox("X axis", options=all_cols, index=0)
        y = c2.selectbox("Y axis", options=numeric_cols, index=0)
        chart_type = c3.selectbox("Chart type", options=["Line", "Bar"], index=0)
        data = df.copy()
        if pd.api.types.is_datetime64_any_dtype(data[x]) is False:
            try:
                data[x] = pd.to_datetime(data[x], errors="ignore")
            except Exception:
                pass
        base = alt.Chart(data).mark_line() if chart_type == "Line" else alt.Chart(data).mark_bar()
        chart = base.encode(x=alt.X(x, title=x), y=alt.Y(y, title=y), tooltip=[x, y]).properties(height=400)
        st.altair_chart(chart, use_container_width=True)
    else:
        st.info("No numeric columns found for charting.")

    st.subheader("Summary Statistics")
    st.dataframe(df.describe(include="all"))
else:
    st.info("Upload a CSV to see statistics and charts.")
