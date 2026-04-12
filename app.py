import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# Page Configuration
st.set_page_config(
    page_title="A-Share Multi-Dimensional Analysis",
    page_icon="📊",
    layout="wide"
)

st.title("📊 A-Share Multi-Dimensional Industry Analysis")
st.markdown("""
This dashboard provides comprehensive analysis across **Valuation**, **Profitability**, **Growth**, and **Risk** dimensions.
""")

# ==================== SIDEBAR ====================
st.sidebar.header("🎛️ Analysis Controls")

# Dimension Selection
analysis_dimension = st.sidebar.selectbox(
    "Primary Dimension",
    ["Valuation vs Profitability", "Growth vs Valuation", "Risk vs Return", "Size vs Profitability"]
)

# Filters
st.sidebar.markdown("---")
st.sidebar.subheader("📊 Data Filters")

min_roe = st.sidebar.slider("Minimum ROE (%)", 0.0, 50.0, 5.0, 0.5)
max_pe = st.sidebar.slider("Maximum PE Ratio", 0, 200, 100, 5)
min_companies = st.sidebar.slider("Min Companies per Industry", 1, 20, 5)

st.sidebar.markdown("---")
st.sidebar.markdown("*Data: WRDS Compustat Global*")
st.sidebar.markdown("*ACC102 Assignment*")

# ==================== DATA LOADING ====================
@st.cache_data
def load_data():
    df = pd.read_csv('a_share_final.csv')
    # Add derived metrics
    df['PB'] = df['market_cap'] / df['ceq']  # Price to Book (proxy)
    df['ROA'] = df['ibc'] / (df['ceq'] * 1.5) * 100  # Approximate ROA
    df['Net Margin'] = df['ibc'] / (df['market_cap'] / df['pe']) * 100  # Approximate
    return df

df = load_data()

# Filter
df_filtered = df[(df['roe'] >= min_roe) & (df['pe'] <= max_pe)]

# Industry Aggregation
industry_stats = df_filtered.groupby('sich').agg({
    'roe': 'median',
    'pe': 'median',
    'PB': 'median',
    'ROA': 'median',
    'Net Margin': 'median',
    'conm': 'count',
    'market_cap': 'sum'
}).rename(columns={'conm': 'Company Count', 'market_cap': 'Total Market Cap'}).reset_index()

industry_stats = industry_stats[industry_stats['Company Count'] >= min_companies]

# Derived metrics
industry_stats['PEG Proxy'] = industry_stats['pe'] / industry_stats['roe']
industry_stats['Risk Proxy'] = 1 / industry_stats['roe']  # Inverse ROE as simple risk proxy
industry_stats['Log Market Cap'] = np.log10(industry_stats['Total Market Cap'])

# ==================== KPI CARDS ====================
st.markdown("### 📈 Key Metrics Overview")
col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    st.metric("Companies", f"{len(df_filtered):,}")
with col2:
    st.metric("Industries", len(industry_stats))
with col3:
    st.metric("Median ROE", f"{df_filtered['roe'].median():.1f}%")
with col4:
    st.metric("Median PE", f"{df_filtered['pe'].median():.1f}")
with col5:
    st.metric("Median PB", f"{df_filtered['PB'].median():.2f}")
with col6:
    st.metric("Total Market Cap", f"¥{industry_stats['Total Market Cap'].sum()/1e12:.2f}T")

st.markdown("---")

# ==================== MAIN VISUALIZATION ====================
st.subheader(f"📊 {analysis_dimension}")

col_left, col_right = st.columns([3, 1])

with col_left:
    if analysis_dimension == "Valuation vs Profitability":
        x_axis = 'pe'
        y_axis = 'roe'
        x_label = 'P/E Ratio (Median)'
        y_label = 'ROE % (Median)'
        color_by = 'PEG Proxy'
        color_label = 'PE/ROE'
        
    elif analysis_dimension == "Growth vs Valuation":
        x_axis = 'pe'
        y_axis = 'ROA'
        x_label = 'P/E Ratio (Median)'
        y_label = 'ROA % (Median)'
        color_by = 'Company Count'
        color_label = 'Companies'
        
    elif analysis_dimension == "Risk vs Return":
        x_axis = 'Risk Proxy'
        y_axis = 'roe'
        x_label = 'Risk Proxy (1/ROE)'
        y_label = 'ROE % (Median)'
        color_by = 'PB'
        color_label = 'P/B Ratio'
        
    else:  # Size vs Profitability
        x_axis = 'Log Market Cap'
        y_axis = 'roe'
        x_label = 'Log10(Market Cap)'
        y_label = 'ROE % (Median)'
        color_by = 'pe'
        color_label = 'P/E Ratio'

    fig = px.scatter(
        industry_stats,
        x=x_axis,
        y=y_axis,
        size='Company Count',
        color=color_by,
        color_continuous_scale='RdYlGn_r' if color_by == 'PEG Proxy' else 'Viridis',
        hover_data={
            'sich': True,
            'pe': ':.2f',
            'roe': ':.2f',
            'PB': ':.2f',
            'ROA': ':.2f',
            'Company Count': True,
            'Total Market Cap': ':,.0f'
        },
        labels={
            x_axis: x_label,
            y_axis: y_label,
            color_by: color_label,
            'Company Count': 'Number of Companies'
        },
        height=550
    )
    
    fig.update_layout(
        template="plotly_white",
        hovermode='closest',
        coloraxis_colorbar=dict(title=color_label)
    )
    
    st.plotly_chart(fig, use_container_width=True)

with col_right:
    st.markdown("#### 📌 Legend")
    st.markdown(f"""
    **Current View:** {analysis_dimension}
    
    **X-Axis:** {x_label}
    **Y-Axis:** {y_label}
    **Color:** {color_label}
    **Size:** Number of Companies
    
    ---
    **Top Performers:**
    """)
    
    top_n = industry_stats.nlargest(3, y_axis)[['sich', y_axis, x_axis]]
    for _, row in top_n.iterrows():
        st.metric(
            f"Industry {int(row['sich'])}",
            f"{row[y_axis]:.1f}",
            delta=f"{x_label}: {row[x_axis]:.2f}"
        )

st.markdown("---")

# ==================== MULTI-DIMENSIONAL TABLE ====================
st.subheader("📋 Multi-Dimensional Industry Analysis")

col1, col2 = st.columns([2, 1])

with col1:
    sort_col = st.selectbox(
        "Sort by metric:",
        ['roe', 'pe', 'PB', 'ROA', 'Net Margin', 'Company Count', 'Total Market Cap', 'PEG Proxy']
    )

with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    show_all = st.checkbox("Show all columns", value=False)

display_cols = ['sich', 'roe', 'pe', 'PB', 'ROA', 'Net Margin', 'Company Count', 'Total Market Cap', 'PEG Proxy']
if not show_all:
    display_cols = ['sich', 'roe', 'pe', 'PB', 'Company Count', 'PEG Proxy']

st.dataframe(
    industry_stats[display_cols].sort_values(sort_col, ascending=False)
    .style.format({
        'roe': '{:.2f}',
        'pe': '{:.2f}',
        'PB': '{:.2f}',
        'ROA': '{:.2f}',
        'Net Margin': '{:.2f}',
        'PEG Proxy': '{:.2f}',
        'Total Market Cap': '{:,.0f}'
    })
    .background_gradient(subset=['roe', 'ROA', 'Net Margin'], cmap='Greens')
    .background_gradient(subset=['pe', 'PB', 'PEG Proxy'], cmap='Reds_r'),
    use_container_width=True,
    height=400
)

st.markdown("---")

# ==================== CORRELATION HEATMAP ====================
st.subheader("🔥 Metric Correlations")

corr_cols = ['roe', 'pe', 'PB', 'ROA', 'Net Margin', 'Company Count', 'PEG Proxy']
corr_matrix = industry_stats[corr_cols].corr()

fig_corr = px.imshow(
    corr_matrix,
    text_auto='.2f',
    color_continuous_scale='RdBu_r',
    range_color=[-1, 1],
    title='Correlation Matrix of Key Metrics'
)
fig_corr.update_layout(height=450)
st.plotly_chart(fig_corr, use_container_width=True)

st.markdown("---")
st.caption("⚠️ Disclaimer: This analysis is for educational purposes only. Not financial advice.")
