import streamlit as st
import pandas as pd
from pathlib import Path

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Used Car Listings Dashboard",
    page_icon="🚗",
    layout="wide"
)

# --- DATA LOADING ---
@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    return df

st.title("🚗 Used Car Listings — Cleaned Data Dashboard")
st.caption("Powered by the Polars ETL pipeline (fingerprint matching, price & mileage quality gates)")

# Resolve relative to this script's location, not the terminal's working
# directory — Streamlit's CWD depends on where `streamlit run` was launched
# from, which is unreliable to assume.
DEFAULT_DATA_PATH = str(Path(__file__).parent.parent / "clean_car_listings.csv")

DATA_PATH = st.sidebar.text_input(
    "Path to cleaned CSV",
    value=DEFAULT_DATA_PATH
)

if not Path(DATA_PATH).exists():
    st.error(f"File not found: {DATA_PATH}. Run the pipeline first, or fix the path in the sidebar.")
    st.stop()

df = load_data(DATA_PATH)

# --- SIDEBAR FILTERS ---
st.sidebar.header("Filters")

search_term = st.sidebar.text_input("Search model name", value="")

min_price, max_price = int(df["avg_price"].min()), int(df["avg_price"].max())
price_range = st.sidebar.slider(
    "Average price range (₱)",
    min_value=min_price, max_value=max_price,
    value=(min_price, max_price)
)

min_mileage, max_mileage = int(df["avg_mileage"].min()), int(df["avg_mileage"].max())
mileage_range = st.sidebar.slider(
    "Average mileage range (km)",
    min_value=min_mileage, max_value=max_mileage,
    value=(min_mileage, max_mileage)
)

# --- APPLY FILTERS ---
filtered = df[
    (df["avg_price"].between(*price_range)) &
    (df["avg_mileage"].between(*mileage_range))
]

if search_term:
    filtered = filtered[filtered["display_title"].str.contains(search_term, case=False, na=False)]

# --- KPI ROW ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Unique Models", f"{len(filtered):,}")
col2.metric("Total Listings", f"{int(filtered['occurrence_count'].sum()):,}")
col3.metric("Avg Price", f"₱{filtered['avg_price'].mean():,.0f}" if len(filtered) else "—")
col4.metric("Avg Mileage", f"{filtered['avg_mileage'].mean():,.0f} km" if len(filtered) else "—")

st.divider()

# --- CHARTS ---
left, right = st.columns(2)

with left:
    st.subheader("Top 15 Models by Listing Count")
    top15 = filtered.sort_values("occurrence_count", ascending=False).head(15)
    st.bar_chart(top15.set_index("display_title")["occurrence_count"])

with right:
    st.subheader("Price vs. Mileage")
    st.scatter_chart(
        filtered,
        x="avg_mileage",
        y="avg_price",
        size="occurrence_count",
        color=None
    )

st.divider()

# --- DATA TABLE ---
st.subheader("Cleaned Listings Table")
st.dataframe(
    filtered.sort_values("occurrence_count", ascending=False),
    use_container_width=True,
    hide_index=True
)

st.caption(f"Showing {len(filtered):,} of {len(df):,} unique models after filters.")