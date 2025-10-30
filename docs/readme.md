# PhonePe Transaction Insights Dashboard

**Subtitle:** End-to-End Data Analytics & Visualization Platform  
**Author:** Viraj Gavade  
**Date:** October 17, 2025  
**Version:** 1.0

---

## Table of Contents

- [Project Overview](#project-overview)
- [Architecture Diagram](#architecture-diagram)
- [Folder Structure](#folder-structure)
- [Step-by-Step Guide](#step-by-step-guide)
- [Database Schema](#database-schema)
- [Visualization & Dashboard Section](#visualization--dashboard-section)
- [Deployment Guide](#deployment-guide)
- [Appendix](#appendix)

---

## Project Overview

**What is this project?**  
A full-stack analytics platform for PhonePe transaction data, transforming raw JSON into actionable business insights via ETL, PostgreSQL, Python analysis, and a professional Streamlit dashboard.

**Goals:**
- Decode transaction patterns across states, quarters, and categories.
- Enable business teams to identify growth, stagnation, and new opportunities.
- Provide interactive, exportable visualizations for data-driven decisions.

**Business Use Cases:**
- Regional transaction growth and seasonality
- Device brand engagement analysis
- Insurance penetration and adoption
- Market expansion targeting
- User registration and engagement trends

**Key Features:**
- Top states/districts/pincodes by transaction value and count
- Quarterly and YoY transaction trends
- Device brand and user engagement analytics
- Insurance penetration and growth
- Market expansion heatmaps and scatter plots
- Downloadable CSVs for all charts
- Professional, wide-layout Streamlit dashboard with advanced filters

---

## Architecture Diagram

![Architecture Diagram](../assets/architecture.png)

*Figure 1: End-to-end flow from raw JSON data to Streamlit dashboard. ETL scripts load and transform data into PostgreSQL, which is then analyzed and visualized.*

---

## Folder Structure

```
project-root/
├── etl/                # ETL scripts for data ingestion
├── sql/                # SQL query files and views
├── analysis/           # Python analysis scripts, DB helpers
├── dashboard/          # Streamlit app and dashboard code
├── docs/               # Documentation and guides
├── assets/             # Images and diagrams
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variable template
└── README.md           # Project overview
```

![ETL & Data Pipeline](../assets/etl_data_pipeline.png)

*Figure 3: ETL pipeline showing data sources, ingestion, schema creation, logging, and extension points. All steps are logged and validated for data integrity.*

---

## Step-by-Step Guide

![Step-by-Step Guide & Database Schema](../assets/steup_guide.png)

*Figure 2: Step-by-step guide for environment setup, ETL, data verification, running queries, and launching the dashboard. Database schema and key SQL logic are visually summarized for quick reference.*

### 1. Environment Setup

**Python & Libraries**
```bash
pip install -r requirements.txt
```

**PostgreSQL**
- Install PostgreSQL (13+ recommended)
- Create a database (e.g., `PhonePayDB`)

**Environment Variables**
- Copy `.env.example` to `.env` and fill in your DB credentials.

### 2. ETL Run Instructions

```bash
python etl/load_data.py --input Data/ --db-url postgresql://user:pass@localhost:5432/PhonePayDB
```
- ETL logs progress, errors, and row counts.

### 3. Data Verification Checklist

- [ ] Check row counts in each table
- [ ] Validate no critical columns are NULL
- [ ] Totals (amount, count) match source aggregates

**Sample SQL:**
```sql
SELECT COUNT(*) FROM aggregated_transaction;
SELECT SUM(amount) FROM aggregated_transaction WHERE year=2023;
```

### 4. Using Queries & Analysis Scripts

- Place custom SQL in `queries/`
- Use `analysis/run_queries.py` helpers to run and export results:
```python
from analysis.run_queries import run_query_file
df = run_query_file('queries/1_transaction_dynamics.sql')
```

### 5. Launching the Dashboard

```bash
streamlit run dashboard/app.py
```
- Use sidebar filters for year, quarter, state, transaction type.
- Download CSVs from each chart.

---

## Database Schema

### Main Tables

| Table                   | Description                                 | Key Columns                        |
|-------------------------|---------------------------------------------|------------------------------------|
| aggregated_transaction  | All transactions (state, year, quarter)     | state, year, quarter, amount, count, transaction_type |
| aggregated_user         | Device/user stats by state/brand            | state, year, quarter, device_brand, user_count, user_percentage |
| aggregated_insurance    | Insurance transactions                      | state, year, quarter, amount, count|
| map_transaction         | District-level transactions                 | state, district, year, quarter, amount, count |
| map_user                | User engagement by state/district           | state, district, year, quarter, registered_users, app_opens |

### Indexes

- All tables indexed on (state, year, quarter)
- District tables indexed on (district, year, quarter)

### Example Queries

**Top 10 States by Amount**
```sql
SELECT state, SUM(amount) AS total_amount
FROM aggregated_transaction
WHERE year = 2023
GROUP BY state
ORDER BY total_amount DESC
LIMIT 10;
```

**Quarterly Trends**
```sql
SELECT year, quarter, SUM(amount) AS total_amount
FROM aggregated_transaction
GROUP BY year, quarter
ORDER BY year, quarter;
```

---

## Visualization & Dashboard Section

### Dashboard Overview

The PhonePe Pulse Dashboard is a comprehensive analytics platform built with Streamlit, featuring interactive filters, KPIs, and multiple business case study tabs with downloadable data.

### Main Dashboard Interface

![Dashboard Home - KPIs and Filters](../assets/Screenshot%202025-10-17%20121612.png)

*Figure 4: Dashboard home page showing key performance indicators (Total Transaction Amount, Total Transactions, States Covered, Average Transaction Value) and sidebar filters for Year, Quarter, State, and Transaction Type.*

### Business Case Study Tabs

#### 1. Transaction Dynamics
![Transaction Dynamics Tab](../assets/Screenshot%202025-10-17%20121856.png)

*Figure 5: Transaction Dynamics tab displaying quarterly trends, transaction type breakdown, and year-over-year growth analysis. Features interactive line charts and stacked area charts showing transaction patterns over time.*

#### 2. Top States Analysis
![Top States Bar Chart](../assets/Screenshot%202025-10-17%20121651.png)

*Figure 6: Top 10 states by transaction amount with horizontal bar chart visualization. Each state shows total amount and transaction count with color-coded bars for easy comparison.*

#### 3. Transaction Type Distribution
![Transaction Type Pie Chart](../assets/Screenshot%202025-10-17%20121716.png)

*Figure 7: Transaction type breakdown using donut chart showing distribution across Peer-to-peer payments, Merchant payments, Recharge & bill payments, Financial Services, and Others.*

#### 4. Device Dominance Analysis
![Device Brand Analysis](../assets/Screenshot%202025-10-17%20121912.png)

*Figure 8: Device brand engagement scatter plot showing total users vs. average percentage, sized by user count. Helps identify which device brands have the highest PhonePe adoption.*

#### 5. Device Brand Share
![Device Brand Share Bar](../assets/device_brand_sharev.png)

*Figure 9: Horizontal bar chart showing market share percentage for each device brand, helping identify market leaders in PhonePe user base.*

#### 6. Insurance Penetration
![Insurance State-wise Analysis](../assets/insurance_penetration.png)

*Figure 10: State-wise insurance penetration rate showing insurance transaction amount as percentage of total transaction amount. Identifies states with high/low insurance adoption.*

#### 7. Insurance YoY Growth
![Insurance Year-over-Year Growth](../assets/insurance_yoy.png)

*Figure 11: Year-over-year growth chart for insurance transactions, showing percentage change in insurance amount across different years and quarters.*

#### 8. Market Expansion Analysis
![Market Expansion Stacked Bar](../assets/market_expansion_analysis.png)

*Figure 12: Stacked bar chart showing transaction type distribution for top states, helping identify which transaction types drive growth in each region.*

#### 9. Geographic Heatmap
![State-wise Transaction Heatmap](../assets/Screenshot%202025-10-17%20121759.png)

*Figure 13: State-year heatmap showing transaction amounts across all states and years, making it easy to spot geographic and temporal patterns at a glance.*

#### 10. User Registration Trends
![User Registration Quarterly Trends](../assets/Screenshot%202025-10-17%20121944.png)

*Figure 14: Quarterly registered user trends showing growth in PhonePe user base over time, with state-wise breakdowns available through filters.*

#### 11. Top Registered States
![Top States by Registered Users](../assets/top_registered_states.png)

*Figure 15: Bar chart ranking states by total registered users, highlighting regions with the largest PhonePe user base.*

#### 12. Seasonality Analysis
![Quarterly Seasonality Index](../assets/seasonal_analysis.png)

*Figure 16: Seasonality index heatmap showing per-state quarterly transaction patterns, helping identify seasonal trends and peak transaction periods.*

#### 13. Advanced Analytics Summary
![Advanced Analytics Dashboard](../assets/Screenshot%202025-10-17%20122011.png)

*Figure 17: Advanced analytics summary view combining multiple KPIs, charts, and insights in a single view for comprehensive business intelligence.*

### Dashboard Features

- **Interactive Filters:** Year, Quarter, State (multi-select), Transaction Type
- **Dynamic KPIs:** Total Amount, Total Transactions, States Covered, Avg Transaction Value
- **Business Tabs:** 10+ case study tabs with specialized analytics
- **CSV Downloads:** Every chart includes a download button for data export
- **Responsive Design:** Wide layout optimized for large screens
- **Real-time Updates:** All charts update instantly when filters change
- **Caching:** Intelligent caching for fast performance on repeated queries

### Chart Types & Snippets

**Bar Chart**
```python
fig = px.bar(df, x='state', y='total_amount', color='total_amount')
st.plotly_chart(fig)
```

**Line Chart**
```python
fig = px.line(df, x='period', y='total_amount', color='transaction_type')
st.plotly_chart(fig)
```

**Donut/Pie Chart**
```python
fig = px.pie(df, values='total_amount', names='transaction_type', hole=0.4)
st.plotly_chart(fig)
```

**Heatmap**
```python
fig = px.imshow(share, aspect='auto', color_continuous_scale='YlGnBu')
st.plotly_chart(fig)
```

**Box Plot**
```python
fig = px.box(df, x='transaction_type', y='avg_value', points='all')
st.plotly_chart(fig)
```

### Professional Styling Tips

- Use `st.set_page_config(layout='wide')` for a modern look.
- Consistent color palettes (Viridis, Blues, Reds, etc.)
- Use `st.columns` for multi-panel layouts.
- Add `st.download_button` for every DataFrame.
- Use `@st.cache_data` for all data fetchers to speed up UI.

---

## Deployment Guide

### Local Run

```bash
pip install -r requirements.txt
streamlit run dashboard/app.py
```

### Streamlit Cloud

- Push to GitHub.
- Set environment variables in Streamlit Cloud dashboard.
- Deploy and share your public URL.

### Docker (Optional)

```dockerfile
FROM python:3.10
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD streamlit run dashboard/app.py
```

---


| Day | Task |
|-----|------|
| 1   | Project setup, repo init, requirements |
| 2   | ETL: JSON to Postgres, schema design   |
| 3   | Data validation, sample queries        |
| 4   | Analysis scripts, run_queries.py       |
| 5   | Initial dashboard layout, KPIs         |
| 6   | Top states, quarterly trends charts    |
| 7   | Device engagement, insurance charts    |
| 8   | Market expansion, user registration    |
| 9   | Advanced analytics tabs (seasonality, volatility, etc.) |
| 10  | CSV downloads, caching, styling        |
| 11  | Deployment scripts, .env, docs         |
| 12  | Testing, bugfixes, polish              |
| 13  | Final review, PDF export, handoff      |
| 14  | Buffer / contingency                   |

---

## Appendix

### Useful Commands

- **psql connect:**  
  `psql -U postgres -d PhonePayDB`
- **ETL re-run:**  
  `python etl/load_data.py --input Data/`
- **Export analysis:**  
  `python analysis/export.py --query queries/1_transaction_dynamics.sql --out results.csv`

### Troubleshooting

- **DB connection error:**  
  Check `.env` and Postgres is running.
- **Missing package:**  
  `pip install -r requirements.txt`
- **Streamlit not updating:**  
  Clear cache: `streamlit cache clear`

### Contribution Guidelines

- Fork, branch, and PR for all changes.
- Write clear commit messages.
- Add/modify tests for new features.
- Update documentation for any new modules.

---

## PDF Export

To export this documentation to PDF with a cover and TOC:

```bash
pandoc documentation.md -o documentation.pdf --standalone --toc --pdf-engine=xelatex
```

For a custom cover, add `--variable=title:"PhonePe Transaction Insights Dashboard"`.

---

**End of Documentation**
