"""
Data Processor
Handles data transformations, calculations, and business logic
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
from datetime import datetime


class DataProcessor:
    """
    Process and transform NetSuite data according to business rules
    """
    
    def __init__(self, netsuite_connector):
        """
        Initialize data processor
        
        Args:
            netsuite_connector: NetSuiteConnector instance
        """
        self.ns = netsuite_connector
    
    def _handle_nulls(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply null/blank handling rules from CRISP
        
        Args:
            df: Input dataframe
            
        Returns:
            Dataframe with nulls handled
        """
        # Numeric fields default to 0
        numeric_fields = ['sales_units', 'sales_dollars', 'returns', 'cost', 'retail']
        for field in numeric_fields:
            if field in df.columns:
                df[field] = df[field].fillna(0)
        
        # Text fields default to "Unknown"
        text_fields = ['category', 'vendor', 'material_desc', 'color_desc', 'territory']
        for field in text_fields:
            if field in df.columns:
                df[field] = df[field].fillna("Unknown")
        
        return df
    
    def _calculate_derived_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate derived metrics according to CRISP specifications
        
        Formulas:
        - Net Units = Sales Units - Returns
        - Gross Profit = Retail - Cost
        - GM% = (Retail - Cost) / Retail
        
        Args:
            df: Input dataframe with base metrics
            
        Returns:
            Dataframe with derived metrics added
        """
        # Net Units = Sales Units - Returns
        df['net_units'] = df['sales_units'] - df['returns']
        
        # Gross Profit = Retail - Cost
        # Note: Must use corrected cost values, not NetSuite's GM calculation
        df['gross_profit'] = df['retail'] - df['cost']
        
        # GM% = (Retail - Cost) / Retail
        # Avoid division by zero
        df['gm_percent'] = np.where(
            df['retail'] > 0,
            ((df['retail'] - df['cost']) / df['retail']) * 100,
            0
        )
        
        return df
    
    def _apply_filters(self, df: pd.DataFrame, category: List[str], vendor: List[str], 
                      brand: Optional[List[str]] = None, 
                      territory: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Apply user-selected filters to dataframe
        
        Args:
            df: Input dataframe
            category: Category filter values
            vendor: Vendor filter values
            brand: Optional brand filter values
            territory: Optional territory filter values
            
        Returns:
            Filtered dataframe
        """
        # Category filter
        if category and "All" not in category:
            df = df[df['category'].isin(category)]
        
        # Vendor filter
        if vendor and "All" not in vendor:
            df = df[df['vendor'].isin(vendor)]
        
        # Brand filter (if provided)
        if brand and "All" not in brand and 'brand' in df.columns:
            df = df[df['brand'].isin(brand)]
        
        # Territory filter (if provided)
        if territory and "All" not in territory and 'territory' in df.columns:
            df = df[df['territory'].isin(territory)]
        
        return df
    
    def get_top_40_styles(self, start_date, end_date, category: List[str], 
                         vendor: List[str], brand: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Get Top 40 Styles ranked by units
        
        Args:
            start_date: Start date
            end_date: End date
            category: Category filter
            vendor: Vendor filter
            brand: Optional brand filter
            
        Returns:
            DataFrame with Top 40 styles
        """
        # Convert dates to strings
        start_str = start_date.strftime("%Y-%m-%d")
        end_str = end_date.strftime("%Y-%m-%d")
        
        # Get sales transactions from NetSuite
        filters = {
            'transaction_type': 'sales',
            'category': category if "All" not in category else None,
            'vendor': vendor if "All" not in vendor else None,
            'brand': brand if brand and "All" not in brand else None
        }
        
        transactions = self.ns.get_sales_transactions(start_str, end_str, filters)
        
        if not transactions:
            return pd.DataFrame()
        
        # Convert to DataFrame
        df = pd.DataFrame(transactions)
        
        # Get item master data for additional attributes
        item_ids = df['item_id'].unique().tolist()
        items = self.ns.get_item_master(item_ids)
        items_df = pd.DataFrame(items)
        
        # Get corrected cost/retail data
        cost_retail = self.ns.get_cost_retail_data(item_ids)
        
        # Merge item attributes
        if not items_df.empty:
            df = df.merge(items_df[['item_id', 'style', 'material_desc', 'color_desc', 
                                    'category', 'vendor']], 
                         on='item_id', how='left')
        
        # Apply corrected cost/retail values
        df['cost'] = df['item_id'].map(lambda x: cost_retail.get(x, {}).get('cost', 0))
        df['retail'] = df['item_id'].map(lambda x: cost_retail.get(x, {}).get('retail', 0))
        
        # Handle nulls
        df = self._handle_nulls(df)
        
        # Aggregate by style
        agg_dict = {
            'sales_units': 'sum',
            'sales_dollars': 'sum',
            'returns': 'sum',
            'cost': 'first',  # Take first cost value (should be same for all transactions of same style)
            'retail': 'first',
            'material_desc': 'first',
            'color_desc': 'first',
            'category': 'first',
            'vendor': 'first'
        }
        
        df_grouped = df.groupby('style').agg(agg_dict).reset_index()
        
        # Calculate derived metrics
        df_grouped = self._calculate_derived_metrics(df_grouped)
        
        # Apply filters
        df_grouped = self._apply_filters(df_grouped, category, vendor, brand)
        
        # Rank by sales units (descending)
        df_grouped = df_grouped.sort_values('sales_units', ascending=False)
        
        # Take top 40
        df_top40 = df_grouped.head(40).reset_index(drop=True)
        
        # Add rank column
        df_top40.insert(0, 'rank', range(1, len(df_top40) + 1))
        
        return df_top40
    
    def get_top_40_customers(self, start_date, end_date, category: List[str], 
                            vendor: List[str], brand: Optional[List[str]] = None,
                            territory: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Get Top 40 Customers ranked by units
        
        Args:
            start_date: Start date
            end_date: End date
            category: Category filter
            vendor: Vendor filter
            brand: Optional brand filter
            territory: Optional territory filter
            
        Returns:
            DataFrame with Top 40 customers
        """
        # Convert dates to strings
        start_str = start_date.strftime("%Y-%m-%d")
        end_str = end_date.strftime("%Y-%m-%d")
        
        # Get sales transactions from NetSuite
        filters = {
            'transaction_type': 'sales',
            'category': category if "All" not in category else None,
            'vendor': vendor if "All" not in vendor else None,
            'brand': brand if brand and "All" not in brand else None,
            'territory': territory if territory and "All" not in territory else None
        }
        
        transactions = self.ns.get_sales_transactions(start_str, end_str, filters)
        
        if not transactions:
            return pd.DataFrame()
        
        # Convert to DataFrame
        df = pd.DataFrame(transactions)
        
        # Get customer master data
        customer_ids = df['customer_id'].unique().tolist()
        customers = self.ns.get_customer_master(customer_ids)
        customers_df = pd.DataFrame(customers)
        
        # Get item data for category/vendor
        item_ids = df['item_id'].unique().tolist()
        items = self.ns.get_item_master(item_ids)
        items_df = pd.DataFrame(items)
        
        # Get cost/retail data
        cost_retail = self.ns.get_cost_retail_data(item_ids)
        
        # Merge customer attributes
        if not customers_df.empty:
            df = df.merge(customers_df[['customer_id', 'customer', 'territory', 'customer_category']], 
                         on='customer_id', how='left')
        
        # Merge item attributes for filtering
        if not items_df.empty:
            df = df.merge(items_df[['item_id', 'category', 'vendor']], 
                         on='item_id', how='left')
        
        # Apply corrected cost/retail
        df['cost'] = df['item_id'].map(lambda x: cost_retail.get(x, {}).get('cost', 0))
        df['retail'] = df['item_id'].map(lambda x: cost_retail.get(x, {}).get('retail', 0))
        
        # Handle nulls
        df = self._handle_nulls(df)
        
        # Aggregate by customer
        agg_dict = {
            'sales_units': 'sum',
            'sales_dollars': 'sum',
            'returns': 'sum',
            'cost': 'sum',  # Sum costs across all items
            'retail': 'sum',  # Sum retail across all items
            'territory': 'first',
            'customer_category': 'first',
            'category': 'first',
            'vendor': 'first'
        }
        
        df_grouped = df.groupby('customer').agg(agg_dict).reset_index()
        
        # Calculate derived metrics
        df_grouped = self._calculate_derived_metrics(df_grouped)
        
        # Apply filters
        df_grouped = self._apply_filters(df_grouped, category, vendor, brand, territory)
        
        # Rank by sales units (descending)
        df_grouped = df_grouped.sort_values('sales_units', ascending=False)
        
        # Take top 40
        df_top40 = df_grouped.head(40).reset_index(drop=True)
        
        # Add rank column
        df_top40.insert(0, 'rank', range(1, len(df_top40) + 1))
        
        return df_top40
    
    def get_customers_by_style(self, style: str, start_date, end_date) -> pd.DataFrame:
        """
        Get all customers who purchased a specific style (drilldown)
        
        Args:
            style: Style name
            start_date: Start date
            end_date: End date
            
        Returns:
            DataFrame with customer purchase details for the style
        """
        # Convert dates to strings
        start_str = start_date.strftime("%Y-%m-%d")
        end_str = end_date.strftime("%Y-%m-%d")
        
        # Get transactions filtered by style
        filters = {
            'transaction_type': 'sales',
            'style': style
        }
        
        transactions = self.ns.get_sales_transactions(start_str, end_str, filters)
        
        if not transactions:
            return pd.DataFrame()
        
        df = pd.DataFrame(transactions)
        
        # Get customer data
        customer_ids = df['customer_id'].unique().tolist()
        customers = self.ns.get_customer_master(customer_ids)
        customers_df = pd.DataFrame(customers)
        
        # Get cost/retail
        item_ids = df['item_id'].unique().tolist()
        cost_retail = self.ns.get_cost_retail_data(item_ids)
        
        # Merge customer names
        if not customers_df.empty:
            df = df.merge(customers_df[['customer_id', 'customer', 'territory']], 
                         on='customer_id', how='left')
        
        # Apply cost/retail
        df['cost'] = df['item_id'].map(lambda x: cost_retail.get(x, {}).get('cost', 0))
        df['retail'] = df['item_id'].map(lambda x: cost_retail.get(x, {}).get('retail', 0))
        
        # Handle nulls
        df = self._handle_nulls(df)
        
        # Aggregate by customer
        df_grouped = df.groupby('customer').agg({
            'sales_units': 'sum',
            'sales_dollars': 'sum',
            'returns': 'sum',
            'cost': 'sum',
            'retail': 'sum',
            'territory': 'first'
        }).reset_index()
        
        # Calculate derived metrics
        df_grouped = self._calculate_derived_metrics(df_grouped)
        
        # Sort by sales units
        df_grouped = df_grouped.sort_values('sales_units', ascending=False).reset_index(drop=True)
        
        return df_grouped
    
    def get_styles_by_customer(self, customer: str, start_date, end_date) -> pd.DataFrame:
        """
        Get all styles purchased by a specific customer (drilldown)
        
        Args:
            customer: Customer name
            start_date: Start date
            end_date: End date
            
        Returns:
            DataFrame with style purchase details for the customer
        """
        # Convert dates to strings
        start_str = start_date.strftime("%Y-%m-%d")
        end_str = end_date.strftime("%Y-%m-%d")
        
        # Get transactions filtered by customer
        filters = {
            'transaction_type': 'sales',
            'customer': customer
        }
        
        transactions = self.ns.get_sales_transactions(start_str, end_str, filters)
        
        if not transactions:
            return pd.DataFrame()
        
        df = pd.DataFrame(transactions)
        
        # Get item master data
        item_ids = df['item_id'].unique().tolist()
        items = self.ns.get_item_master(item_ids)
        items_df = pd.DataFrame(items)
        
        # Get cost/retail
        cost_retail = self.ns.get_cost_retail_data(item_ids)
        
        # Merge item attributes
        if not items_df.empty:
            df = df.merge(items_df[['item_id', 'style', 'material_desc', 'color_desc', 
                                    'category', 'vendor']], 
                         on='item_id', how='left')
        
        # Apply cost/retail
        df['cost'] = df['item_id'].map(lambda x: cost_retail.get(x, {}).get('cost', 0))
        df['retail'] = df['item_id'].map(lambda x: cost_retail.get(x, {}).get('retail', 0))
        
        # Handle nulls
        df = self._handle_nulls(df)
        
        # Aggregate by style
        df_grouped = df.groupby('style').agg({
            'sales_units': 'sum',
            'sales_dollars': 'sum',
            'returns': 'sum',
            'cost': 'first',
            'retail': 'first',
            'material_desc': 'first',
            'color_desc': 'first',
            'category': 'first',
            'vendor': 'first'
        }).reset_index()
        
        # Calculate derived metrics
        df_grouped = self._calculate_derived_metrics(df_grouped)
        
        # Sort by sales units
        df_grouped = df_grouped.sort_values('sales_units', ascending=False).reset_index(drop=True)
        
        return df_grouped
