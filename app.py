import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# ==================== PAGE CONFIG ====================
st.set_page_config(
    page_title="A-Share Industry Analysis",
    page_icon="📊",
    layout="wide"
)

st.title("📊 A-Share Industry Valuation & Profitability Dashboard")
st.markdown("""
This interactive tool analyzes Chinese A-share industries across key dimensions:  
**Valuation (PE, PB)** and **Profitability (ROE, ROA)**.
""")

# ==================== SIDEBAR ====================
st.sidebar.header("🎛️ Filters & View")

view_mode = st.sidebar.radio(
    "Select View",
    ["PE vs ROE (Valuation & Profitability)", "PB vs ROA (Asset Efficiency)"]
)

st.sidebar.markdown("---")
st.sidebar.subheader("📊 Data Filters")

# 放宽默认值，避免空结果
min_roe = st.sidebar.slider("Minimum ROE (%)", -20.0, 50.0, 0.0, 0.5)
max_pe = st.sidebar.slider("Maximum PE Ratio", 0, 300, 150, 5)
min_companies = st.sidebar.slider("Min Companies per Industry", 1, 15, 3)

st.sidebar.markdown("---")
st.sidebar.markdown("*Data: WRDS Compustat Global*")
st.sidebar.markdown("*ACC102 Mini Assignment*")

# ==================== DATA LOADING ====================
@st.cache_data
def load_data():
    df = pd.read_csv('a_share_final.csv')
    df['market_cap_mil'] = df['market_cap'] / 1e6
    df['PB'] = df['market_cap_mil'] / df['ceq']
    df['ROA'] = df['ibc'] / (df['ceq'] * 2) * 100
    df = df[(df['PB'] > 0) & (df['PB'] < 50)]
    return df

df = load_data()
df_filtered = df[(df['roe'] >= min_roe) & (df['pe'] <= max_pe)]

industry_stats = df_filtered.groupby('sich').agg({
    'roe': 'median',
    'pe': 'median',
    'PB': 'median',
    'ROA': 'median',
    'conm': 'count',
    'market_cap': 'sum'
}).rename(columns={'conm': 'Company Count', 'market_cap': 'Total Market Cap'}).reset_index()

industry_stats = industry_stats[industry_stats['Company Count'] >= min_companies]

# 衍生指标（仅当有数据时计算）
if not industry_stats.empty:
    industry_stats['PEG Proxy'] = industry_stats['pe'] / industry_stats['roe']
    industry_stats['Log Market Cap'] = np.log10(industry_stats['Total Market Cap'])

# ==================== KPI CARDS ====================
st.markdown("### 📈 Market Snapshot")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Companies Analyzed", f"{len(df_filtered):,}")
with col2:
    st.metric("Industries Covered", len(industry_stats))
with col3:
    st.metric("Median ROE", f"{df_filtered['roe'].median():.1f}%" if not df_filtered.empty else "N/A")
with col4:
    st.metric("Median PE", f"{df_filtered['pe'].median():.1f}" if not df_filtered.empty else "N/A")

st.markdown("---")

# ==================== MAIN CHART ====================
st.subheader(f"📊 {view_mode}")

if industry_stats.empty:
    st.warning("⚠️ No industries match the current filters. Please relax the criteria in the sidebar.")
else:
    if view_mode == "PE vs ROE (Valuation & Profitability)":
        x_axis, y_axis = 'pe', 'roe'
        x_label, y_label = 'P/E Ratio (Median)', 'ROE % (Median)'
        color_by, color_label = 'PEG Proxy', 'PE/ROE'
        color_scale = 'RdYlGn_r'
    else:
        x_axis, y_axis = 'PB', 'ROA'
        x_label, y_label = 'P/B Ratio (Median)', 'ROA % (Median)'
        color_by, color_label = 'roe', 'ROE %'
        color_scale = 'Blues'

    fig = px.scatter(
        industry_stats,
        x=x_axis,
        y=y_axis,
        size='Company Count',
        color=color_by,
        color_continuous_scale=color_scale,
        hover_data=['sich', 'pe', 'roe', 'PB', 'ROA', 'Company Count'],
        labels={
            x_axis: x_label,
            y_axis: y_label,
            color_by: color_label,
            'Company Count': 'Number of Companies'
        },
        height=550
    )
    if view_mode == "PE vs ROE (Valuation & Profitability)":
        fig.add_hline(y=10, line_dash="dash", line_color="green", annotation_text="ROE=10%")
        fig.add_vline(x=30, line_dash="dash", line_color="red", annotation_text="PE=30")
    fig.update_layout(template="plotly_white", hovermode='closest', coloraxis_colorbar=dict(title=color_label))
    st.plotly_chart(fig, use_container_width=True)

# ==================== DATA TABLE ====================
st.markdown("---")
st.subheader("📋 Industry Metrics Table")

if not industry_stats.empty:
    sort_col = st.selectbox(
        "Sort by:",
        ['roe', 'pe', 'PB', 'ROA', 'Company Count', 'Total Market Cap']
    )
    st.dataframe(
        industry_stats[['sich', 'roe', 'pe', 'PB', 'ROA', 'Company Count', 'Total Market Cap']]
        .sort_values(sort_col, ascending=False)
        .style.format({
            'roe': '{:.2f}',
            'pe': '{:.2f}',
            'PB': '{:.2f}',
            'ROA': '{:.2f}',
            'Total Market Cap': '{:,.0f}'
        })
        .background_gradient(subset=['roe', 'ROA'], cmap='Greens')
        .background_gradient(subset=['pe', 'PB'], cmap='Reds_r'),
        use_container_width=True,
        height=400
    )
else:
    st.info("No data to display. Adjust filters to see industry metrics.")

# ==================== CORRELATION HEATMAP ====================
st.markdown("---")
st.subheader("📈 Correlation Heatmap")

if not industry_stats.empty and len(industry_stats) >= 3:
    corr_cols = ['roe', 'pe', 'PB', 'ROA']
    corr_matrix = industry_stats[corr_cols].corr()
    fig_corr = px.imshow(
        corr_matrix,
        text_auto='.2f',
        color_continuous_scale='RdBu_r',
        range_color=[-1, 1],
        title='Correlation Among Key Metrics'
    )
    fig_corr.update_layout(height=400)
    st.plotly_chart(fig_corr, use_container_width=True)
else:
    st.info("Not enough industries to compute correlation matrix. Please relax filters.")

st.markdown("---")
st.caption("⚠️ Disclaimer: This analysis is for educational purposes only. Not financial advice.")
