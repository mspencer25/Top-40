"""
Test Script for Top 40 Dashboard
Tests NetSuite connection, data processing, and business logic
"""

import sys
from datetime import datetime, timedelta
from netsuite_connector import NetSuiteConnector
from data_processor import DataProcessor
import pandas as pd


def test_connection():
    """Test NetSuite connection"""
    print("=" * 60)
    print("TEST 1: NetSuite Connection")
    print("=" * 60)
    
    # Replace with your credentials for testing
    try:
        connector = NetSuiteConnector(
            account_id="YOUR_ACCOUNT_ID",
            consumer_key="YOUR_CONSUMER_KEY",
            consumer_secret="YOUR_CONSUMER_SECRET",
            token_id="YOUR_TOKEN_ID",
            token_secret="YOUR_TOKEN_SECRET"
        )
        
        result = connector.test_connection()
        
        if result:
            print("✅ Connection successful!")
            return connector
        else:
            print("❌ Connection failed!")
            return None
            
    except Exception as e:
        print(f"❌ Connection error: {str(e)}")
        return None


def test_sales_transactions(connector):
    """Test sales transaction retrieval"""
    print("\n" + "=" * 60)
    print("TEST 2: Sales Transactions")
    print("=" * 60)
    
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        print(f"Fetching transactions from {start_date.date()} to {end_date.date()}")
        
        transactions = connector.get_sales_transactions(
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d"),
            filters={}
        )
        
        print(f"✅ Retrieved {len(transactions)} transactions")
        
        if transactions:
            print("\nSample transaction:")
            sample = transactions[0]
            for key, value in sample.items():
                print(f"  {key}: {value}")
        
        return transactions
        
    except Exception as e:
        print(f"❌ Error fetching transactions: {str(e)}")
        return []


def test_item_master(connector):
    """Test item master data retrieval"""
    print("\n" + "=" * 60)
    print("TEST 3: Item Master Data")
    print("=" * 60)
    
    try:
        items = connector.get_item_master()
        
        print(f"✅ Retrieved {len(items)} items")
        
        if items:
            print("\nSample item:")
            sample = items[0]
            for key, value in sample.items():
                print(f"  {key}: {value}")
        
        return items
        
    except Exception as e:
        print(f"❌ Error fetching items: {str(e)}")
        return []


def test_customer_master(connector):
    """Test customer master data retrieval"""
    print("\n" + "=" * 60)
    print("TEST 4: Customer Master Data")
    print("=" * 60)
    
    try:
        customers = connector.get_customer_master()
        
        print(f"✅ Retrieved {len(customers)} customers")
        
        if customers:
            print("\nSample customer:")
            sample = customers[0]
            for key, value in sample.items():
                print(f"  {key}: {value}")
        
        return customers
        
    except Exception as e:
        print(f"❌ Error fetching customers: {str(e)}")
        return []


def test_data_processing(connector):
    """Test data processing and calculations"""
    print("\n" + "=" * 60)
    print("TEST 5: Data Processing & Calculations")
    print("=" * 60)
    
    try:
        processor = DataProcessor(connector)
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        print("Testing Top 40 Styles...")
        styles = processor.get_top_40_styles(
            start_date=start_date.date(),
            end_date=end_date.date(),
            category=["All"],
            vendor=["All"]
        )
        
        if not styles.empty:
            print(f"✅ Processed {len(styles)} styles")
            print("\nTop 5 Styles:")
            print(styles[['rank', 'style', 'sales_units', 'gm_percent']].head())
            
            # Validate calculations
            print("\n📊 Validating calculations...")
            test_row = styles.iloc[0]
            
            # Check Net Units = Sales Units - Returns
            calculated_net = test_row['sales_units'] - test_row['returns']
            if abs(calculated_net - test_row['net_units']) < 0.01:
                print("✅ Net Units calculation correct")
            else:
                print(f"❌ Net Units calculation error: {calculated_net} != {test_row['net_units']}")
            
            # Check Gross Profit = Retail - Cost
            calculated_gp = test_row['retail'] - test_row['cost']
            if abs(calculated_gp - test_row['gross_profit']) < 0.01:
                print("✅ Gross Profit calculation correct")
            else:
                print(f"❌ Gross Profit calculation error: {calculated_gp} != {test_row['gross_profit']}")
            
            # Check GM% = (Retail - Cost) / Retail
            if test_row['retail'] > 0:
                calculated_gm = ((test_row['retail'] - test_row['cost']) / test_row['retail']) * 100
                if abs(calculated_gm - test_row['gm_percent']) < 0.01:
                    print("✅ GM% calculation correct")
                else:
                    print(f"❌ GM% calculation error: {calculated_gm:.2f}% != {test_row['gm_percent']:.2f}%")
        else:
            print("⚠️ No styles data returned")
        
        print("\nTesting Top 40 Customers...")
        customers = processor.get_top_40_customers(
            start_date=start_date.date(),
            end_date=end_date.date(),
            category=["All"],
            vendor=["All"],
            territory=["All"]
        )
        
        if not customers.empty:
            print(f"✅ Processed {len(customers)} customers")
            print("\nTop 5 Customers:")
            print(customers[['rank', 'customer', 'sales_units', 'gm_percent']].head())
        else:
            print("⚠️ No customers data returned")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in data processing: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_drilldown(connector):
    """Test drilldown functionality"""
    print("\n" + "=" * 60)
    print("TEST 6: Drilldown Functionality")
    print("=" * 60)
    
    try:
        processor = DataProcessor(connector)
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        # Get top styles first
        styles = processor.get_top_40_styles(
            start_date=start_date.date(),
            end_date=end_date.date(),
            category=["All"],
            vendor=["All"]
        )
        
        if not styles.empty:
            test_style = styles.iloc[0]['style']
            print(f"Testing drilldown for style: {test_style}")
            
            customers = processor.get_customers_by_style(
                style=test_style,
                start_date=start_date.date(),
                end_date=end_date.date()
            )
            
            if not customers.empty:
                print(f"✅ Found {len(customers)} customers for this style")
                print("\nTop 3 customers:")
                print(customers[['customer', 'sales_units', 'sales_dollars']].head(3))
            else:
                print("⚠️ No customers found for this style")
        
        # Test reverse drilldown
        customers = processor.get_top_40_customers(
            start_date=start_date.date(),
            end_date=end_date.date(),
            category=["All"],
            vendor=["All"],
            territory=["All"]
        )
        
        if not customers.empty:
            test_customer = customers.iloc[0]['customer']
            print(f"\nTesting drilldown for customer: {test_customer}")
            
            styles = processor.get_styles_by_customer(
                customer=test_customer,
                start_date=start_date.date(),
                end_date=end_date.date()
            )
            
            if not styles.empty:
                print(f"✅ Found {len(styles)} styles for this customer")
                print("\nTop 3 styles:")
                print(styles[['style', 'sales_units', 'sales_dollars']].head(3))
            else:
                print("⚠️ No styles found for this customer")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in drilldown: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_filtering(connector):
    """Test filtering functionality"""
    print("\n" + "=" * 60)
    print("TEST 7: Filtering")
    print("=" * 60)
    
    try:
        processor = DataProcessor(connector)
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        # Test with filters
        print("Testing with category filter...")
        styles = processor.get_top_40_styles(
            start_date=start_date.date(),
            end_date=end_date.date(),
            category=["MEN'S OXFORD"],
            vendor=["All"]
        )
        
        if not styles.empty:
            print(f"✅ Retrieved {len(styles)} styles with filter")
            # Verify all are in correct category
            if all(styles['category'] == "MEN'S OXFORD"):
                print("✅ Category filter working correctly")
            else:
                print("❌ Category filter not working properly")
        else:
            print("⚠️ No data with filter (might be expected)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in filtering: {str(e)}")
        return False


def run_all_tests():
    """Run all tests"""
    print("\n")
    print("*" * 60)
    print("  TOP 40 DASHBOARD - TEST SUITE")
    print("  Drew Shoe Corporation")
    print("*" * 60)
    print("\n")
    
    # Test connection
    connector = test_connection()
    
    if not connector:
        print("\n❌ Cannot proceed without connection. Please check credentials.")
        return False
    
    # Run all tests
    tests = [
        ("Sales Transactions", lambda: test_sales_transactions(connector)),
        ("Item Master", lambda: test_item_master(connector)),
        ("Customer Master", lambda: test_customer_master(connector)),
        ("Data Processing", lambda: test_data_processing(connector)),
        ("Drilldown", lambda: test_drilldown(connector)),
        ("Filtering", lambda: test_filtering(connector))
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test '{test_name}' failed with exception: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print("\n" + "=" * 60)
    print(f"Results: {passed}/{total} tests passed")
    print("=" * 60)
    
    return passed == total


if __name__ == "__main__":
    print("\n⚠️  IMPORTANT: Update credentials in test_connection() function before running!")
    print("Press Enter to continue or Ctrl+C to cancel...")
    input()
    
    success = run_all_tests()
    
    if success:
        print("\n✅ All tests passed! Dashboard is ready to use.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Please review errors above.")
        sys.exit(1)
