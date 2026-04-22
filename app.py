import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import os

# ==================== PAGE CONFIG ====================
st.set_page_config(
    page_title="A-Share Industry Analysis",
    page_icon="📊",
    layout="wide"
)

# ==================== HEADER ====================
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

min_roe = st.sidebar.slider("Minimum ROE (%)", -20.0, 50.0, 0.0, 0.5)
max_pe = st.sidebar.slider("Maximum PE Ratio", 0, 300, 150, 5)
min_companies = st.sidebar.slider("Min Companies per Industry", 1, 15, 3)

st.sidebar.markdown("---")
st.sidebar.info("*Data: WRDS Compustat Global*\n\n*ACC102 Mini Assignment*")

# ==================== DATA LOADING ====================
@st.cache_data
def load_data():
   
    if not os.path.exists('a_share_final.csv'):
        return pd.DataFrame()
        
    df = pd.read_csv('a_share_final.csv')
    
   
    required_cols = ['market_cap', 'ceq', 'ibc', 'roe', 'pe', 'sich']
    if not all(col in df.columns for col in required_cols):
        st.error("Missing required columns in the dataset.")
        return pd.DataFrame()

    df['market_cap_mil'] = df['market_cap'] / 1e6
    
   
    df['PB'] = np.where(df['ceq'] != 0, df['market_cap_mil'] / df['ceq'], np.nan)
    df['ROA'] = np.where(df['ceq'] != 0, (df['ibc'] / (df['ceq'] * 2)) * 100, np.nan)
    
    df = df[(df['PB'] > 0) & (df['PB'] < 50)]
    return df

df = load_data()


if df.empty:
    st.error("⚠️ Error: 'a_share_final.csv' not found or is empty. Please ensure the data file is in the same directory.")
    st.stop()

# ==================== DATA PROCESSING ====================
df_filtered = df[(df['roe'] >= min_roe) & (df['pe'] <= max_pe)]

industry_stats = df_filtered.groupby('sich').agg({
    'roe': 'median',
    'pe': 'median',
    'PB': 'median',
    'ROA': 'median',
    'sich': 'count', 
    'market_cap': 'sum'
}).rename(columns={'sich': 'Company Count', 'market_cap': 'Total Market Cap'}).reset_index()

industry_stats = industry_stats[industry_stats['Company Count'] >= min_companies]

if not industry_stats.empty:
    industry_stats['PEG Proxy'] = np.where(
        industry_stats['roe'] > 0, 
        industry_stats['pe'] / industry_stats['roe'], 
        np.nan
    )
    industry_stats['Log Market Cap'] = np.where(
        industry_stats['Total Market Cap'] > 0,
        np.log10(industry_stats['Total Market Cap']),
        0
    )

# ==================== KPI CARDS ====================
st.markdown("### 📈 Market Snapshot")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Companies Analyzed", f"{len(df_filtered):,}")
col2.metric("Industries Covered", len(industry_stats))
col3.metric("Median ROE", f"{df_filtered['roe'].median():.1f}%" if not df_filtered.empty else "N/A")
col4.metric("Median PE", f"{df_filtered['pe'].median():.1f}" if not df_filtered.empty else "N/A")

st.markdown("---")

# ==================== TABS LAYOUT ====================
tab1, tab2, tab3 = st.tabs(["📊 Scatter Analysis", "📋 Data Table", "📈 Heatmap"])

# -------- TAB 1: Main Chart --------
with tab1:
    if industry_stats.empty:
        st.warning("⚠️ No industries match the current filters. Please relax the criteria in the sidebar.")
    else:
        if view_mode == "PE vs ROE (Valuation & Profitability)":
            x_axis, y_axis = 'pe', 'roe'
            x_label, y_label = 'P/E Ratio (Median)', 'ROE % (Median)'
            color_by, color_label = 'PEG Proxy', 'PE/ROE (PEG Proxy)'
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
            hover_name='sich', 
            hover_data={'sich': False, 'pe': ':.2f', 'roe': ':.2f', 'PB': ':.2f', 'ROA': ':.2f', 'Company Count': True},
            labels={
                x_axis: x_label,
                y_axis: y_label,
                color_by: color_label,
                'Company Count': 'Number of Companies'
            },
            height=600
        )
        
        if view_mode == "PE vs ROE (Valuation & Profitability)":
            fig.add_hline(y=10, line_dash="dash", line_color="green", annotation_text="Target ROE=10%")
            fig.add_vline(x=30, line_dash="dash", line_color="red", annotation_text="High PE=30")

# 添加趋势线
        fig.add_traces(
            px.scatter(
                industry_stats, x='pe', y='roe', trendline='ols'
            ).data[1]
        ) 
        fig.update_layout(
            template="plotly_white", 
            hovermode='closest', 
            coloraxis_colorbar=dict(title=color_label),
            margin=dict(l=20, r=20, t=30, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)

# -------- TAB 2: Data Table --------
with tab2:
    if not industry_stats.empty:
        col_sort, col_order = st.columns([1, 1])
        with col_sort:
            sort_col = st.selectbox("Sort by:", ['roe', 'pe', 'PB', 'ROA', 'Company Count', 'Total Market Cap'])
        with col_order:
            sort_asc = st.radio("Order:", ["Descending", "Ascending"], horizontal=True) == "Ascending"

        st.dataframe(
            industry_stats[['sich', 'roe', 'pe', 'PB', 'ROA', 'Company Count', 'Total Market Cap']]
            .sort_values(sort_col, ascending=sort_asc)
            .style.format({
                'roe': '{:.2f}%',
                'pe': '{:.2f}',
                'PB': '{:.2f}',
                'ROA': '{:.2f}%',
                'Total Market Cap': '{:,.0f}'
            })
            .background_gradient(subset=['roe', 'ROA'], cmap='Greens')
            .background_gradient(subset=['pe', 'PB'], cmap='Reds_r'),
            use_container_width=True,
            height=500
        )
    else:
        st.info("No data to display. Adjust filters to see industry metrics.")

# -------- TAB 3: Heatmap --------
with tab3:
    if not industry_stats.empty and len(industry_stats) >= 3:
        corr_cols = ['roe', 'pe', 'PB', 'ROA']
        corr_matrix = industry_stats[corr_cols].corr()
        
        fig_corr = px.imshow(
            corr_matrix,
            text_auto='.2f',
            color_continuous_scale='RdBu_r',
            aspect="auto",
            range_color=[-1, 1],
            title='Pearson Correlation Among Key Metrics'
        )
        fig_corr.update_layout(height=500)
        st.plotly_chart(fig_corr, use_container_width=True)
    else:
        st.info("Not enough industries to compute correlation matrix. Please relax filters.")
# --- New Charts Added for Enhanced Analysis ---

st.markdown("---")
st.subheader("🥧 Top 10 Industries by Total Market Cap")

if not industry_stats.empty:
    # Get the top 10 industries by total market cap
    top10_mcap = industry_stats.nlargest(10, 'Total Market Cap')[['sich', 'Total Market Cap']]
    top10_mcap['sich'] = top10_mcap['sich'].astype(int).astype(str)

    fig_pie = px.pie(
        top10_mcap,
        values='Total Market Cap',
        names='sich',
        title='Top 10 Industries by Total Market Cap (RMB)',
        hole=0.3
    )
    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_pie, use_container_width=True)
else:
    st.info("No industry data available to display pie chart.")

# ==================== FOOTER ====================
st.markdown("---")
