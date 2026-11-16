from pathlib import Path
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="Customer Churn | Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

is_dark = st.context.theme.type == "dark"
palette = {
    "ink": "#eaf0ff" if is_dark else "#17233b",
    "muted": "#9aa8c7" if is_dark else "#64748b",
    "panel": "#121c31" if is_dark else "#ffffff",
    "line": "rgba(157,177,218,.15)" if is_dark else "rgba(71,95,132,.18)",
    "app_background": "radial-gradient(ellipse at 15% 0%, #172d4d 0%, #0a1222 42%, #080e1b 100%)"
    if is_dark else "radial-gradient(ellipse at 15% 0%, #eef4ff 0%, #f8fafc 48%, #ffffff 100%)",
    "heading": "#f3f6ff" if is_dark else "#17233b",
    "sidebar": "linear-gradient(180deg,#101b30,#0b1425)" if is_dark else "linear-gradient(180deg,#f3f7ff,#eaf1fb)",
    "metric": "linear-gradient(145deg,rgba(25,42,69,.96),rgba(16,28,48,.96))"
    if is_dark else "linear-gradient(145deg,rgba(255,255,255,.98),rgba(240,246,255,.98))",
    "metric_label": "#9eacc8" if is_dark else "#64748b",
    "metric_value": "#f4f7ff" if is_dark else "#17233b",
    "panel_background": "linear-gradient(145deg,rgba(22,36,60,.92),rgba(14,25,43,.92))"
    if is_dark else "linear-gradient(145deg,rgba(255,255,255,.96),rgba(244,248,255,.96))",
    "hero_background": "linear-gradient(110deg,rgba(28,53,89,.95),rgba(18,31,53,.82))"
    if is_dark else "linear-gradient(110deg,rgba(232,241,255,.98),rgba(255,255,255,.9))",
    "hero_border": "rgba(137,164,224,.2)" if is_dark else "rgba(91,126,186,.25)",
    "hero_text": "#b5c2dd" if is_dark else "#526581",
    "insight_text": "#dce5fb" if is_dark else "#344766",
    "tab_background": "rgba(24,39,65,.8)" if is_dark else "rgba(226,235,249,.9)",
    "tab_active": "#263e68" if is_dark else "#d5e3f7",
}

# Keep the custom dashboard styling aligned with Streamlit's active appearance.
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
:root {{ --ink:{palette["ink"]}; --muted:{palette["muted"]}; --panel:{palette["panel"]}; --line:{palette["line"]}; }}
html, body, [class*="css"] {{ font-family:'DM Sans',sans-serif; }}
.stApp {{ background: {palette["app_background"]}; color:var(--ink); }}
.block-container {{ padding-top:1.6rem; padding-bottom:2.5rem; max-width:1500px; }}
h1,h2,h3 {{ font-family:'Space Grotesk',sans-serif !important; letter-spacing:-.035em; color:{palette["heading"]}; }}
[data-testid="stSidebar"] {{ background:{palette["sidebar"]}; border-right:1px solid var(--line); }}
[data-testid="stMetric"] {{ background:{palette["metric"]}; border:1px solid var(--line); padding:18px 20px; border-radius:16px; box-shadow:0 12px 32px rgba(0,0,0,.12); }}
[data-testid="stMetricLabel"] {{ color:{palette["metric_label"]} !important; font-size:.82rem; }}
[data-testid="stMetricValue"] {{ color:{palette["metric_value"]} !important; font-family:'Space Grotesk',sans-serif; }}
[data-testid="stMetricDelta"] {{ font-size:.78rem; }}
.panel {{ background:{palette["panel_background"]}; border:1px solid var(--line); border-radius:18px; padding:18px 20px; margin-bottom:12px; }}
.eyebrow {{ color:#7f9cff; text-transform:uppercase; letter-spacing:.16em; font-size:.72rem; font-weight:700; }}
.hero {{ background:{palette["hero_background"]}; border:1px solid {palette["hero_border"]}; border-radius:22px; padding:25px 28px; margin-bottom:22px; position:relative; overflow:hidden; }}
.hero:after {{ content:""; position:absolute; width:240px;height:240px;right:-55px;top:-110px;border-radius:50%;background:rgba(105,139,255,.13);filter:blur(2px); }}
.hero h1 {{ margin:.25rem 0 .35rem 0; font-size:2.2rem; }}
.hero p {{ color:{palette["hero_text"]}; margin:0; max-width:720px; }}
.insight {{ border-left:3px solid #7896ff; padding:9px 13px; margin:9px 0; background:rgba(113,143,255,.07); border-radius:0 10px 10px 0; color:{palette["insight_text"]}; }}
.small-note {{ color:{palette["muted"]}; font-size:.82rem; }}
div[data-testid="stDataFrame"] {{ border:1px solid var(--line); border-radius:12px; overflow:hidden; }}
.stTabs [data-baseweb="tab-list"] {{ gap:8px; }}
.stTabs [data-baseweb="tab"] {{ background:{palette["tab_background"]}; border-radius:10px 10px 0 0; padding:10px 16px; }}
.stTabs [aria-selected="true"] {{ background:{palette["tab_active"]} !important; }}
</style>
""", unsafe_allow_html=True)

PLOT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Sans", color=palette["insight_text"]),
    margin=dict(l=20, r=20, t=45, b=20),
    legend=dict(orientation="h", y=-0.22),
    xaxis=dict(gridcolor="rgba(160,180,220,.10)", zerolinecolor="rgba(160,180,220,.12)"),
    yaxis=dict(gridcolor="rgba(160,180,220,.10)", zerolinecolor="rgba(160,180,220,.12)"),
)
BLUE, CORAL, TEAL, GOLD = "#7896ff", "#ff8a78", "#45c9b0", "#f4c66a"

@st.cache_data(show_spinner=False)
def load_data(file):
    data = pd.read_csv(file)
    required = {"CreditScore", "Geography", "Gender", "Age", "Tenure", "Balance",
                "NumOfProducts", "HasCrCard", "IsActiveMember", "EstimatedSalary", "Exited"}
    missing = required - set(data.columns)
    if missing:
        raise ValueError(f"Dataset is missing required columns: {', '.join(sorted(missing))}")
    data = data.copy()
    for col in ["Geography", "Gender"]:
        data[col] = data[col].astype("string").str.strip()
    data["Exited"] = pd.to_numeric(data["Exited"], errors="coerce")
    data = data.dropna(subset=["Exited"])
    data["Exited"] = data["Exited"].astype(int)
    data["Churn Status"] = np.where(data["Exited"].eq(1), "Churned", "Stayed")
    data["Activity"] = np.where(data["IsActiveMember"].eq(1), "Active", "Inactive")
    data["Card"] = np.where(data["HasCrCard"].eq(1), "Has card", "No card")
    data["Age Group"] = pd.cut(
        data["Age"], bins=[17, 30, 40, 50, 60, 100],
        labels=["18–30", "31–40", "41–50", "51–60", "61+"], include_lowest=True
    )
    return data

def style_fig(fig, height=350):
    fig.update_layout(**PLOT, height=height)
    fig.update_xaxes(showline=False)
    fig.update_yaxes(showline=False)
    return fig

def pct(x):
    return f"{x:.1f}%"

# Sidebar: source and filters
st.sidebar.markdown("## 📊 Churn Analytics")
st.sidebar.caption("BANK CUSTOMER RETENTION")
default_file = Path(__file__).with_name("Churn_Modelling(1).csv")
uploaded = st.sidebar.file_uploader("Use a different CSV dataset", type=["csv"])
source = uploaded if uploaded is not None else (default_file if default_file.exists() else None)

if source is None:
    st.title("Bank Customer Churn Dashboard")
    st.info("Upload the bank churn CSV in the sidebar, or place `Churn_Modelling(1).csv` beside `app.py`.")
    st.stop()

try:
    raw = load_data(source)
except Exception as exc:
    st.error(f"Could not load this dataset: {exc}")
    st.stop()

st.sidebar.markdown("---")
st.sidebar.markdown("### Filter the analysis")
geographies = sorted(raw["Geography"].dropna().unique().tolist())
genders = sorted(raw["Gender"].dropna().unique().tolist())
selected_geo = st.sidebar.multiselect("Geography", geographies, default=geographies)
selected_gender = st.sidebar.multiselect("Gender", genders, default=genders)
age_min, age_max = int(raw["Age"].min()), int(raw["Age"].max())
age_range = st.sidebar.slider("Age range", age_min, age_max, (age_min, age_max))
activity = st.sidebar.multiselect("Membership", ["Active", "Inactive"], default=["Active", "Inactive"])
products = sorted(raw["NumOfProducts"].dropna().unique().tolist())
selected_products = st.sidebar.multiselect("Number of products", products, default=products)
status = st.sidebar.multiselect("Customer status", ["Stayed", "Churned"], default=["Stayed", "Churned"])

filtered = raw[
    raw["Geography"].isin(selected_geo)
    & raw["Gender"].isin(selected_gender)
    & raw["Age"].between(age_range[0], age_range[1])
    & raw["Activity"].isin(activity)
    & raw["NumOfProducts"].isin(selected_products)
    & raw["Churn Status"].isin(status)
].copy()

st.markdown("""
<div class="hero">
  <div class="eyebrow">Customer intelligence · Retention overview</div>
  <h1>Bank Customer Churn</h1>
  <p>Explore customer behavior, compare churn patterns and uncover the segments that deserve attention. Every metric and visualization responds to your filters.</p>
</div>
""", unsafe_allow_html=True)

if filtered.empty:
    st.warning("No customers match the selected filters. Adjust the filters in the sidebar.")
    st.stop()

n = len(filtered)
churn_n = int(filtered["Exited"].sum())
churn_rate = filtered["Exited"].mean() * 100
retention_rate = 100 - churn_rate
avg_age = filtered["Age"].mean()
avg_balance = filtered["Balance"].mean()
overall_rate = raw["Exited"].mean() * 100

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Customers in view", f"{n:,}", f"{n/raw.shape[0]*100:.1f}% of dataset")
k2.metric("Churn rate", pct(churn_rate), f"{churn_n:,} churned")
k3.metric("Retention rate", pct(retention_rate), "Stayed customers")
k4.metric("Average age", f"{avg_age:.1f} yrs")
k5.metric("Average balance", f"{avg_balance:,.0f}")

st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
overview, segments, customers, data_quality = st.tabs(["✦ Overview", "◈ Segment analysis", "⌕ Customer explorer", "▤ Data quality"])

with overview:
    left, right = st.columns([1.05, 1.35], gap="large")
    with left:
        st.markdown("#### Customer status")
        status_counts = filtered["Churn Status"].value_counts().reindex(["Stayed", "Churned"], fill_value=0).reset_index()
        status_counts.columns = ["Status", "Customers"]
        fig = px.pie(status_counts, names="Status", values="Customers", hole=.68,
                     color="Status", color_discrete_map={"Stayed": TEAL, "Churned": CORAL})
        fig.update_traces(textposition="outside", textinfo="percent+label", marker=dict(line=dict(color="#101a2c", width=3)))
        fig.add_annotation(text=f"<b>{churn_rate:.1f}%</b><br><span style='font-size:11px'>CHURN</span>",
                           x=.5, y=.5, showarrow=False, font=dict(size=22, color="#f3f6ff"))
        st.plotly_chart(style_fig(fig, 340), use_container_width=True)
    with right:
        st.markdown("#### Churn by customer age")
        age_df = filtered.groupby("Age Group", observed=False).agg(Customers=("Exited", "size"), Churned=("Exited", "sum")).reset_index()
        age_df["Churn rate"] = np.where(age_df["Customers"] > 0, age_df["Churned"] / age_df["Customers"] * 100, 0)
        fig = px.bar(age_df, x="Age Group", y="Churn rate", text=age_df["Churn rate"].map(lambda x: f"{x:.1f}%"),
                     color="Churn rate", color_continuous_scale=["#4ac9b0", "#7896ff", "#ff8a78"],
                     hover_data={"Customers": True, "Churned": True, "Churn rate": ":.1f"})
        fig.update_traces(textposition="outside", cliponaxis=False)
        fig.update_layout(coloraxis_showscale=False, yaxis_title="Churn rate (%)", xaxis_title="")
        st.plotly_chart(style_fig(fig, 340), use_container_width=True)

    c1, c2 = st.columns(2, gap="large")
    with c1:
        st.markdown("#### Geography mix and churn")
        geo = filtered.groupby("Geography").agg(Customers=("Exited", "size"), Churned=("Exited", "sum")).reset_index()
        geo["Churn rate"] = geo["Churned"] / geo["Customers"] * 100
        fig = px.bar(geo, x="Geography", y=["Customers", "Churned"], barmode="group",
                     color_discrete_sequence=[BLUE, CORAL], labels={"value":"Customers", "variable":"Group"})
        st.plotly_chart(style_fig(fig, 330), use_container_width=True)
    with c2:
        st.markdown("#### Age and balance by status")
        fig = px.scatter(filtered, x="Age", y="Balance", color="Churn Status",
                         color_discrete_map={"Stayed": TEAL, "Churned": CORAL},
                         opacity=.55, hover_data=["Geography", "Gender", "NumOfProducts"])
        st.plotly_chart(style_fig(fig, 330), use_container_width=True)

    st.markdown("#### What stands out in this selection?")
    seg_geo = filtered.groupby("Geography")["Exited"].mean().mul(100).dropna()
    seg_activity = filtered.groupby("Activity")["Exited"].mean().mul(100).dropna()
    seg_gender = filtered.groupby("Gender")["Exited"].mean().mul(100).dropna()
    seg_products = filtered.groupby("NumOfProducts")["Exited"].mean().mul(100).dropna()
    insights = [
        f"The selected customer group has a churn rate of **{churn_rate:.1f}%**, compared with **{overall_rate:.1f}%** across the full uploaded dataset.",
        f"Customers who churn are **{filtered.loc[filtered.Exited.eq(1), 'Age'].median():.0f}** years old at the median, versus **{filtered.loc[filtered.Exited.eq(0), 'Age'].median():.0f}** for customers who stay." if churn_n and (filtered.Exited.eq(0).any()) else "Not enough customers in both status groups to compare median age.",
    ]
    if not seg_geo.empty:
        insights.append(f"Among selected geographies, **{seg_geo.idxmax()}** has the highest churn rate (**{seg_geo.max():.1f}%**).")
    if not seg_activity.empty and set(seg_activity.index) == {"Active", "Inactive"}:
        insights.append(f"Inactive customers churn at **{seg_activity['Inactive']:.1f}%**, compared with **{seg_activity['Active']:.1f}%** for active customers.")
    if not seg_products.empty:
        insights.append(f"The highest product-count churn rate in this selection is for **{seg_products.idxmax()} product(s)** (**{seg_products.max():.1f}%**).")
    for item in insights:
        st.markdown(f"<div class='insight'>✦ {item}</div>", unsafe_allow_html=True)

with segments:
    st.markdown("#### Compare churn across customer segments")
    dimension = st.selectbox("Choose a segment", ["Geography", "Gender", "NumOfProducts", "Tenure", "Activity", "Card", "Age Group"])
    grouped = filtered.groupby(dimension, observed=False).agg(
        Customers=("Exited", "size"), Churned=("Exited", "sum"),
        Avg_Age=("Age", "mean"), Avg_Balance=("Balance", "mean")
    ).reset_index()
    grouped["Churn rate"] = grouped["Churned"] / grouped["Customers"] * 100
    a, b = st.columns([1.15, 1], gap="large")
    with a:
        fig = px.bar(grouped, x=dimension, y="Churn rate", color="Churn rate",
                     color_continuous_scale=["#45c9b0", "#7896ff", "#ff8a78"],
                     text=grouped["Churn rate"].map(lambda x:f"{x:.1f}%"),
                     hover_data=["Customers", "Churned", "Avg_Age", "Avg_Balance"])
        fig.update_traces(textposition="outside", cliponaxis=False)
        fig.update_layout(coloraxis_showscale=False, yaxis_title="Churn rate (%)")
        st.plotly_chart(style_fig(fig, 390), use_container_width=True)
    with b:
        fig = px.bar(grouped, x=dimension, y="Customers", color="Customers",
                     color_continuous_scale=["#263f69", BLUE], text="Customers")
        fig.update_traces(textposition="outside")
        fig.update_layout(coloraxis_showscale=False, yaxis_title="Number of customers")
        st.plotly_chart(style_fig(fig, 390), use_container_width=True)
    st.dataframe(grouped.rename(columns={"Avg_Age":"Average age", "Avg_Balance":"Average balance"}).style.format({
        "Churn rate":"{:.1f}%", "Average age":"{:.1f}", "Average balance":"{:,.2f}"
    }), use_container_width=True, hide_index=True)

    st.markdown("#### Numeric relationship explorer")
    x_col = st.selectbox("X-axis", ["Age", "CreditScore", "Tenure", "Balance", "EstimatedSalary"])
    y_col = st.selectbox("Y-axis", ["Balance", "Age", "CreditScore", "Tenure", "EstimatedSalary"], index=0)
    fig = px.scatter(filtered, x=x_col, y=y_col, color="Churn Status",
                     color_discrete_map={"Stayed": TEAL, "Churned": CORAL},
                     opacity=.55, hover_data=["Geography", "Gender", "NumOfProducts"])
    st.plotly_chart(style_fig(fig, 430), use_container_width=True)

with customers:
    st.markdown("#### Search and inspect customer records")
    search = st.text_input("Search visible records", placeholder="Search geography, gender, surname or customer ID…")
    table = filtered.copy()
    if search.strip():
        searchable = [c for c in ["Surname", "CustomerId", "Geography", "Gender", "Churn Status"] if c in table.columns]
        mask = pd.Series(False, index=table.index)
        for col in searchable:
            mask |= table[col].astype(str).str.contains(search.strip(), case=False, na=False)
        table = table[mask]
    display_cols = [c for c in ["CustomerId", "Surname", "Geography", "Gender", "Age", "CreditScore",
                                 "Tenure", "Balance", "NumOfProducts", "IsActiveMember", "HasCrCard",
                                 "EstimatedSalary", "Churn Status"] if c in table.columns]
    st.caption(f"{len(table):,} matching records · {len(filtered):,} records after filters")
    st.dataframe(table[display_cols], use_container_width=True, hide_index=True, height=460)
    csv_bytes = table[display_cols].to_csv(index=False).encode("utf-8")
    st.download_button("⬇ Download displayed records (CSV)", csv_bytes, "filtered_customer_churn.csv", "text/csv")

with data_quality:
    st.markdown("#### Dataset health check")
    q1, q2, q3, q4 = st.columns(4)
    q1.metric("Rows", f"{len(raw):,}")
    q2.metric("Columns", f"{raw.shape[1]}")
    q3.metric("Missing cells", f"{int(raw.isna().sum().sum()):,}")
    q4.metric("Duplicate rows", f"{int(raw.duplicated().sum()):,}")
    quality = pd.DataFrame({
        "Column": raw.columns,
        "Data type": [str(x) for x in raw.dtypes],
        "Missing": [int(raw[c].isna().sum()) for c in raw.columns],
        "Unique values": [int(raw[c].nunique(dropna=True)) for c in raw.columns],
    })
    st.dataframe(quality, use_container_width=True, hide_index=True)
    st.markdown("<div class='insight'>The supplied EDA reports 10,000 records, 14 columns, no missing values, no duplicate rows, and no duplicated CustomerId values. The table above is recalculated from the loaded file.</div>", unsafe_allow_html=True)
    st.markdown("#### Correlation with churn")
    numeric = raw.select_dtypes(include=np.number)
    corr = numeric.corr(numeric_only=True)
    if "Exited" in corr:
        corr_target = corr[["Exited"]].drop(index=["Exited"]).sort_values("Exited")
        fig = px.bar(corr_target.reset_index(), x="Exited", y="index", orientation="h",
                     color="Exited", color_continuous_scale=["#ff8a78", "#7896ff"])
        fig.update_layout(coloraxis_showscale=False, xaxis_title="Pearson correlation", yaxis_title="")
        st.plotly_chart(style_fig(fig, 430), use_container_width=True)

st.markdown("---")
st.markdown("<div class='small-note'>Built by Yosr Elnoby </div>", unsafe_allow_html=True)
