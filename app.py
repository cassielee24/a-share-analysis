import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="A股行业估值分析", layout="wide")
st.title("A股行业 PE vs ROE 分析仪表盘")
st.markdown("---")
st.subheader("🎛️ 筛选条件")

col1, col2 = st.columns(2)
with col1:
    min_roe = st.slider("最低 ROE (%)", 0.0, 50.0, 5.0)
with col2:
    max_pe = st.slider("最高 PE", 0, 200, 100)
st.markdown("*数据来源：WRDS Compustat Global | ACC102 作业*")

@st.cache_data
def load_data():
    df = pd.read_csv('a_share_final.csv')
    return df

df = load_data()
st.success(f"成功加载 {len(df)} 家公司数据")
st.markdown("---")
st.subheader("📈 行业 PE vs ROE 散点图")

# 按行业计算中位数
# 先筛选公司数据
df_filtered = df[(df['roe'] >= min_roe) & (df['pe'] <= max_pe)]

industry = df_filtered.groupby('sich').agg({
    'roe': 'median',
    'pe': 'median',
    'conm': 'count'
}).rename(columns={'conm': '公司数量'}).reset_index()

industry = industry[industry['公司数量'] >= 5]

fig = px.scatter(
    industry, 
    x='pe', 
    y='roe', 
    size='公司数量',
    hover_data=['sich'],
    title='各行业 PE vs ROE（每个点代表一个行业）'
)

fig.add_hline(y=10, line_dash="dash", line_color="green", annotation_text="ROE=10%")
fig.add_vline(x=30, line_dash="dash", line_color="red", annotation_text="PE=30")

st.plotly_chart(fig, use_container_width=True)
