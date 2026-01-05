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


# Make exactly 3 columns regardless
cols = st.columns(3)

for i, (_, row) in enumerate(latest_df.iterrows()):
    with cols[i % 3]:
        st.subheader(row["Class"])
        st.metric("Weighted", f"{row['Weighted Grade']:.3f}",
                  None if pd.isna(row["Δ Weighted Grade"]) else f"{row['Δ Weighted Grade']:+.3f}")
        st.metric("GPA", f"{row['GPA']:.3f}",
                  None if pd.isna(row["Δ GPA"]) else f"{row['Δ GPA']:+.3f}")

# ---- KPI grid (safe, dynamic columns) ----
if latest_df.empty:
    st.warning("No rows found for the latest week. Verify the 'Weekly Changes' sheet.")
    st.stop()

classes = latest_df["Class"].tolist()
n_cols = int(max(1, min(6, len(classes))))  # cap columns for readability

cols = st.columns(n_cols)

for i, (_, row) in enumerate(latest_df.iterrows()):
    with cols[i % n_cols]:
        st.subheader(row["Class"])
        st.metric(
            "Weighted",
            f"{row['Weighted Grade']:.3f}",
            None if pd.isna(row["Δ Weighted Grade"]) else f"{row['Δ Weighted Grade']:+.3f}",
        )
        st.metric(
            "GPA",
            f"{row['GPA']:.3f}",
            None if pd.isna(row["Δ GPA"]) else f"{row['Δ GPA']:+.3f}",
        )

