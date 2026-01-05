
# app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Noah Weekly Grades — Web Dashboard", layout="wide")

# ----------- Data loading helpers -----------
@st.cache_data
def load_excel(path: str, sheet: str = "Weekly Changes"):
    """Load the Excel sheet reliably. Requires openpyxl for .xlsx."""
    try:
        return pd.read_excel(path, sheet_name=sheet, engine="openpyxl")
    except ImportError:
        st.error(
            "Missing dependency: `openpyxl`. "
            "Add `openpyxl>=3.1` to requirements.txt and redeploy."
        )
        st.stop()
    except FileNotFoundError:
        st.error(f"File not found: {path}. Upload a file or fix the path.")
        st.stop()
    except Exception as e:
        st.error(f"Failed to read Excel: {e}")
        st.stop()

# ----------- Ingest: Upload or local file -----------
st.title("Noah Weekly Grades — Dashboard")

uploaded = st.file_uploader("Upload the .xlsx file with a 'Weekly Changes' sheet", type=["xlsx"])

if uploaded:
    df = pd.read_excel(uploaded, sheet_name="Weekly Changes", engine="openpyxl")
else:
    # Fallback to a repo/working-dir file name (adjust as needed)
    df = load_excel("grading_data.xlsx", sheet="Weekly Changes")

# ----------- Clean & prepare -----------
df.columns = [c.strip() for c in df.columns]

# Required columns check
required_cols = {"Week", "Class", "Weighted Grade", "GPA"}
missing = required_cols - set(df.columns)
if missing:
    st.error(
        "Your 'Weekly Changes' sheet is missing required columns: "
        + ", ".join(sorted(missing))
    )
    st.stop()

df["Week"] = pd.to_datetime(df["Week"], errors="coerce")
df = df.dropna(subset=["Week"]).sort_values("Week")

if df.empty:
    st.warning("No valid rows after parsing 'Week'. Please verify your data.")
    st.stop()

# Latest-week slice
latest_week = df["Week"].max()
latest_df = df[df["Week"] == latest_week].copy()

if latest_df.empty:
    st.warning(
        "No rows for the latest week. Check that 'Weekly Changes' contains rows for "
        f"{latest_week.date()}."
    )
    st.stop()

st.caption(f"Latest update: {latest_week.date()}")

# ----------- KPI grid (safe dynamic columns) -----------
kpi_cols_present = {"Δ Weighted Grade", "Δ GPA"} <= set(df.columns)

classes = latest_df["Class"].tolist()
n_cols = int(max(1, min(6, len(classes))))  # cap for readability
cols = st.columns(n_cols)

for i, (_, row) in enumerate(latest_df.iterrows()):
    with cols[i % n_cols]:
        st.subheader(row["Class"])

        # Weighted metric
        delta_w = None
        if kpi_cols_present and pd.notna(row.get("Δ Weighted Grade")):
            delta_w = f"{row.get('Δ Weighted Grade'):+.3f}"
        st.metric("Weighted", f"{row['Weighted Grade']:.3f}", delta_w)

        # GPA metric
        delta_g = None
        if kpi_cols_present and pd.notna(row.get("Δ GPA")):
            delta_g = f"{row.get('Δ GPA'):+.3f}"
        st.metric("GPA", f"{row['GPA']:.3f}", delta_g)

# ----------- Trend charts -----------
st.divider()
st.subheader("Trend — Weighted Grade")

weighted_pivot = df.pivot_table(
    index="Week", columns="Class", values="Weighted Grade", aggfunc="first"
)

fig1, ax1 = plt.subplots(figsize=(9, 4))
for c in weighted_pivot.columns:
    ax1.plot(weighted_pivot.index, weighted_pivot[c], marker="o", label=c)
ax1.set_ylabel("Weighted Grade")
ax1.grid(True)
ax1.legend(ncol=2)
st.pyplot(fig1)

st.subheader("Trend — GPA")
gpa_pivot = df.pivot_table(index="Week", columns="Class", values="GPA", aggfunc="first")

fig2, ax2 = plt.subplots(figsize=(9, 4))
for c in gpa_pivot.columns:
    ax2.plot(gpa_pivot.index, gpa_pivot[c], marker="o", label=c)
ax2.set_ylim(0, 4.2)
ax2.set_ylabel("GPA")
ax2.grid(True)
ax2.legend(ncol=2)
st.pyplot(fig2)

# ----------- Latest-week table -----------
st.subheader("Data (Latest Week)")
display_cols = ["Class", "Weighted Grade", "GPA"]
if kpi_cols_present:
    display_cols += ["Δ Weighted Grade", "Δ GPA"]
st.dataframe(latest_df[display_cols], use_container_width=True)

# ----------- Diagnostics (optional) -----------
with st.expander("Environment info"):
    st.write({"rows_total": int(len(df)), "classes": classes})
    try:
        import openpyxl  # noqa
        st.caption("openpyxl installed")
    except ImportError:
        st.caption("openpyxl NOT installed")
    st.caption(f"pandas {pd.__version__}")


