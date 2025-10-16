"""
PhonePe Pulse Data Visualization Module
Creates publication-ready figures for README and presentations
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from run_queries import run_query

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10

# Create output directory
OUTPUT_DIR = "figs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def save_figure(fig, filename, dpi=300):
    """Save matplotlib figure"""
    filepath = os.path.join(OUTPUT_DIR, filename)
    fig.savefig(filepath, dpi=dpi, bbox_inches='tight')
    print(f"✅ Saved: {filepath}")
    plt.close(fig)

def save_plotly_figure(fig, filename):
    """Save plotly figure as HTML and PNG"""
    html_path = os.path.join(OUTPUT_DIR, filename.replace('.png', '.html'))
    png_path = os.path.join(OUTPUT_DIR, filename)
    
    fig.write_html(html_path)
    print(f"✅ Saved: {html_path}")
    
    try:
        fig.write_image(png_path, width=1200, height=600)
        print(f"✅ Saved: {png_path}")
    except Exception as e:
        print(f"⚠️  Could not save PNG (install kaleido): {e}")

# ==========================
# 1. Top 10 States Bar Chart
# ==========================
def plot_top_states():
    """Bar chart showing top 10 states by transaction amount"""
    sql = """
        SELECT state, SUM(amount) AS total_amount, SUM(count) AS total_transactions
        FROM aggregated_transaction
        GROUP BY state
        ORDER BY total_amount DESC
        LIMIT 10;
    """
    df = run_query(sql)
    
    # Matplotlib version
    fig, ax = plt.subplots(figsize=(12, 6))
    bars = ax.barh(df['state'], df['total_amount'] / 1e9, color=sns.color_palette("viridis", len(df)))
    ax.set_xlabel('Total Amount (Billion ₹)', fontsize=12, fontweight='bold')
    ax.set_ylabel('State', fontsize=12, fontweight='bold')
    ax.set_title('Top 10 States by Transaction Amount', fontsize=14, fontweight='bold')
    ax.invert_yaxis()
    
    # Add value labels
    for i, (amount, state) in enumerate(zip(df['total_amount'], df['state'])):
        ax.text(amount/1e9 + 0.5, i, f'₹{amount/1e9:.1f}B', 
                va='center', fontsize=9, fontweight='bold')
    
    plt.tight_layout()
    save_figure(fig, 'top_10_states.png')
    
    # Plotly version
    fig_plotly = px.bar(
        df, 
        x='total_amount', 
        y='state',
        orientation='h',
        title='Top 10 States by Transaction Amount',
        labels={'total_amount': 'Total Amount (₹)', 'state': 'State'},
        color='total_amount',
        color_continuous_scale='Viridis',
        text='total_amount'
    )
    fig_plotly.update_traces(texttemplate='₹%{text:.2s}', textposition='outside')
    fig_plotly.update_layout(showlegend=False, height=500)
    save_plotly_figure(fig_plotly, 'top_10_states_interactive.png')

# ==========================
# 2. Quarterly Trends Line Chart
# ==========================
def plot_quarterly_trends():
    """Line chart showing quarterly transaction trends"""
    sql = """
        SELECT year, quarter, SUM(amount) AS total_amount, SUM(count) AS total_transactions
        FROM aggregated_transaction
        GROUP BY year, quarter
        ORDER BY year, quarter;
    """
    df = run_query(sql)
    df['period'] = df['year'].astype(str) + '-Q' + df['quarter'].astype(str)
    
    # Matplotlib version
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8))
    
    # Amount trend
    ax1.plot(df['period'], df['total_amount'] / 1e12, marker='o', linewidth=2, 
             color='#5f27cd', markersize=6)
    ax1.set_ylabel('Total Amount (Trillion ₹)', fontsize=11, fontweight='bold')
    ax1.set_title('Quarterly Transaction Amount Trends', fontsize=13, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.tick_params(axis='x', rotation=45)
    
    # Transaction count trend
    ax2.plot(df['period'], df['total_transactions'] / 1e9, marker='s', linewidth=2, 
             color='#0abde3', markersize=6)
    ax2.set_xlabel('Quarter', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Total Transactions (Billion)', fontsize=11, fontweight='bold')
    ax2.set_title('Quarterly Transaction Count Trends', fontsize=13, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    save_figure(fig, 'quarterly_trends.png')
    
    # Plotly version
    fig_plotly = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Transaction Amount Over Time', 'Transaction Count Over Time'),
        vertical_spacing=0.12
    )
    
    fig_plotly.add_trace(
        go.Scatter(x=df['period'], y=df['total_amount']/1e12, mode='lines+markers',
                   name='Amount (Trillion ₹)', line=dict(color='#5f27cd', width=3)),
        row=1, col=1
    )
    
    fig_plotly.add_trace(
        go.Scatter(x=df['period'], y=df['total_transactions']/1e9, mode='lines+markers',
                   name='Count (Billion)', line=dict(color='#0abde3', width=3)),
        row=2, col=1
    )
    
    fig_plotly.update_xaxes(tickangle=45)
    fig_plotly.update_layout(height=700, showlegend=False)
    save_plotly_figure(fig_plotly, 'quarterly_trends_interactive.png')

# ==========================
# 3. Device Distribution Pie Chart
# ==========================
def plot_device_distribution():
    """Pie chart showing device brand distribution"""
    sql = """
        SELECT device_brand, SUM(user_count) AS total_users
        FROM aggregated_user
        GROUP BY device_brand
        ORDER BY total_users DESC
        LIMIT 10;
    """
    df = run_query(sql)
    
    # Matplotlib version
    fig, ax = plt.subplots(figsize=(10, 8))
    colors = sns.color_palette("Set3", len(df))
    wedges, texts, autotexts = ax.pie(
        df['total_users'], 
        labels=df['device_brand'],
        autopct='%1.1f%%',
        startangle=90,
        colors=colors,
        textprops={'fontsize': 10, 'fontweight': 'bold'}
    )
    ax.set_title('Device Brand Distribution by User Count', fontsize=14, fontweight='bold', pad=20)
    
    # Make percentage text more visible
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontsize(9)
    
    plt.tight_layout()
    save_figure(fig, 'device_distribution.png')
    
    # Plotly version
    fig_plotly = px.pie(
        df,
        values='total_users',
        names='device_brand',
        title='Device Brand Distribution',
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig_plotly.update_traces(textposition='inside', textinfo='percent+label')
    fig_plotly.update_layout(height=600)
    save_plotly_figure(fig_plotly, 'device_distribution_interactive.png')

# ==========================
# 4. Insurance vs Transaction Comparison
# ==========================
def plot_insurance_comparison():
    """Bar chart comparing insurance and transaction amounts by state"""
    # Get top 10 states by transaction
    transaction_sql = """
        SELECT state, SUM(amount) AS transaction_amount
        FROM aggregated_transaction
        GROUP BY state
        ORDER BY transaction_amount DESC
        LIMIT 10;
    """
    txn_df = run_query(transaction_sql)
    
    # Get insurance data for same states
    states = "','".join(txn_df['state'].tolist())
    insurance_sql = f"""
        SELECT state, SUM(amount) AS insurance_amount
        FROM aggregated_insurance
        WHERE state IN ('{states}')
        GROUP BY state;
    """
    ins_df = run_query(insurance_sql)
    
    # Merge dataframes
    comparison_df = txn_df.merge(ins_df, on='state', how='left')
    comparison_df['insurance_amount'].fillna(0, inplace=True)
    
    # Matplotlib version
    fig, ax = plt.subplots(figsize=(14, 7))
    x = range(len(comparison_df))
    width = 0.35
    
    bars1 = ax.bar([i - width/2 for i in x], comparison_df['transaction_amount'] / 1e9, 
                    width, label='Transactions', color='#0abde3', alpha=0.8)
    bars2 = ax.bar([i + width/2 for i in x], comparison_df['insurance_amount'] / 1e6, 
                    width, label='Insurance', color='#ee5a6f', alpha=0.8)
    
    ax.set_xlabel('State', fontsize=12, fontweight='bold')
    ax.set_ylabel('Amount (Billion ₹ for Txn, Million ₹ for Insurance)', fontsize=11, fontweight='bold')
    ax.set_title('Transaction vs Insurance Amount Comparison by State', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(comparison_df['state'], rotation=45, ha='right')
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    save_figure(fig, 'insurance_comparison.png')
    
    # Plotly version
    fig_plotly = go.Figure()
    fig_plotly.add_trace(go.Bar(
        x=comparison_df['state'],
        y=comparison_df['transaction_amount']/1e9,
        name='Transactions (Billion ₹)',
        marker_color='#0abde3'
    ))
    fig_plotly.add_trace(go.Bar(
        x=comparison_df['state'],
        y=comparison_df['insurance_amount']/1e6,
        name='Insurance (Million ₹)',
        marker_color='#ee5a6f'
    ))
    
    fig_plotly.update_layout(
        title='Transaction vs Insurance Amount Comparison',
        xaxis_title='State',
        yaxis_title='Amount',
        barmode='group',
        height=600
    )
    save_plotly_figure(fig_plotly, 'insurance_comparison_interactive.png')

# ==========================
# 5. Transaction Type Breakdown
# ==========================
def plot_transaction_types():
    """Stacked bar chart showing transaction type distribution by year"""
    sql = """
        SELECT year, transaction_type, SUM(amount) AS total_amount
        FROM aggregated_transaction
        GROUP BY year, transaction_type
        ORDER BY year, total_amount DESC;
    """
    df = run_query(sql)
    
    # Pivot for stacked bar
    pivot_df = df.pivot(index='year', columns='transaction_type', values='total_amount').fillna(0)
    
    # Matplotlib version
    fig, ax = plt.subplots(figsize=(14, 7))
    pivot_df.div(1e12).plot(kind='bar', stacked=True, ax=ax, 
                             colormap='tab10', width=0.7)
    
    ax.set_xlabel('Year', fontsize=12, fontweight='bold')
    ax.set_ylabel('Total Amount (Trillion ₹)', fontsize=12, fontweight='bold')
    ax.set_title('Transaction Type Distribution by Year', fontsize=14, fontweight='bold')
    ax.legend(title='Transaction Type', bbox_to_anchor=(1.05, 1), loc='upper left')
    ax.set_xticklabels(pivot_df.index, rotation=0)
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    save_figure(fig, 'transaction_types_yearly.png')

# ==========================
# 6. Geographic Heatmap
# ==========================
def plot_state_heatmap():
    """Heatmap showing transaction amount by state and year"""
    sql = """
        SELECT state, year, SUM(amount) AS total_amount
        FROM aggregated_transaction
        GROUP BY state, year
        ORDER BY state, year;
    """
    df = run_query(sql)
    
    # Pivot for heatmap
    pivot_df = df.pivot(index='state', columns='year', values='total_amount').fillna(0)
    
    # Matplotlib version
    fig, ax = plt.subplots(figsize=(12, 18))
    sns.heatmap(pivot_df / 1e9, annot=True, fmt='.1f', cmap='YlOrRd', 
                cbar_kws={'label': 'Amount (Billion ₹)'}, ax=ax, linewidths=0.5)
    
    ax.set_title('Transaction Amount Heatmap by State and Year', fontsize=14, fontweight='bold', pad=20)
    ax.set_xlabel('Year', fontsize=12, fontweight='bold')
    ax.set_ylabel('State', fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    save_figure(fig, 'state_year_heatmap.png')

# ==========================
# Main Execution
# ==========================
if __name__ == "__main__":
    print("🎨 Generating PhonePe Pulse Visualizations...\n")
    
    try:
        print("1️⃣  Creating Top 10 States chart...")
        plot_top_states()
        
        print("\n2️⃣  Creating Quarterly Trends chart...")
        plot_quarterly_trends()
        
        print("\n3️⃣  Creating Device Distribution chart...")
        plot_device_distribution()
        
        print("\n4️⃣  Creating Insurance Comparison chart...")
        plot_insurance_comparison()
        
        print("\n5️⃣  Creating Transaction Types chart...")
        plot_transaction_types()
        
        print("\n6️⃣  Creating State Heatmap...")
        plot_state_heatmap()
        
        print("\n✨ All visualizations generated successfully!")
        print(f"📁 Figures saved in: {os.path.abspath(OUTPUT_DIR)}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
