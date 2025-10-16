"""
Test script to verify dashboard queries work correctly
Run this before starting the Streamlit app
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from analysis.run_queries import run_query
import pandas as pd

def test_query(name, sql, params=None):
    """Test a single query"""
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print(f"{'='*60}")
    try:
        df = run_query(sql, params=params)
        print(f"✅ Success! Returned {len(df)} rows")
        print("\nFirst 5 rows:")
        print(df.head())
        print(f"\nColumns: {list(df.columns)}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("🧪 PhonePe Pulse Dashboard Query Tests")
    print("="*60)
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Top States
    tests_total += 1
    sql1 = """
        SELECT state, SUM(amount) AS total_amount, SUM(count) AS total_transactions
        FROM aggregated_transaction
        WHERE year = %s
        GROUP BY state
        ORDER BY total_amount DESC
        LIMIT 10;
    """
    if test_query("Top 10 States (2023)", sql1, params=[2023]):
        tests_passed += 1
    
    # Test 2: Quarterly Trends
    tests_total += 1
    sql2 = """
        SELECT year, quarter, SUM(amount) AS total_amount, SUM(count) AS total_transactions
        FROM aggregated_transaction
        GROUP BY year, quarter
        ORDER BY year, quarter;
    """
    if test_query("Quarterly Trends", sql2):
        tests_passed += 1
    
    # Test 3: Device Distribution
    tests_total += 1
    sql3 = """
        SELECT device_brand, SUM(user_count) AS total_users, AVG(user_percentage) AS avg_percentage
        FROM aggregated_user
        WHERE year = %s
        GROUP BY device_brand
        ORDER BY total_users DESC
        LIMIT 10;
    """
    if test_query("Device Distribution (2023)", sql3, params=[2023]):
        tests_passed += 1
    
    # Test 4: Insurance Data
    tests_total += 1
    sql4 = """
        SELECT state, SUM(amount) AS insurance_amount, SUM(count) AS insurance_count
        FROM aggregated_insurance
        WHERE year = %s
        GROUP BY state
        ORDER BY insurance_amount DESC
        LIMIT 10;
    """
    if test_query("Insurance by State (2023)", sql4, params=[2023]):
        tests_passed += 1
    
    # Test 5: Transaction Types
    tests_total += 1
    sql5 = """
        SELECT transaction_type, SUM(amount) AS total_amount, SUM(count) AS total_transactions
        FROM aggregated_transaction
        WHERE year = %s AND quarter = %s
        GROUP BY transaction_type
        ORDER BY total_amount DESC;
    """
    if test_query("Transaction Types (2023 Q4)", sql5, params=[2023, 4]):
        tests_passed += 1
    
    # Test 6: State List
    tests_total += 1
    sql6 = "SELECT DISTINCT state FROM aggregated_transaction ORDER BY state;"
    if test_query("State List", sql6):
        tests_passed += 1
    
    # Test 7: Summary Metrics
    tests_total += 1
    sql7 = """
        SELECT 
            SUM(amount) AS total_amount,
            SUM(count) AS total_transactions,
            COUNT(DISTINCT state) AS total_states,
            AVG(amount) AS avg_transaction_value
        FROM aggregated_transaction
        WHERE year = %s;
    """
    if test_query("Summary Metrics (2023)", sql7, params=[2023]):
        tests_passed += 1
    
    # Summary
    print(f"\n{'='*60}")
    print(f"🎯 Test Results: {tests_passed}/{tests_total} passed")
    print(f"{'='*60}")
    
    if tests_passed == tests_total:
        print("✅ All tests passed! Dashboard should work correctly.")
        print("🚀 You can now run: streamlit run dashboard/app.py")
    else:
        print(f"⚠️  {tests_total - tests_passed} test(s) failed. Check database connection and data.")
    
    return tests_passed == tests_total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
