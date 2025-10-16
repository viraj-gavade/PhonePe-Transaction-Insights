# PhonePe Pulse Dashboard

An interactive data analytics dashboard built with Streamlit for visualizing PhonePe transaction data across India.

## 🚀 Features

### 📊 Interactive Visualizations
1. **Top 10 States Bar Chart** - Visualize leading states by transaction amount
2. **Quarterly Trends Line Chart** - Track transaction patterns over time
3. **Device Distribution Pie Chart** - Analyze user device preferences
4. **Insurance Comparison** - Compare insurance vs regular transactions
5. **Transaction Type Breakdown** - Understand payment category distribution

### 🎛️ Dynamic Filters
- **Year Filter**: Select specific years or view all data (2018-2024)
- **Quarter Filter**: Filter by quarter (Q1-Q4) or view annual data
- **State Filter**: Focus on specific states or compare all states
- **Transaction Type Filter**: Analyze specific payment categories

### 📈 Key Metrics Dashboard
- Total Transaction Amount (₹)
- Total Transaction Count
- Number of States Covered
- Average Transaction Value

### 📥 Data Export
- Download filtered data as CSV
- Export visualizations for reports
- Save custom query results

## 🛠️ Installation

### Prerequisites
```bash
# Python 3.8+
# PostgreSQL database with PhonePe Pulse data loaded
```

### Install Dependencies
```bash
pip install streamlit pandas plotly psycopg2-binary
```

## 🏃 Running the Dashboard

### 1. Test Database Queries (Recommended)
```bash
python dashboard/test_dashboard.py
```

This will verify:
- Database connection is working
- All required tables exist
- Queries return expected data
- Data types are correct

### 2. Launch Streamlit Dashboard
```bash
streamlit run dashboard/app.py
```

The dashboard will open in your browser at `http://localhost:8501`

### 3. Using the Dashboard

1. **Select Filters** in the sidebar:
   - Choose Year (or "All" for all years)
   - Choose Quarter (or "All" for all quarters)
   - Choose State (or "All" for nationwide view)
   - Choose Transaction Type (or "All" for all types)

2. **View Visualizations**:
   - Charts update automatically when filters change
   - Hover over charts for detailed information
   - Scroll down to see all visualizations

3. **Download Data**:
   - Click download buttons at the bottom
   - Choose which dataset to export
   - CSV files are saved with filter information in filename

## 📊 Generating Static Figures

To create publication-ready figures for README/presentations:

```bash
cd analysis
python visualize.py
```

This generates:
- `top_10_states.png` - Bar chart of top states
- `quarterly_trends.png` - Time series analysis
- `device_distribution.png` - Pie chart of devices
- `insurance_comparison.png` - Transaction vs insurance
- `transaction_types_yearly.png` - Stacked bar chart
- `state_year_heatmap.png` - Geographic heatmap
- Interactive HTML versions of all charts

Figures are saved in `analysis/figs/` directory.

## 🗂️ Project Structure

```
dashboard/
├── app.py                  # Main Streamlit dashboard
├── test_dashboard.py       # Query testing script
└── README.md              # This file

analysis/
├── run_queries.py         # Database query functions
├── visualize.py           # Static visualization generator
└── figs/                  # Generated figures
    ├── top_10_states.png
    ├── quarterly_trends.png
    └── ...
```

## 🔍 Available Queries

The dashboard uses the following database tables:

### aggregated_transaction
- Columns: year, quarter, state, transaction_type, count, amount
- Contains: Transaction data by category and location

### aggregated_insurance
- Columns: year, quarter, state, insurance_type, count, amount
- Contains: Insurance transaction data

### aggregated_user
- Columns: year, quarter, state, device_brand, user_count, user_percentage
- Contains: User demographics and device information

## 🎨 Customization

### Modify Filters
Edit `dashboard/app.py` lines 40-60 to customize filter options:
```python
year_options = ['All', 2018, 2019, 2020, 2021, 2022, 2023, 2024]
quarter_options = ['All', 1, 2, 3, 4]
```

### Add New Visualizations
1. Create a new query function in `app.py`:
```python
@st.cache_data
def get_my_data(year, quarter):
    sql = "SELECT ... FROM ... WHERE ..."
    return run_query(sql, params=[year, quarter])
```

2. Add visualization code:
```python
st.markdown("## My New Chart")
my_df = get_my_data(year, quarter)
fig = px.bar(my_df, x='column1', y='column2')
st.plotly_chart(fig, use_container_width=True)
```

### Customize Styling
Modify the CSS in `app.py` lines 23-35:
```python
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        color: #5f27cd;
    }
    </style>
""", unsafe_allow_html=True)
```

## 🐛 Troubleshooting

### Database Connection Error
```
Error: could not connect to server
```
**Solution**: Check PostgreSQL is running and credentials in `analysis/run_queries.py` are correct.

### No Data Displayed
```
Warning: No data available for the selected filters
```
**Solution**: 
- Verify data exists for selected year/quarter
- Check ETL process completed successfully
- Run `test_dashboard.py` to verify queries

### Import Error
```
ModuleNotFoundError: No module named 'analysis'
```
**Solution**: Run from project root directory: `streamlit run dashboard/app.py`

### Plotly Images Not Saving
```
Could not save PNG (install kaleido)
```
**Solution**: 
```bash
pip install kaleido
```

## 📝 Performance Tips

1. **Use Caching**: All query functions use `@st.cache_data` to avoid repeated database calls
2. **Limit Results**: Use `LIMIT` in SQL queries for large datasets
3. **Index Database**: Create indexes on frequently queried columns (year, quarter, state)
4. **Filter Early**: Apply filters in SQL queries rather than in pandas

## 🤝 Contributing

To add new features:
1. Test queries in `test_dashboard.py`
2. Add query function with `@st.cache_data` decorator
3. Create visualization using Plotly or matplotlib
4. Update this README with new features

## 📄 License

This project uses PhonePe Pulse data. Please refer to the main repository LICENSE.

## 🔗 Resources

- [Streamlit Documentation](https://docs.streamlit.io/)
- [Plotly Python](https://plotly.com/python/)
- [PhonePe Pulse Repository](https://github.com/PhonePe/pulse)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

---

**Built with** ❤️ **using Streamlit**
