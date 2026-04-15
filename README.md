# A-Share Industry Valuation & Profitability Dashboard

**Product Link:** [Live Streamlit App](https://a-share-analysis-9p8bqnj7z8dycz9h7qtuyn.streamlit.app)

---

## 1. Problem & User
Investors need a quick, visual way to screen A-share industries for attractive valuation combined with strong profitability. This interactive dashboard allows users to filter industries by PE, PB, ROE, and ROA, and to identify sectors that offer a balance of low valuation and high return. The target audience includes retail investors, finance students, and entry-level analysts seeking an intuitive overview of industry-level financial health.

## 2. Data
- **Source:** WRDS Compustat Global – tables `comp.g_funda` and `comp.g_secd`.
- **Access Date:** April 2026.
- **Coverage:** Chinese A-share companies (`loc='CHN'`) for fiscal year 2024.
- **Key Fields:** Net income (`ibc`), common equity (`ceq`), closing price (`prccd`), shares outstanding (`cshoc`), SIC industry code (`sich`).
- **Cleaned Dataset:** `a_share_final.csv` (3,733 companies after removing missing/outlier values).

## 3. Methods
1. **Data Acquisition:** Extracted financial fundamentals and market data from WRDS using SQL queries via the `wrds` Python package.
2. **Data Merging & Cleaning:** Joined fundamentals with price data on `gvkey`; removed records with missing or extreme values.
3. **Feature Engineering:** Calculated ROE, PE, PB, ROA, and market capitalization. Standardized units by converting market cap (RMB) to millions to match Compustat equity units.
4. **Industry Aggregation:** Grouped by SIC industry and computed median metrics to reduce the influence of outliers.
5. **Interactive Dashboard:** Built with `streamlit` and `plotly.express`. Users can filter by ROE, PE, and minimum companies per industry, switch between two analysis views, and explore a correlation heatmap.

## 4. Key Findings
- Industries with **high ROE (>15%) and low PE (<30)** are predominantly found in consumer goods and technology sectors (based on SIC codes).
- A weak negative correlation (-0.23) exists between PE and ROE at the industry level, suggesting that high profitability does not always command proportionally higher valuations.
- The PB vs. ROA view highlights asset-efficient industries that generate strong returns on assets with reasonable book value multiples.
- Most A-share industries exhibit a median PE below 50 and a median ROE between 5% and 20%.

## 5. How to Run Locally
git clone https://github.com/cassielee24/a-share-analysis.git
cd a-share-analysis
pip install -r requirements.txt
streamlit run app.py

## 6. Product Link / Demo
- **Live Dashboard:** [Streamlit App](https://a-share-analysis-9p8bqnj7z8dycz9h7qtuyn.streamlit.app)
- **Demo Video:** *[Link to your 1–3 minute demo video]*  
  *(Please insert the video link here before final submission.)*

## 7. Limitations & Next Steps
- **Data Currency:** Only fiscal year 2024 data is used; incorporating multi-year trends would improve robustness.
- **Industry Granularity:** SIC codes are broad; more detailed classifications (e.g., GICS) would enhance precision.
- **Derived Metrics:** ROA and net margin are approximations due to the absence of total asset data in the current extraction.
- **Survivorship Bias:** The dataset excludes companies with negative earnings or equity.
- **Next Steps:** Add time-series analysis, integrate macroeconomic overlays, and improve mobile responsiveness.
```
