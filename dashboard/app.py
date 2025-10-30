import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import os


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from analysis.run_queries import run_query, run_query_file, run_query_file_select

st.set_page_config(
    page_title="PhonePe Pulse Dashboard",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #5f27cd;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

# ==========================
# Sidebar Filters
# ==========================
st.sidebar.title("🎛️ Filters")
st.sidebar.markdown("---")

# Year filter
year_options = ['All', 2018, 2019, 2020, 2021, 2022, 2023, 2024]
year = st.sidebar.selectbox("📅 Year", year_options, index=0)

# Quarter filter
quarter_options = ['All', 1, 2, 3, 4]
quarter = st.sidebar.selectbox("📊 Quarter", quarter_options, index=0)

# State filter (multi-select)
@st.cache_data
def get_states():
    sql = "SELECT DISTINCT state FROM aggregated_transaction ORDER BY state;"
    df = run_query(sql)
    return df['state'].tolist()

state_options = get_states()
selected_states = st.sidebar.multiselect("📍 States", options=state_options, default=[])

# Transaction Type filter
transaction_types = ['All', 'Peer-to-peer payments', 'Merchant payments', 
                     'Recharge & bill payments', 'Financial Services', 'Others']
transaction_type = st.sidebar.selectbox("💳 Transaction Type", transaction_types, index=0)

st.sidebar.markdown("---")
st.sidebar.info("📱 PhonePe Pulse Data Analytics Dashboard")



def apply_time_filters(df: pd.DataFrame, year_sel, quarter_sel) -> pd.DataFrame:
    if 'year' in df.columns and year_sel != 'All':
        df = df[df['year'] == year_sel]
    if 'quarter' in df.columns and quarter_sel != 'All':
        df = df[df['quarter'] == quarter_sel]
    return df

def apply_state_filters(df: pd.DataFrame, states: list) -> pd.DataFrame:
    if states and 'state' in df.columns:
        df = df[df['state'].isin(states)]
    return df

def apply_txn_type_filter(df: pd.DataFrame, txn_type: str) -> pd.DataFrame:
    if txn_type != 'All' and 'transaction_type' in df.columns:
        df = df[df['transaction_type'] == txn_type]
    return df

@st.cache_data
def get_top_states_df(limit=10):
    df = run_query_file('sql/queries/1_transaction_dynamics.sql')
    # This returns top states query per file (last SELECT). If needed, ensure it is the right one.
    df = df.rename(columns={'sum': 'total_amount'}) if 'sum' in df.columns else df
    if 'total_amount' not in df.columns and 'total_amount' in df.columns:
        pass
    return df.head(limit)

@st.cache_data
def get_quarterly_trends_df():
    # Use the first SELECT in the file which creates a view; we want trends
    text = run_query_file_select('sql/queries/1_transaction_dynamics.sql', contains='year, quarter')
    return text

@st.cache_data
def get_device_engagement_df():
    # Last select in file is engagement ratio
    return run_query_file('sql/queries/2_device_engagement.sql')

@st.cache_data
def get_insurance_trends_df():
    return run_query_file('sql/queries/3_insurance_penetration.sql')

@st.cache_data
def get_summary_metrics(year, quarter, states, transaction_type):
    """Get summary metrics for KPI cards"""
    conditions = []
    params = []
    
    if year != 'All':
        conditions.append("year = %s")
        params.append(year)
    if quarter != 'All':
        conditions.append("quarter = %s")
        params.append(quarter)
    if states:
        conditions.append("state = ANY(%s)")
        params.append(states)
    if transaction_type != 'All':
        conditions.append("transaction_type = %s")
        params.append(transaction_type)
    
    where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
    
    sql = f"""
        SELECT 
            SUM(amount) AS total_amount,
            SUM(count) AS total_transactions,
            COUNT(DISTINCT state) AS total_states,
            AVG(amount) AS avg_transaction_value
        FROM aggregated_transaction
        {where_clause};
    """
    return run_query(sql, params=params if params else None)

@st.cache_data
def get_top_states(year, quarter, states, transaction_type, limit=10):
    """Get top states by transaction amount with multi-select state filter"""
    conditions = []
    params = []

    if year != 'All':
        conditions.append("year = %s")
        params.append(year)
    if quarter != 'All':
        conditions.append("quarter = %s")
        params.append(quarter)
    if states:
        conditions.append("state = ANY(%s)")
        params.append(states)
    if transaction_type != 'All':
        conditions.append("transaction_type = %s")
        params.append(transaction_type)

    where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

    sql = f"""
        SELECT state,
               SUM(amount) AS total_amount,
               SUM(count) AS total_transactions
        FROM aggregated_transaction
        {where_clause}
        GROUP BY state
        ORDER BY total_amount DESC
        LIMIT %s;
    """
    params.append(limit)
    return run_query(sql, params=params if params else None)

@st.cache_data
def get_quarterly_trends(year, states, transaction_type):
    """Get quarterly transaction trends with multi-select state filter"""
    conditions = []
    params = []

    if year != 'All':
        conditions.append("year = %s")
        params.append(year)
    if states:
        conditions.append("state = ANY(%s)")
        params.append(states)
    if transaction_type != 'All':
        conditions.append("transaction_type = %s")
        params.append(transaction_type)

    where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

    sql = f"""
        SELECT year, quarter,
               SUM(amount) AS total_amount,
               SUM(count) AS total_transactions
        FROM aggregated_transaction
        {where_clause}
        GROUP BY year, quarter
        ORDER BY year, quarter;
    """
    return run_query(sql, params=params if params else None)

@st.cache_data
def get_transaction_type_breakdown(year, quarter, states):
    """Get transaction type breakdown with multi-select state filter"""
    conditions = []
    params = []

    if year != 'All':
        conditions.append("year = %s")
        params.append(year)
    if quarter != 'All':
        conditions.append("quarter = %s")
        params.append(quarter)
    if states:
        conditions.append("state = ANY(%s)")
        params.append(states)

    where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

    sql = f"""
        SELECT transaction_type,
               SUM(amount) AS total_amount,
               SUM(count) AS total_transactions
        FROM aggregated_transaction
        {where_clause}
        GROUP BY transaction_type
        ORDER BY total_amount DESC;
    """
    return run_query(sql, params=params if params else None)

@st.cache_data
def get_device_distribution(year, quarter, states):
    """Get device brand distribution with multi-select state filter"""
    conditions = []
    params = []

    if year != 'All':
        conditions.append("year = %s")
        params.append(year)
    if quarter != 'All':
        conditions.append("quarter = %s")
        params.append(quarter)
    if states:
        conditions.append("state = ANY(%s)")
        params.append(states)

    where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

    sql = f"""
        SELECT device_brand,
               SUM(user_count) AS total_users,
               AVG(user_percentage) AS avg_percentage
        FROM aggregated_user
        {where_clause}
        GROUP BY device_brand
        ORDER BY total_users DESC
        LIMIT 10;
    """
    return run_query(sql, params=params if params else None)

@st.cache_data
def get_insurance_comparison(year, quarter, states):
    """Get insurance totals by state with multi-select filter"""
    conditions = []
    params = []

    if year != 'All':
        conditions.append("year = %s")
        params.append(year)
    if quarter != 'All':
        conditions.append("quarter = %s")
        params.append(quarter)
    if states:
        conditions.append("state = ANY(%s)")
        params.append(states)

    where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

    insurance_sql = f"""
        SELECT state,
               SUM(amount) AS insurance_amount,
               SUM(count) AS insurance_count
        FROM aggregated_insurance
        {where_clause}
        GROUP BY state
        ORDER BY insurance_amount DESC
        LIMIT 10;
    """
    return run_query(insurance_sql, params=params if params else None)

@st.cache_data
def get_txn_type_breakdown_df():
    sql = """
        SELECT transaction_type, SUM(amount) AS total_amount, SUM(count) AS total_transactions
        FROM aggregated_transaction
        GROUP BY transaction_type
        ORDER BY total_amount DESC;
    """
    return run_query(sql)

# ==========================
# Main Dashboard
# ==========================

# Header
st.markdown('<h1 class="main-header">📱 PhonePe Pulse Dashboard</h1>', unsafe_allow_html=True)

# Summary Metrics
st.markdown("## 📊 Key Metrics")
metrics_df = get_summary_metrics(year, quarter, selected_states, transaction_type)

if not metrics_df.empty:
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_amount = metrics_df['total_amount'].iloc[0]
        st.metric(
            label="💰 Total Transaction Amount",
            value=f"₹{total_amount/1e9:.2f}B" if pd.notna(total_amount) else "N/A"
        )
    
    with col2:
        total_txns = metrics_df['total_transactions'].iloc[0]
        st.metric(
            label="🔢 Total Transactions",
            value=f"{total_txns/1e6:.2f}M" if pd.notna(total_txns) else "N/A"
        )
    
    with col3:
        total_states = metrics_df['total_states'].iloc[0]
        st.metric(
            label="📍 States Covered",
            value=f"{int(total_states)}" if pd.notna(total_states) else "N/A"
        )
    
    with col4:
        avg_value = metrics_df['avg_transaction_value'].iloc[0]
        st.metric(
            label="📈 Avg Transaction Value",
            value=f"₹{avg_value:.2f}" if pd.notna(avg_value) else "N/A"
        )

st.markdown("---")

# ==========================
# Visualizations
# ==========================

# Row 1: Top States Bar Chart
st.markdown("## 🏆 Top 10 States by Transaction Amount")
top_states_df = get_top_states(year, quarter, selected_states, transaction_type, limit=10)

if not top_states_df.empty:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        fig_states = px.bar(
            top_states_df,
            x='state',
            y='total_amount',
            title='Top 10 States by Transaction Amount',
            labels={'total_amount': 'Total Amount (₹)', 'state': 'State'},
            color='total_amount',
            color_continuous_scale='Viridis'
        )
        fig_states.update_layout(height=400)
        st.plotly_chart(fig_states, use_container_width=True)
    
    with col2:
        st.markdown("### 📋 Data Table")
        display_df = top_states_df.copy()
        display_df['total_amount'] = display_df['total_amount'].apply(lambda x: f"₹{x/1e9:.2f}B")
        display_df['total_transactions'] = display_df['total_transactions'].apply(lambda x: f"{x/1e6:.2f}M")
        st.dataframe(display_df, use_container_width=True, height=400)
else:
    st.warning("No data available for the selected filters.")

st.markdown("---")

# Row 2: Quarterly Trends and Transaction Type Breakdown
col1, col2 = st.columns(2)

with col1:
    st.markdown("## 📈 Quarterly Trends")
    trends_df = get_quarterly_trends(year, selected_states, transaction_type)
    
    if not trends_df.empty:
        trends_df['period'] = trends_df['year'].astype(str) + '-Q' + trends_df['quarter'].astype(str)
        
        fig_trends = px.line(
            trends_df,
            x='period',
            y='total_amount',
            title='Transaction Amount Trends Over Time',
            labels={'total_amount': 'Total Amount (₹)', 'period': 'Period'},
            markers=True
        )
        fig_trends.update_layout(height=400)
        st.plotly_chart(fig_trends, use_container_width=True)
    else:
        st.warning("No trend data available.")

with col2:
    st.markdown("## 💳 Transaction Type Breakdown")
    txn_type_df = get_transaction_type_breakdown(year, quarter, selected_states)
    
    if not txn_type_df.empty:
        fig_pie = px.pie(
            txn_type_df,
            values='total_amount',
            names='transaction_type',
            title='Transaction Amount Distribution by Type',
            hole=0.4
        )
        fig_pie.update_layout(height=400)
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.warning("No transaction type data available.")

st.markdown("---")

# Row 3: Device Distribution and Insurance Comparison
col1, col2 = st.columns(2)

with col1:
    st.markdown("## 📱 Device Brand Distribution")
    device_df = get_device_distribution(year, quarter, selected_states)
    
    if not device_df.empty:
        fig_device = px.bar(
            device_df,
            x='device_brand',
            y='total_users',
            title='Top Device Brands by User Count',
            labels={'total_users': 'Total Users', 'device_brand': 'Device Brand'},
            color='total_users',
            color_continuous_scale='Blues'
        )
        fig_device.update_layout(height=400)
        st.plotly_chart(fig_device, use_container_width=True)
    else:
        st.warning("No device data available.")

with col2:
    st.markdown("## 🏥 Insurance Transactions")
    insurance_df = get_insurance_comparison(year, quarter, selected_states)
    
    if not insurance_df.empty:
        fig_insurance = px.bar(
            insurance_df,
            x='state',
            y='insurance_amount',
            title='Top 10 States by Insurance Amount',
            labels={'insurance_amount': 'Insurance Amount (₹)', 'state': 'State'},
            color='insurance_amount',
            color_continuous_scale='Reds'
        )
        fig_insurance.update_layout(height=400)
        st.plotly_chart(fig_insurance, use_container_width=True)
    else:
        st.warning("No insurance data available.")

st.markdown("---")

# ==========================
# Additional Visualizations
# ==========================

# Row 4: Year-over-Year Growth and State Rankings
st.markdown("## 📊 Advanced Analytics")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📈 Year-over-Year Growth")
    
    @st.cache_data
    def get_yoy_growth(states):
        """Get year-over-year growth rate"""
        conditions = []
        params = []
        
        if states:
            conditions.append("state = ANY(%s)")
            params.append(states)
        
        where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
        
        sql = f"""
            SELECT year, 
                   SUM(amount) AS total_amount,
                   SUM(count) AS total_transactions
            FROM aggregated_transaction
            {where_clause}
            GROUP BY year
            ORDER BY year;
        """
        df = run_query(sql, params=params if params else None)
        
        if len(df) > 1:
            df['amount_growth'] = df['total_amount'].pct_change() * 100
            df['txn_growth'] = df['total_transactions'].pct_change() * 100
        
        return df
    
    yoy_df = get_yoy_growth(selected_states)
    
    if not yoy_df.empty and len(yoy_df) > 1:
        fig_yoy = go.Figure()
        
        fig_yoy.add_trace(go.Bar(
            x=yoy_df['year'],
            y=yoy_df['amount_growth'],
            name='Amount Growth %',
            marker_color='#0abde3',
            text=yoy_df['amount_growth'].round(1),
            texttemplate='%{text}%',
            textposition='outside'
        ))
        
        fig_yoy.add_trace(go.Bar(
            x=yoy_df['year'],
            y=yoy_df['txn_growth'],
            name='Transaction Growth %',
            marker_color='#ee5a6f',
            text=yoy_df['txn_growth'].round(1),
            texttemplate='%{text}%',
            textposition='outside'
        ))
        
        fig_yoy.update_layout(
            title='Year-over-Year Growth Rate',
            xaxis_title='Year',
            yaxis_title='Growth Rate (%)',
            barmode='group',
            height=400,
            showlegend=True
        )
        
        st.plotly_chart(fig_yoy, use_container_width=True)
    else:
        st.info("Select multiple years for growth analysis")

with col2:
    st.markdown("### 🏅 State Performance Rankings")
    
    @st.cache_data
    def get_state_rankings(year, quarter):
        """Get comprehensive state rankings"""
        conditions = []
        params = []
        
        if year != 'All':
            conditions.append("year = %s")
            params.append(year)
        if quarter != 'All':
            conditions.append("quarter = %s")
            params.append(quarter)
        
        where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
        
        sql = f"""
            SELECT state,
                   SUM(amount) AS total_amount,
                   SUM(count) AS total_transactions,
                   AVG(amount/NULLIF(count, 0)) AS avg_transaction_value
            FROM aggregated_transaction
            {where_clause}
            GROUP BY state
            HAVING SUM(count) > 0
            ORDER BY total_amount DESC
            LIMIT 15;
        """
        return run_query(sql, params=params if params else None)
    
    rankings_df = get_state_rankings(year, quarter)
    
    if not rankings_df.empty:
        rankings_df['rank'] = range(1, len(rankings_df) + 1)
        
        # Create a scatter plot showing amount vs transactions
        fig_rankings = px.scatter(
            rankings_df,
            x='total_transactions',
            y='total_amount',
            size='avg_transaction_value',
            hover_data=['state', 'rank'],
            text='state',
            title='State Performance Matrix',
            labels={
                'total_transactions': 'Total Transactions',
                'total_amount': 'Total Amount (₹)',
                'avg_transaction_value': 'Avg Value'
            },
            color='avg_transaction_value',
            color_continuous_scale='Viridis'
        )
        
        fig_rankings.update_traces(textposition='top center', textfont_size=8)
        fig_rankings.update_layout(height=400)
        
        st.plotly_chart(fig_rankings, use_container_width=True)
    else:
        st.warning("No ranking data available")

st.markdown("---")

# Row 5: Map Visualization and Top Districts
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🗺️ Geographic Distribution")
    
    @st.cache_data
    def get_geographic_distribution(year, quarter):
        """Get state-wise distribution for choropleth"""
        conditions = []
        params = []
        
        if year != 'All':
            conditions.append("year = %s")
            params.append(year)
        if quarter != 'All':
            conditions.append("quarter = %s")
            params.append(quarter)
        
        where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
        
        sql = f"""
            SELECT state,
                   SUM(amount) AS total_amount,
                   SUM(count) AS total_transactions
            FROM aggregated_transaction
            {where_clause}
            GROUP BY state
            ORDER BY total_amount DESC;
        """
        return run_query(sql, params=params if params else None)
    
    geo_df = get_geographic_distribution(year, quarter)
    
    if not geo_df.empty:
        # Create a treemap
        fig_geo = px.treemap(
            geo_df.head(20),
            path=['state'],
            values='total_amount',
            title='Transaction Amount Distribution by State (Treemap)',
            color='total_transactions',
            color_continuous_scale='RdYlGn',
            hover_data=['total_transactions']
        )
        
        fig_geo.update_layout(height=400)
        st.plotly_chart(fig_geo, use_container_width=True)
    else:
        st.warning("No geographic data available")

with col2:
    st.markdown("### 🏙️ Top Districts")
    
    @st.cache_data
    def get_top_districts(year, quarter, states):
        """Get top districts by transaction amount"""
        conditions = []
        params = []
        
        if year != 'All':
            conditions.append("year = %s")
            params.append(year)
        if quarter != 'All':
            conditions.append("quarter = %s")
            params.append(quarter)
        if states:
            conditions.append("state = ANY(%s)")
            params.append(states)
        
        where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
        
        sql = f"""
            SELECT district,
                   SUM(amount) AS total_amount,
                   SUM(count) AS total_transactions
            FROM map_transaction
            {where_clause}
            GROUP BY district
            ORDER BY total_amount DESC
            LIMIT 10;
        """
        return run_query(sql, params=params if params else None)
    
    districts_df = get_top_districts(year, quarter, selected_states)
    
    if not districts_df.empty:
        fig_districts = px.bar(
            districts_df,
            y='district',
            x='total_amount',
            orientation='h',
            title='Top 10 Districts by Transaction Amount',
            labels={'total_amount': 'Total Amount (₹)', 'district': 'District'},
            color='total_amount',
            color_continuous_scale='Blues',
            text='total_amount'
        )
        
        fig_districts.update_traces(texttemplate='₹%{text:.2s}', textposition='outside')
        fig_districts.update_layout(height=400, showlegend=False)
        
        st.plotly_chart(fig_districts, use_container_width=True)
    else:
        st.warning("No district data available for selected filters")

st.markdown("---")

# Row 6: Transaction Value Analysis and Time Patterns
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 💵 Transaction Value Distribution")
    
    @st.cache_data
    def get_value_distribution(year, quarter):
        """Get transaction value distribution by type"""
        conditions = []
        params = []
        
        if year != 'All':
            conditions.append("year = %s")
            params.append(year)
        if quarter != 'All':
            conditions.append("quarter = %s")
            params.append(quarter)
        
        where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
        
        sql = f"""
            SELECT transaction_type,
                   SUM(amount) AS total_amount,
                   SUM(count) AS total_transactions,
                   AVG(amount/NULLIF(count, 0)) AS avg_value
            FROM aggregated_transaction
            {where_clause}
            GROUP BY transaction_type
            HAVING SUM(count) > 0
            ORDER BY avg_value DESC;
        """
        return run_query(sql, params=params if params else None)
    
    value_dist_df = get_value_distribution(year, quarter)
    
    if not value_dist_df.empty:
        fig_value = go.Figure()
        
        fig_value.add_trace(go.Bar(
            x=value_dist_df['transaction_type'],
            y=value_dist_df['avg_value'],
            marker_color='#5f27cd',
            text=value_dist_df['avg_value'].round(2),
            texttemplate='₹%{text}',
            textposition='outside',
            name='Avg Transaction Value'
        ))
        
        fig_value.update_layout(
            title='Average Transaction Value by Type',
            xaxis_title='Transaction Type',
            yaxis_title='Average Value (₹)',
            height=400,
            xaxis={'tickangle': -45}
        )
        
        st.plotly_chart(fig_value, use_container_width=True)
    else:
        st.warning("No value distribution data available")

with col2:
    st.markdown("### 📅 Quarterly Pattern Analysis")
    
    @st.cache_data
    def get_quarterly_patterns(year):
        """Get quarterly patterns across years"""
        conditions = []
        params = []
        
        if year != 'All':
            conditions.append("year = %s")
            params.append(year)
        
        where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
        
        sql = f"""
            SELECT quarter,
                   AVG(amount) AS avg_amount,
                   AVG(count) AS avg_transactions
            FROM aggregated_transaction
            {where_clause}
            GROUP BY quarter
            ORDER BY quarter;
        """
        return run_query(sql, params=params if params else None)
    
    pattern_df = get_quarterly_patterns(year)
    
    if not pattern_df.empty:
        fig_pattern = go.Figure()
        
        fig_pattern.add_trace(go.Scatterpolar(
            r=pattern_df['avg_amount'],
            theta=['Q' + str(q) for q in pattern_df['quarter']],
            fill='toself',
            name='Avg Amount',
            line_color='#0abde3'
        ))
        
        fig_pattern.update_layout(
            polar=dict(
                radialaxis=dict(visible=True)
            ),
            title='Quarterly Transaction Pattern (Radar Chart)',
            height=400
        )
        
        st.plotly_chart(fig_pattern, use_container_width=True)
    else:
        st.warning("No quarterly pattern data available")

st.markdown("---")

# Row 7: User Engagement and Insurance Trends
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 👥 User Engagement Metrics")
    
    @st.cache_data
    def get_user_engagement(year, quarter, states):
        """Get user engagement data"""
        conditions = []
        params = []
        
        if year != 'All':
            conditions.append("year = %s")
            params.append(year)
        if quarter != 'All':
            conditions.append("quarter = %s")
            params.append(quarter)
        if states:
            conditions.append("state = ANY(%s)")
            params.append(states)
        
        where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
        
        sql = f"""
            SELECT state,
                   SUM(registered_users) AS total_users,
                   SUM(app_opens) AS total_opens,
                   AVG(app_opens::float/NULLIF(registered_users, 0)) AS engagement_rate
            FROM map_user
            {where_clause}
            GROUP BY state
            HAVING SUM(registered_users) > 0
            ORDER BY engagement_rate DESC
            LIMIT 15;
        """
        return run_query(sql, params=params if params else None)
    
    engagement_df = get_user_engagement(year, quarter, selected_states)
    
    if not engagement_df.empty:
        fig_engagement = px.bar(
            engagement_df,
            x='state',
            y='engagement_rate',
            title='User Engagement Rate by State (App Opens per User)',
            labels={'engagement_rate': 'Engagement Rate', 'state': 'State'},
            color='engagement_rate',
            color_continuous_scale='Greens',
            text='engagement_rate'
        )
        
        fig_engagement.update_traces(texttemplate='%{text:.1f}', textposition='outside')
        fig_engagement.update_layout(height=400, xaxis={'tickangle': -45})
        
        st.plotly_chart(fig_engagement, use_container_width=True)
    else:
        st.warning("No user engagement data available")

with col2:
    st.markdown("### 🏥 Insurance Adoption Trends")
    
    @st.cache_data
    def get_insurance_trends(states):
        """Get insurance adoption trends"""
        conditions = []
        params = []
        
        if states:
            conditions.append("state = ANY(%s)")
            params.append(states)
        
        where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
        
        sql = f"""
            SELECT year, quarter,
                   SUM(amount) AS total_amount,
                   SUM(count) AS total_count
            FROM aggregated_insurance
            {where_clause}
            GROUP BY year, quarter
            ORDER BY year, quarter;
        """
        return run_query(sql, params=params if params else None)
    
    ins_trends_df = get_insurance_trends(selected_states)
    
    if not ins_trends_df.empty:
        ins_trends_df['period'] = ins_trends_df['year'].astype(str) + '-Q' + ins_trends_df['quarter'].astype(str)
        
        fig_ins = go.Figure()
        
        fig_ins.add_trace(go.Scatter(
            x=ins_trends_df['period'],
            y=ins_trends_df['total_count'],
            mode='lines+markers',
            name='Insurance Transactions',
            line=dict(color='#ee5a6f', width=3),
            marker=dict(size=8),
            fill='tozeroy',
            fillcolor='rgba(238, 90, 111, 0.2)'
        ))
        
        fig_ins.update_layout(
            title='Insurance Transaction Trends Over Time',
            xaxis_title='Period',
            yaxis_title='Number of Transactions',
            height=400,
            xaxis={'tickangle': -45}
        )
        
        st.plotly_chart(fig_ins, use_container_width=True)
    else:
        st.warning("No insurance trend data available")

st.markdown("---")

# Row 8: Comparative Analysis
st.markdown("### 🔍 Comparative Analysis")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Top 5 vs Bottom 5 States")
    
    @st.cache_data
    def get_top_bottom_states(year, quarter):
        """Get top and bottom performing states"""
        conditions = []
        params = []
        
        if year != 'All':
            conditions.append("year = %s")
            params.append(year)
        if quarter != 'All':
            conditions.append("quarter = %s")
            params.append(quarter)
        
        where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
        
        sql = f"""
            WITH ranked_states AS (
                SELECT state,
                       SUM(amount) AS total_amount,
                       ROW_NUMBER() OVER (ORDER BY SUM(amount) DESC) as rank_desc,
                       ROW_NUMBER() OVER (ORDER BY SUM(amount) ASC) as rank_asc
                FROM aggregated_transaction
                {where_clause}
                GROUP BY state
                HAVING state != 'All'
            )
            SELECT state, total_amount,
                   CASE WHEN rank_desc <= 5 THEN 'Top 5'
                        WHEN rank_asc <= 5 THEN 'Bottom 5'
                   END as category
            FROM ranked_states
            WHERE rank_desc <= 5 OR rank_asc <= 5
            ORDER BY total_amount DESC;
        """
        return run_query(sql, params=params if params else None)
    
    comp_df = get_top_bottom_states(year, quarter)
    
    if not comp_df.empty:
        fig_comp = px.bar(
            comp_df,
            x='total_amount',
            y='state',
            orientation='h',
            color='category',
            title='Top 5 vs Bottom 5 States by Transaction Amount',
            labels={'total_amount': 'Total Amount (₹)', 'state': 'State'},
            color_discrete_map={'Top 5': '#10ac84', 'Bottom 5': '#ee5a6f'}
        )
        
        fig_comp.update_layout(height=400)
        st.plotly_chart(fig_comp, use_container_width=True)
    else:
        st.info("Comparative data not available")

with col2:
    st.markdown("#### Transaction Mix by State")
    
    @st.cache_data
    def get_transaction_mix(year, quarter):
        """Get transaction type distribution for top states"""
        conditions_cte = ["state != 'All'"]
        conditions_main = ["t.state != 'All'"]
        params = []
        params_cte = []

        if year != 'All':
            conditions_cte.append("year = %s")
            conditions_main.append("t.year = %s")
            params.append(year)
            params_cte.append(year)
        if quarter != 'All':
            conditions_cte.append("quarter = %s")
            conditions_main.append("t.quarter = %s")
            params.append(quarter)
            params_cte.append(quarter)

        where_clause_cte = "WHERE " + " AND ".join(conditions_cte)
        where_clause_main = "WHERE " + " AND ".join(conditions_main)

        # Combine parameters (CTE params + main query params)
        all_params = params_cte + params

        sql = f"""
            WITH top_states AS (
                SELECT state
                FROM aggregated_transaction
                {where_clause_cte}
                GROUP BY state
                ORDER BY SUM(amount) DESC
                LIMIT 5
            )
            SELECT t.state, t.transaction_type, SUM(t.amount) as total_amount
            FROM aggregated_transaction t
            INNER JOIN top_states ts ON t.state = ts.state
            {where_clause_main}
            GROUP BY t.state, t.transaction_type
            ORDER BY t.state, total_amount DESC;
        """
        return run_query(sql, params=all_params if all_params else None)
    
    mix_df = get_transaction_mix(year, quarter)
    
    if not mix_df.empty:
        fig_mix = px.bar(
            mix_df,
            x='state',
            y='total_amount',
            color='transaction_type',
            title='Transaction Type Mix for Top 5 States',
            labels={'total_amount': 'Total Amount (₹)', 'state': 'State'},
            barmode='stack'
        )
        
        fig_mix.update_layout(height=400, xaxis={'tickangle': -45})
        st.plotly_chart(fig_mix, use_container_width=True)
    else:
        st.info("Transaction mix data not available")

st.markdown("---")

# ==========================
# 📚 Business Case Studies
# ==========================

st.markdown("## 📚 Business Case Studies")
case_tab1, case_tab2, case_tab3, case_tab4, case_tab5 = st.tabs([
    "1) Transaction Dynamics",
    "2) Device Dominance",
    "3) Insurance Penetration",
    "4) Market Expansion",
    "5) User Registration"
])

@st.cache_data
def get_txn_by_type_trend(year, states):
    conditions = []
    params = []
    if year != 'All':
        conditions.append("year = %s")
        params.append(year)
    if states:
        conditions.append("state = ANY(%s)")
        params.append(states)
    where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
    sql = f"""
        SELECT year, quarter, transaction_type,
               SUM(amount) AS total_amount
        FROM aggregated_transaction
        {where_clause}
        GROUP BY year, quarter, transaction_type
        ORDER BY year, quarter, transaction_type;
    """
    return run_query(sql, params=params if params else None)

@st.cache_data
def get_insurance_penetration(year, quarter, states):
    conditions = []
    params = []
    if year != 'All':
        conditions.append("year = %s")
        params.append(year)
    if quarter != 'All':
        conditions.append("quarter = %s")
        params.append(quarter)
    if states:
        conditions.append("state = ANY(%s)")
        params.append(states)
    where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

    sql_ins = f"""
        SELECT state, SUM(amount) AS insurance_amount
        FROM aggregated_insurance
        {where_clause}
        GROUP BY state
    """
    sql_txn = f"""
        SELECT state, SUM(amount) AS txn_amount
        FROM aggregated_transaction
        {where_clause}
        GROUP BY state
    """
    ins_df = run_query(sql_ins, params=params if params else None)
    txn_df = run_query(sql_txn, params=params if params else None)
    if ins_df.empty or txn_df.empty:
        return pd.DataFrame(columns=['state','insurance_amount','txn_amount','penetration'])
    merged = pd.merge(txn_df, ins_df, on='state', how='left').fillna({'insurance_amount': 0})
    merged['penetration'] = merged.apply(lambda r: (r['insurance_amount']/r['txn_amount']) if r['txn_amount'] else 0, axis=1)
    return merged.sort_values('penetration', ascending=False)

@st.cache_data
def get_registrations_trend(year, states):
    conditions = []
    params = []
    if year != 'All':
        conditions.append("year = %s")
        params.append(year)
    if states:
        conditions.append("state = ANY(%s)")
        params.append(states)
    where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
    sql = f"""
        SELECT year, quarter, SUM(registered_users) AS registered_users
        FROM map_user
        {where_clause}
        GROUP BY year, quarter
        ORDER BY year, quarter;
    """
    return run_query(sql, params=params if params else None)

with case_tab1:
    st.markdown("### 1) Transaction Dynamics by Type")
    tdf = get_txn_by_type_trend(year, selected_states)
    if not tdf.empty:
        tdf['period'] = tdf['year'].astype(str) + '-Q' + tdf['quarter'].astype(str)
        fig = px.line(tdf, x='period', y='total_amount', color='transaction_type', markers=True,
                      title='Amount Trend by Transaction Type')
        fig.update_layout(height=420, xaxis={'tickangle': -45})
        st.plotly_chart(fig, use_container_width=True)
        # Stacked area: type share over time
        area_df = tdf.copy()
        area_piv = area_df.pivot_table(index='period', columns='transaction_type', values='total_amount', aggfunc='sum').fillna(0)
        area_piv = area_piv.sort_index()
        area_fig = go.Figure()
        for col in area_piv.columns:
            area_fig.add_trace(go.Scatter(x=area_piv.index, y=area_piv[col], stackgroup='one', name=col, mode='lines'))
        area_fig.update_layout(title='Transaction Type Stack over Time', height=420)
        st.plotly_chart(area_fig, use_container_width=True)
        st.download_button("⬇️ Download (CSV)", tdf.to_csv(index=False), file_name="txn_dynamics_by_type.csv", mime="text/csv")
    else:
        st.info("No data for selected filters.")

with case_tab2:
    st.markdown("### 2) Device Dominance and Engagement")
    ddf = get_device_distribution(year, quarter, selected_states)
    if not ddf.empty:
        fig = px.scatter(ddf, x='avg_percentage', y='total_users', size='total_users', color='device_brand',
                         hover_data=['device_brand','total_users','avg_percentage'],
                         title='Device Brand: Users vs Avg % Share')
        fig.update_layout(height=420)
        st.plotly_chart(fig, use_container_width=True)
        # Device brand share (% of users)
        dshare = ddf[['device_brand','total_users']].copy()
        total = dshare['total_users'].sum()
        if total:
            dshare['share_pct'] = (dshare['total_users'] / total) * 100
            dshare = dshare.sort_values('share_pct', ascending=True)
            bar = px.bar(dshare, y='device_brand', x='share_pct', orientation='h', title='Device Brand Share (%)')
            bar.update_layout(height=420)
            st.plotly_chart(bar, use_container_width=True)
        st.download_button("⬇️ Download (CSV)", ddf.to_csv(index=False), file_name="device_dominance.csv", mime="text/csv")
    else:
        st.info("No device data for selected filters.")

with case_tab3:
    st.markdown("### 3) Insurance Penetration by State")
    ip_df = get_insurance_penetration(year, quarter, selected_states)
    if not ip_df.empty:
        topn = ip_df.head(15)
        fig = px.bar(topn, x='state', y='penetration', color='insurance_amount',
                     labels={'penetration':'Insurance Penetration (Amt / Total Txn Amt)'},
                     title='Top States by Insurance Penetration')
        fig.update_layout(height=420, xaxis={'tickangle': -45})
        st.plotly_chart(fig, use_container_width=True)
        # YoY growth in insurance amount
        @st.cache_data
        def insurance_yoy(states):
            cond = []
            params = []
            if states:
                cond.append("state = ANY(%s)")
                params.append(states)
            w = "WHERE " + " AND ".join(cond) if cond else ""
            sql = f"""
                SELECT year, SUM(amount) AS total_amount
                FROM aggregated_insurance
                {w}
                GROUP BY year
                ORDER BY year;
            """
            df = run_query(sql, params=params if params else None)
            if len(df) > 1:
                df['yoy_pct'] = df['total_amount'].pct_change() * 100
            return df
        yoy = insurance_yoy(selected_states)
        if not yoy.empty and 'yoy_pct' in yoy.columns:
            yoy_fig = px.bar(yoy, x='year', y='yoy_pct', title='Insurance Amount YoY Growth (%)', text=yoy['yoy_pct'].round(1))
            yoy_fig.update_traces(textposition='outside')
            yoy_fig.update_layout(height=420)
            st.plotly_chart(yoy_fig, use_container_width=True)
        st.download_button("⬇️ Download (CSV)", ip_df.to_csv(index=False), file_name="insurance_penetration.csv", mime="text/csv")
    else:
        st.info("No insurance/transaction data for penetration computation.")

with case_tab4:
    st.markdown("### 4) Market Expansion: Transaction Mix (Top States)")
    mx = get_transaction_mix(year, quarter)
    if not mx.empty:
        # Normalize to shares
        piv = mx.pivot_table(index='state', columns='transaction_type', values='total_amount', aggfunc='sum').fillna(0)
        row_sums = piv.sum(axis=1)
        share = piv.div(row_sums, axis=0)
        fig = px.imshow(share, aspect='auto', color_continuous_scale='YlGnBu',
                        labels=dict(color='Share'), title='Transaction Type Share by Top States (Heatmap)')
        st.plotly_chart(fig, use_container_width=True)
        # Stacked bar for amounts
        mx_sorted = mx.sort_values(['state','total_amount'], ascending=[True, False])
        stack = px.bar(mx_sorted, x='state', y='total_amount', color='transaction_type', barmode='stack',
                       title='Transaction Amounts by Type (Top States)')
        stack.update_layout(height=420, xaxis={'tickangle': -45})
        st.plotly_chart(stack, use_container_width=True)
        st.download_button("⬇️ Download (CSV)", share.reset_index().to_csv(index=False), file_name="market_expansion_mix.csv", mime="text/csv")
    else:
        st.info("No transaction mix data available.")

with case_tab5:
    st.markdown("### 5) User Registration Trend")
    rtr = get_registrations_trend(year, selected_states)
    if not rtr.empty:
        rtr['period'] = rtr['year'].astype(str) + '-Q' + rtr['quarter'].astype(str)
        fig = px.line(rtr, x='period', y='registered_users', markers=True,
                      title='Registered Users Trend')
        fig.update_layout(height=420, xaxis={'tickangle': -45})
        st.plotly_chart(fig, use_container_width=True)
        # Top states by registered users
        @st.cache_data
        def top_registered_states(year, states):
            cond = []
            params = []
            if year != 'All':
                cond.append("year = %s")
                params.append(year)
            if states:
                cond.append("state = ANY(%s)")
                params.append(states)
            w = "WHERE " + " AND ".join(cond) if cond else ""
            sql = f"""
                SELECT state, SUM(registered_users) AS users
                FROM map_user
                {w}
                GROUP BY state
                ORDER BY users DESC
                LIMIT 10;
            """
            return run_query(sql, params=params if params else None)
        topu = top_registered_states(year, selected_states)
        if not topu.empty:
            bar = px.bar(topu, x='state', y='users', title='Top States by Registered Users', color='users')
            bar.update_layout(height=420, xaxis={'tickangle': -45})
            st.plotly_chart(bar, use_container_width=True)
        st.download_button("⬇️ Download (CSV)", rtr.to_csv(index=False), file_name="registration_trend.csv", mime="text/csv")
    else:
        st.info("No registration data for selected filters.")

# Spacer
st.markdown("---")

# ==========================
# 📚 Business Case Studies — Advanced
# ==========================
st.markdown("## 📚 Business Case Studies — Advanced")
adv1, adv2, adv3, adv4, adv5 = st.tabs([
    "6) Seasonality Index",
    "7) Merchant vs P2P",
    "8) Volatility by State",
    "9) Emerging States",
    "10) High-Value Types"
])

@st.cache_data
def get_state_quarter_amount(year, states):
    cond, params = [], []
    if year != 'All':
        cond.append("year = %s"); params.append(year)
    if states:
        cond.append("state = ANY(%s)"); params.append(states)
    w = "WHERE " + " AND ".join(cond) if cond else ""
    sql = f"""
        SELECT state, year, quarter, SUM(amount) AS total_amount
        FROM aggregated_transaction
        {w}
        GROUP BY state, year, quarter
        ORDER BY state, year, quarter;
    """
    return run_query(sql, params=params if params else None)

with adv1:
    st.markdown("### 6) Seasonality Index (per State)")
    sq = get_state_quarter_amount(year, selected_states)
    if not sq.empty:
        # Compute index: quarter amount / state yearly average
        df = sq.copy()
        yearly = df.groupby(['state','year'], as_index=False)['total_amount'].mean().rename(columns={'total_amount':'year_avg'})
        df = df.merge(yearly, on=['state','year'], how='left')
        df['seasonality_idx'] = df.apply(lambda r: (r['total_amount']/r['year_avg']) if r['year_avg'] else 0, axis=1)
        heat = df.pivot_table(index='state', columns='quarter', values='seasonality_idx', aggfunc='mean').fillna(0)
        fig = px.imshow(heat, aspect='auto', color_continuous_scale='RdBu', origin='lower',
                        labels=dict(color='Index'), title='Seasonality Index by State (Q vs State-Year Avg)')
        st.plotly_chart(fig, use_container_width=True)
        st.download_button("⬇️ Download (CSV)", df.to_csv(index=False), file_name="seasonality_index.csv", mime="text/csv")
    else:
        st.info("No data available for selected filters.")

@st.cache_data
def get_merchant_p2p_share(year, states):
    cond, params = [], []
    if year != 'All': cond.append("year = %s"); params.append(year)
    if states: cond.append("state = ANY(%s)"); params.append(states)
    w = "WHERE " + " AND ".join(cond) if cond else ""
    sql = f"""
        SELECT state,
               SUM(CASE WHEN transaction_type = 'Merchant payments' THEN amount ELSE 0 END) AS merchant_amt,
               SUM(CASE WHEN transaction_type = 'Peer-to-peer payments' THEN amount ELSE 0 END) AS p2p_amt
        FROM aggregated_transaction
        {w}
        GROUP BY state
    """
    return run_query(sql, params=params if params else None)

with adv2:
    st.markdown("### 7) Merchant vs P2P Balance")
    mp = get_merchant_p2p_share(year, selected_states)
    if not mp.empty:
        mp['merchant_share'] = mp.apply(lambda r: r['merchant_amt']/ (r['merchant_amt']+r['p2p_amt']) if (r['merchant_amt']+r['p2p_amt']) else 0, axis=1)
        mp['p2p_share'] = 1 - mp['merchant_share']
        mp_long = mp.melt(id_vars=['state'], value_vars=['merchant_share','p2p_share'], var_name='type', value_name='share')
        fig = px.bar(mp_long, x='state', y='share', color='type', barmode='stack', title='Merchant vs P2P Share by State')
        fig.update_layout(height=420, xaxis={'tickangle': -45})
        st.plotly_chart(fig, use_container_width=True)
        st.download_button("⬇️ Download (CSV)", mp.to_csv(index=False), file_name="merchant_p2p_share.csv", mime="text/csv")
    else:
        st.info("No data available for selected filters.")

@st.cache_data
def get_state_volatility(year, states):
    df = get_state_quarter_amount(year, states)
    if df.empty:
        return df
    g = df.groupby('state')['total_amount']
    stats = g.agg(['mean','std']).reset_index()
    stats['cv'] = stats.apply(lambda r: (r['std']/r['mean']) if r['mean'] else 0, axis=1)
    return stats.sort_values('cv', ascending=False)

with adv3:
    st.markdown("### 8) Volatility by State (Coefficient of Variation)")
    vol = get_state_volatility(year, selected_states)
    if not vol.empty:
        fig = px.bar(vol.head(20), x='state', y='cv', title='State Volatility (Top 20 by CV)', color='cv')
        fig.update_layout(height=420, xaxis={'tickangle': -45})
        st.plotly_chart(fig, use_container_width=True)
        st.download_button("⬇️ Download (CSV)", vol.to_csv(index=False), file_name="state_volatility.csv", mime="text/csv")
    else:
        st.info("No data available for selected filters.")

@st.cache_data
def get_state_cagr_and_share(states):
    cond, params = [], []
    if states: cond.append("state = ANY(%s)" ); params.append(states)
    w = "WHERE " + " AND ".join(cond) if cond else ""
    sql = f"""
        SELECT state, year, SUM(amount) AS total_amount
        FROM aggregated_transaction
        {w}
        GROUP BY state, year
        ORDER BY state, year
    """
    df = run_query(sql, params=params if params else None)
    if df.empty:
        return df
    # Compute CAGR per state (first to last year present)
    out = []
    for s, g in df.groupby('state'):
        g = g.sort_values('year')
        first, last = g['total_amount'].iloc[0], g['total_amount'].iloc[-1]
        n = max(1, len(g['year'].unique())-1)
        cagr = ( (last/first)**(1/n) - 1)*100 if first and n>0 else 0
        out.append({'state': s, 'cagr_pct': cagr, 'latest_amount': last})
    out_df = pd.DataFrame(out)
    total_latest = out_df['latest_amount'].sum()
    out_df['latest_share_pct'] = out_df['latest_amount']/total_latest*100 if total_latest else 0
    return out_df

with adv4:
    st.markdown("### 9) Emerging States (CAGR vs Share)")
    em = get_state_cagr_and_share(selected_states)
    if not em.empty:
        fig = px.scatter(em, x='latest_share_pct', y='cagr_pct', size='latest_amount', color='cagr_pct',
                         hover_data=['state','latest_amount'], title='Emerging States: Growth vs Current Share')
        fig.update_layout(height=420)
        st.plotly_chart(fig, use_container_width=True)
        st.download_button("⬇️ Download (CSV)", em.to_csv(index=False), file_name="emerging_states.csv", mime="text/csv")
    else:
        st.info("No data available for selected filters.")

@st.cache_data
def get_avg_value_by_type(year, states):
    cond, params = [], []
    if year != 'All': cond.append("year = %s"); params.append(year)
    if states: cond.append("state = ANY(%s)"); params.append(states)
    w = "WHERE " + " AND ".join(cond) if cond else ""
    sql = f"""
        SELECT state, transaction_type,
               SUM(amount) AS total_amount,
               SUM(count) AS total_count
        FROM aggregated_transaction
        {w}
        GROUP BY state, transaction_type
    """
    df = run_query(sql, params=params if params else None)
    if df.empty:
        return df
    df['avg_value'] = df.apply(lambda r: (r['total_amount']/r['total_count']) if r['total_count'] else 0, axis=1)
    return df

with adv5:
    st.markdown("### 10) High-Value Transaction Types (Distribution)")
    hv = get_avg_value_by_type(year, selected_states)
    if not hv.empty:
        fig = px.box(hv, x='transaction_type', y='avg_value', points='all', title='Avg Transaction Value by Type (across States)')
        fig.update_layout(height=420, xaxis={'tickangle': -30})
        st.plotly_chart(fig, use_container_width=True)
        st.download_button("⬇️ Download (CSV)", hv.to_csv(index=False), file_name="high_value_types.csv", mime="text/csv")
    else:
        st.info("No data available for selected filters.")

# ==========================
# Download Section
# ==========================
st.markdown("## 📥 Download Data")

col1, col2, col3 = st.columns(3)

with col1:
    if not top_states_df.empty:
        csv_states = top_states_df.to_csv(index=False)
        st.download_button(
            label="📊 Download Top States Data",
            data=csv_states,
            file_name=f"top_states_{year}_{quarter}.csv",
            mime="text/csv"
        )

with col2:
    if not trends_df.empty:
        csv_trends = trends_df.to_csv(index=False)
        st.download_button(
            label="📈 Download Trends Data",
            data=csv_trends,
            file_name=f"quarterly_trends_{year}.csv",
            mime="text/csv"
        )

with col3:
    if not device_df.empty:
        csv_device = device_df.to_csv(index=False)
        st.download_button(
            label="📱 Download Device Data",
            data=csv_device,
            file_name=f"device_distribution_{year}_{quarter}.csv",
            mime="text/csv"
        )

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>📱 PhonePe Pulse Dashboard | Data Source: PhonePe Pulse Repository</p>
        <p>Built with Streamlit 🎈 | Last Updated: October 2025</p>
    </div>
""", unsafe_allow_html=True)
