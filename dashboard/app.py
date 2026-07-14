import streamlit as st
import pandas as pd
import altair as alt
from pathlib import Path

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Used Car Listings Dashboard",
    page_icon="🚗",
    layout="wide"
)

# --- KNOWN BRANDS (mirrors generate_data.py so extraction stays consistent) ---
KNOWN_BRANDS = [
    "Toyota", "Honda", "Mitsubishi", "Nissan", "Ford",
    "Hyundai", "Kia", "Suzuki", "Mazda", "Chevrolet",
    "Isuzu", "MG", "Geely", "Foton"
]

def extract_brand(title: str) -> str:
    """Finds the first known brand name that appears in the display title."""
    title_lower = str(title).lower()
    for brand in KNOWN_BRANDS:
        if brand.lower() in title_lower:
            return brand
    return "Other"

# --- PRICE TIERS (PHP, tuned to this dataset's ₱150k-2M generation range) ---
PRICE_TIER_BINS = [0, 300_000, 700_000, 1_200_000, float("inf")]
PRICE_TIER_LABELS = ["Budget (<₱300k)", "Mid-Range (₱300k-700k)", "Premium (₱700k-1.2M)", "Luxury (>₱1.2M)"]

# --- DATA LOADING ---
@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["brand"] = df["display_title"].apply(extract_brand)
    df["price_per_km"] = (df["avg_price"] / df["avg_mileage"]).round(2)
    df["price_tier"] = pd.cut(
        df["avg_price"],
        bins=PRICE_TIER_BINS,
        labels=PRICE_TIER_LABELS
    )
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

brand_options = sorted(df["brand"].unique())
selected_brands = st.sidebar.multiselect("Brand", options=brand_options, default=brand_options)

tier_options = [t for t in PRICE_TIER_LABELS if t in df["price_tier"].unique()]
selected_tiers = st.sidebar.multiselect("Price Tier", options=tier_options, default=tier_options)

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
    (df["brand"].isin(selected_brands)) &
    (df["price_tier"].isin(selected_tiers)) &
    (df["avg_price"].between(*price_range)) &
    (df["avg_mileage"].between(*mileage_range))
]

if search_term:
    filtered = filtered[filtered["display_title"].str.contains(search_term, case=False, na=False)]

# --- KPI ROW ---
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Unique Models", f"{len(filtered):,}")
col2.metric("Total Listings", f"{int(filtered['occurrence_count'].sum()):,}")
col3.metric("Avg Price", f"₱{filtered['avg_price'].mean():,.0f}" if len(filtered) else "—")
col4.metric("Avg Mileage", f"{filtered['avg_mileage'].mean():,.0f} km" if len(filtered) else "—")
col5.metric("Avg Price/km", f"₱{filtered['price_per_km'].mean():,.2f}" if len(filtered) else "—")

st.divider()

# --- TOP MODELS & PRICE VS MILEAGE ---
left, right = st.columns(2)

with left:
    st.subheader("Top 15 Models by Listing Count")
    top15 = filtered.sort_values("occurrence_count", ascending=False).head(15)
    st.bar_chart(top15.set_index("display_title")["occurrence_count"])

with right:
    st.subheader("Price vs. Mileage (by Brand)")
    st.scatter_chart(
        filtered,
        x="avg_mileage",
        y="avg_price",
        size="occurrence_count",
        color="brand"
    )

st.divider()

# --- BRAND BREAKDOWN ---
st.subheader("Brand Breakdown")
brand_col1, brand_col2 = st.columns(2)

brand_listings = (
    filtered.groupby("brand", as_index=False)["occurrence_count"]
    .sum()
    .sort_values("occurrence_count", ascending=False)
)
brand_avg_price = (
    filtered.groupby("brand", as_index=False)["avg_price"]
    .mean()
    .sort_values("avg_price", ascending=False)
)

with brand_col1:
    st.caption("Total listings per brand")
    st.bar_chart(brand_listings.set_index("brand")["occurrence_count"])

with brand_col2:
    st.caption("Average price per brand (₱)")
    st.bar_chart(brand_avg_price.set_index("brand")["avg_price"])

st.divider()

# --- PRICE EFFICIENCY (PRICE PER KM) ---
st.subheader("Price Efficiency (₱ per km driven)")
eff_col1, eff_col2 = st.columns(2)

with eff_col1:
    st.caption("Distribution of price-per-km across models")
    hist = (
        alt.Chart(filtered)
        .mark_bar()
        .encode(
            x=alt.X("price_per_km:Q", bin=alt.Bin(maxbins=30), title="Price per km (₱)"),
            y=alt.Y("count()", title="Number of models"),
            tooltip=["count()"]
        )
        .properties(height=350)
    )
    st.altair_chart(hist, use_container_width=True)

with eff_col2:
    st.caption("Price distribution by brand (box plot)")
    box = (
        alt.Chart(filtered)
        .mark_boxplot(extent="min-max")
        .encode(
            x=alt.X("brand:N", title="Brand"),
            y=alt.Y("avg_price:Q", title="Average Price (₱)"),
            color=alt.Color("brand:N", legend=None)
        )
        .properties(height=350)
    )
    st.altair_chart(box, use_container_width=True)

st.divider()

# --- PRICE TIER BREAKDOWN ---
st.subheader("Price Tier Breakdown")
tier_col1, tier_col2 = st.columns(2)

tier_counts = (
    filtered.groupby("price_tier", as_index=False, observed=True)["display_title"]
    .count()
    .rename(columns={"display_title": "model_count"})
)

with tier_col1:
    st.caption("Number of models per price tier")
    tier_count_chart = (
        alt.Chart(tier_counts)
        .mark_bar()
        .encode(
            x=alt.X("price_tier:N", sort=PRICE_TIER_LABELS, title="Price Tier"),
            y=alt.Y("model_count:Q", title="Number of models"),
            color=alt.Color("price_tier:N", legend=None),
            tooltip=["price_tier", "model_count"]
        )
        .properties(height=350)
    )
    st.altair_chart(tier_count_chart, use_container_width=True)

with tier_col2:
    st.caption("Brand mix within each price tier")
    tier_brand_counts = (
        filtered.groupby(["price_tier", "brand"], as_index=False, observed=True)["occurrence_count"]
        .sum()
    )
    stacked_chart = (
        alt.Chart(tier_brand_counts)
        .mark_bar()
        .encode(
            x=alt.X("price_tier:N", sort=PRICE_TIER_LABELS, title="Price Tier"),
            y=alt.Y("occurrence_count:Q", title="Total Listings"),
            color=alt.Color("brand:N", title="Brand"),
            tooltip=["price_tier", "brand", "occurrence_count"]
        )
        .properties(height=350)
    )
    st.altair_chart(stacked_chart, use_container_width=True)

st.divider()

# --- BEST VALUE LISTINGS ---
st.subheader("💰 Best Value Models (Lowest ₱/km, min. 3 listings)")
best_value = (
    filtered[filtered["occurrence_count"] >= 3]
    .sort_values("price_per_km", ascending=True)
    .head(10)
)
if len(best_value):
    st.dataframe(
        best_value[["display_title", "brand", "price_tier", "avg_price", "avg_mileage", "price_per_km", "occurrence_count"]],
        use_container_width=True,
        hide_index=True
    )
else:
    st.info("No models with 3+ listings in the current filter selection.")

st.divider()

# --- DATA TABLE ---
st.subheader("Cleaned Listings Table")
st.dataframe(
    filtered.sort_values("occurrence_count", ascending=False),
    use_container_width=True,
    hide_index=True
)

st.download_button(
    label="⬇️ Download filtered data as CSV",
    data=filtered.to_csv(index=False).encode("utf-8"),
    file_name="filtered_car_listings.csv",
    mime="text/csv"
)

st.caption(f"Showing {len(filtered):,} of {len(df):,} unique models after filters.")