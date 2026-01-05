import streamlit as st
import pandas as pd

st.set_page_config(page_title="Excel Dashboard", layout="wide")

@st.cache_data
def load_data():
    return pd.read_excel(
        "grading_data.xlsx",
        engine="openpyxl"
    )
df = load_data()

st.title("Web-Based Dashboard")
st.markdown("Hosted dashboard generated from Excel")

st.sidebar.header("Filters")

text_columns = df.select_dtypes(include="object").columns
filtered_df = df.copy()

for col in text_columns:
    options = st.sidebar.multiselect(
        f"Select {col}",
        sorted(df[col].dropna().unique())
    )
    if options:
        filtered_df = filtered_df[filtered_df[col].isin(options)]

st.subheader("Key Metrics")
num_cols = filtered_df.select_dtypes(include="number").columns

cols = st.columns(len(num_cols))
for i, col in enumerate(num_cols):
    cols[i].metric(col, round(filtered_df[col].mean(), 2))

st.subheader("Data Table")
st.dataframe(filtered_df, use_container_width=True)

st.subheader("Charts")
for col in num_cols:
    st.bar_chart(filtered_df[col])

