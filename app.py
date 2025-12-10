"""
Top 40 Styles & Customers Dashboard
Drew Shoe - Merchandising Quick Wins
Author: Megan Spencer
Last Updated: Dec 10, 2025
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add modules to path
sys.path.append(str(Path(__file__).parent))

from netsuite_connector import NetSuiteConnector
from data_processor import DataProcessor
from utils import format_currency, format_number, format_percentage

# Page configuration
st.set_page_config(
    page_title="Top 40 Dashboard - Drew Shoe",
    page_icon="👟",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
    }
    .dataframe {
        font-size: 12px;
    }
    h1 {
        color: #1f4788;
        padding-bottom: 20px;
    }
    h2 {
        color: #2e5c9a;
        padding-top: 10px;
    }
    .stAlert {
        margin-top: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'netsuite_connector' not in st.session_state:
    st.session_state.netsuite_connector = None
if 'data_processor' not in st.session_state:
    st.session_state.data_processor = None
if 'styles_data' not in st.session_state:
    st.session_state.styles_data = None
if 'customers_data' not in st.session_state:
    st.session_state.customers_data = None
if 'drilldown_data' not in st.session_state:
    st.session_state.drilldown_data = None
if 'drilldown_type' not in st.session_state:
    st.session_state.drilldown_type = None

def initialize_connection():
    """Initialize NetSuite connection"""
    with st.sidebar.expander("🔐 NetSuite Connection", expanded=False):
        account_id = st.text_input("Account ID", type="password", key="account_id")
        consumer_key = st.text_input("Consumer Key", type="password", key="consumer_key")
        consumer_secret = st.text_input("Consumer Secret", type="password", key="consumer_secret")
        token_id = st.text_input("Token ID", type="password", key="token_id")
        token_secret = st.text_input("Token Secret", type="password", key="token_secret")
        
        if st.button("Connect to NetSuite"):
            if all([account_id, consumer_key, consumer_secret, token_id, token_secret]):
                try:
                    connector = NetSuiteConnector(
                        account_id=account_id,
                        consumer_key=consumer_key,
                        consumer_secret=consumer_secret,
                        token_id=token_id,
                        token_secret=token_secret
                    )
                    st.session_state.netsuite_connector = connector
                    st.session_state.data_processor = DataProcessor(connector)
                    st.success("✅ Connected to NetSuite successfully!")
                except Exception as e:
                    st.error(f"❌ Connection failed: {str(e)}")
            else:
                st.warning("⚠️ Please fill in all connection fields")
    
    return st.session_state.netsuite_connector is not None

def render_sidebar_filters():
    """Render sidebar filters"""
    st.sidebar.title("📊 Dashboard Filters")
    
    # Date Range
    st.sidebar.subheader("📅 Date Range")
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        start_date = st.date_input(
            "Start Date",
            value=datetime.now() - timedelta(days=90),
            key="start_date"
        )
    with col2:
        end_date = st.date_input(
            "End Date",
            value=datetime.now(),
            key="end_date"
        )
    
    # Manual date entry option
    with st.sidebar.expander("✍️ Manual Date Entry"):
        manual_start = st.text_input("Start (YYYY-MM-DD)", value=start_date.strftime("%Y-%m-%d"))
        manual_end = st.text_input("End (YYYY-MM-DD)", value=end_date.strftime("%Y-%m-%d"))
        if st.button("Apply Manual Dates"):
            try:
                start_date = datetime.strptime(manual_start, "%Y-%m-%d").date()
                end_date = datetime.strptime(manual_end, "%Y-%m-%d").date()
                st.success("✅ Manual dates applied")
            except:
                st.error("❌ Invalid date format")
    
    st.sidebar.divider()
    
    # Category Filter
    categories = ["All", "MEN'S OXFORD", "WOMEN'S CASUAL", "BOOTS", "SANDALS", "ATHLETIC"]
    category = st.sidebar.multiselect(
        "🏷️ Category",
        options=categories,
        default=["All"]
    )
    
    # Vendor Filter
    vendors = ["All", "WEST NEW WING", "DREW SHOE", "COMFORT PLUS", "OTHER"]
    vendor = st.sidebar.multiselect(
        "🏭 Vendor",
        options=vendors,
        default=["All"]
    )
    
    # Brand Filter
    brands = ["All", "DREW", "PARAMOUNT", "PRIVATE LABEL"]
    brand = st.sidebar.multiselect(
        "🏢 Brand",
        options=brands,
        default=["All"]
    )
    
    # Territory Filter (for customers)
    territories = ["All", "SOUTHWEST", "NORTHEAST", "MIDWEST", "WEST"]
    territory = st.sidebar.multiselect(
        "🗺️ Sales Territory",
        options=territories,
        default=["All"]
    )
    
    st.sidebar.divider()
    
    # Refresh Data Button
    if st.sidebar.button("🔄 Refresh Data", type="primary"):
        st.session_state.styles_data = None
        st.session_state.customers_data = None
        st.session_state.drilldown_data = None
        st.rerun()
    
    return {
        'start_date': start_date,
        'end_date': end_date,
        'category': category,
        'vendor': vendor,
        'brand': brand,
        'territory': territory
    }

def render_kpi_tiles(data, report_type="styles"):
    """Render KPI tiles at top of dashboard"""
    
    if data is None or data.empty:
        return
    
    col1, col2, col3, col4 = st.columns(4)
    
    total_sales = data['sales_dollars'].sum()
    total_units = data['sales_units'].sum()
    total_gp = data['gross_profit'].sum()
    avg_gm = (total_gp / total_sales * 100) if total_sales > 0 else 0
    
    with col1:
        st.metric(
            label="💰 Total Sales",
            value=format_currency(total_sales),
            delta=None
        )
    
    with col2:
        st.metric(
            label="📦 Total Units",
            value=format_number(total_units),
            delta=None
        )
    
    with col3:
        st.metric(
            label="💵 Gross Profit",
            value=format_currency(total_gp),
            delta=None
        )
    
    with col4:
        st.metric(
            label="📊 Avg GM%",
            value=format_percentage(avg_gm),
            delta=None
        )

def render_top_40_styles(filters):
    """Render Top 40 Styles dashboard"""
    st.header("👟 Top 40 Styles by Units")
    
    # Load data
    if st.session_state.styles_data is None:
        with st.spinner("Loading Top 40 Styles data..."):
            try:
                processor = st.session_state.data_processor
                st.session_state.styles_data = processor.get_top_40_styles(
                    start_date=filters['start_date'],
                    end_date=filters['end_date'],
                    category=filters['category'],
                    vendor=filters['vendor'],
                    brand=filters['brand']
                )
            except Exception as e:
                st.error(f"❌ Error loading styles data: {str(e)}")
                return
    
    data = st.session_state.styles_data
    
    if data is None or data.empty:
        st.warning("⚠️ No data available for the selected filters")
        return
    
    # KPI Tiles
    render_kpi_tiles(data, "styles")
    
    st.divider()
    
    # Main table
    st.subheader("📋 Top 40 Styles Table")
    
    # Format the dataframe for display
    display_df = data.copy()
    display_df['sales_dollars'] = display_df['sales_dollars'].apply(format_currency)
    display_df['gross_profit'] = display_df['gross_profit'].apply(format_currency)
    display_df['gm_percent'] = display_df['gm_percent'].apply(lambda x: format_percentage(x))
    display_df['sales_units'] = display_df['sales_units'].apply(lambda x: f"{x:,.0f}")
    display_df['returns'] = display_df['returns'].apply(lambda x: f"{x:,.0f}")
    display_df['net_units'] = display_df['net_units'].apply(lambda x: f"{x:,.0f}")
    
    # Rename columns for display
    display_df = display_df.rename(columns={
        'style': 'Style',
        'material_desc': 'Material',
        'color_desc': 'Color',
        'category': 'Category',
        'vendor': 'Vendor',
        'sales_units': 'Sales Units',
        'returns': 'Returns',
        'net_units': 'Net Units',
        'sales_dollars': 'Sales $',
        'gross_profit': 'Gross Profit',
        'gm_percent': 'GM%'
    })
    
    # Display with clickable rows
    st.dataframe(
        display_df,
        use_container_width=True,
        height=600,
        hide_index=True
    )
    
    # Row selection for drilldown
    st.subheader("🔍 Drilldown: Click a Style")
    
    selected_style = st.selectbox(
        "Select a style to view customer purchases:",
        options=data['style'].unique(),
        key="style_selector"
    )
    
    if selected_style and st.button("View Customers for this Style", key="drill_style"):
        with st.spinner(f"Loading customers for {selected_style}..."):
            try:
                processor = st.session_state.data_processor
                drilldown = processor.get_customers_by_style(
                    style=selected_style,
                    start_date=filters['start_date'],
                    end_date=filters['end_date']
                )
                st.session_state.drilldown_data = drilldown
                st.session_state.drilldown_type = "style"
            except Exception as e:
                st.error(f"❌ Error loading drilldown: {str(e)}")
    
    # Display drilldown data
    if st.session_state.drilldown_data is not None and st.session_state.drilldown_type == "style":
        st.divider()
        st.subheader(f"🎯 Customers purchasing: {selected_style}")
        
        drill_df = st.session_state.drilldown_data.copy()
        drill_df['sales_dollars'] = drill_df['sales_dollars'].apply(format_currency)
        drill_df['gross_profit'] = drill_df['gross_profit'].apply(format_currency)
        drill_df['gm_percent'] = drill_df['gm_percent'].apply(lambda x: format_percentage(x))
        
        st.dataframe(drill_df, use_container_width=True, hide_index=True)
        
        # Export option
        csv = drill_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Drilldown Data",
            data=csv,
            file_name=f"customers_{selected_style}_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    
    # Export main data
    st.divider()
    col1, col2 = st.columns([1, 4])
    with col1:
        csv = data.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Export to CSV",
            data=csv,
            file_name=f"top_40_styles_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

def render_top_40_customers(filters):
    """Render Top 40 Customers dashboard"""
    st.header("🏢 Top 40 Customers by Units")
    
    # Load data
    if st.session_state.customers_data is None:
        with st.spinner("Loading Top 40 Customers data..."):
            try:
                processor = st.session_state.data_processor
                st.session_state.customers_data = processor.get_top_40_customers(
                    start_date=filters['start_date'],
                    end_date=filters['end_date'],
                    category=filters['category'],
                    vendor=filters['vendor'],
                    brand=filters['brand'],
                    territory=filters['territory']
                )
            except Exception as e:
                st.error(f"❌ Error loading customers data: {str(e)}")
                return
    
    data = st.session_state.customers_data
    
    if data is None or data.empty:
        st.warning("⚠️ No data available for the selected filters")
        return
    
    # KPI Tiles
    render_kpi_tiles(data, "customers")
    
    st.divider()
    
    # Main table
    st.subheader("📋 Top 40 Customers Table")
    
    # Format the dataframe for display
    display_df = data.copy()
    display_df['sales_dollars'] = display_df['sales_dollars'].apply(format_currency)
    display_df['gross_profit'] = display_df['gross_profit'].apply(format_currency)
    display_df['gm_percent'] = display_df['gm_percent'].apply(lambda x: format_percentage(x))
    display_df['sales_units'] = display_df['sales_units'].apply(lambda x: f"{x:,.0f}")
    display_df['returns'] = display_df['returns'].apply(lambda x: f"{x:,.0f}")
    display_df['net_units'] = display_df['net_units'].apply(lambda x: f"{x:,.0f}")
    
    # Rename columns for display
    display_df = display_df.rename(columns={
        'customer': 'Customer',
        'category': 'Category',
        'vendor': 'Vendor',
        'territory': 'Territory',
        'sales_units': 'Sales Units',
        'returns': 'Returns',
        'net_units': 'Net Units',
        'sales_dollars': 'Sales $',
        'gross_profit': 'Gross Profit',
        'gm_percent': 'GM%'
    })
    
    # Display table
    st.dataframe(
        display_df,
        use_container_width=True,
        height=600,
        hide_index=True
    )
    
    # Row selection for drilldown
    st.subheader("🔍 Drilldown: Click a Customer")
    
    selected_customer = st.selectbox(
        "Select a customer to view purchased styles:",
        options=data['customer'].unique(),
        key="customer_selector"
    )
    
    if selected_customer and st.button("View Styles for this Customer", key="drill_customer"):
        with st.spinner(f"Loading styles for {selected_customer}..."):
            try:
                processor = st.session_state.data_processor
                drilldown = processor.get_styles_by_customer(
                    customer=selected_customer,
                    start_date=filters['start_date'],
                    end_date=filters['end_date']
                )
                st.session_state.drilldown_data = drilldown
                st.session_state.drilldown_type = "customer"
            except Exception as e:
                st.error(f"❌ Error loading drilldown: {str(e)}")
    
    # Display drilldown data
    if st.session_state.drilldown_data is not None and st.session_state.drilldown_type == "customer":
        st.divider()
        st.subheader(f"🎯 Styles purchased by: {selected_customer}")
        
        drill_df = st.session_state.drilldown_data.copy()
        drill_df['sales_dollars'] = drill_df['sales_dollars'].apply(format_currency)
        drill_df['gross_profit'] = drill_df['gross_profit'].apply(format_currency)
        drill_df['gm_percent'] = drill_df['gm_percent'].apply(lambda x: format_percentage(x))
        
        st.dataframe(drill_df, use_container_width=True, hide_index=True)
        
        # Export option
        csv = drill_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Drilldown Data",
            data=csv,
            file_name=f"styles_{selected_customer.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    
    # Export main data
    st.divider()
    col1, col2 = st.columns([1, 4])
    with col1:
        csv = data.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Export to CSV",
            data=csv,
            file_name=f"top_40_customers_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

def main():
    """Main application"""
    
    # Title
    st.title("👟 Drew Shoe - Top 40 Dashboard")
    st.markdown("**Merchandising Quick Wins** | Last Updated: Dec 10, 2025")
    
    # Initialize connection
    if not initialize_connection():
        st.info("👈 Please configure NetSuite connection in the sidebar to get started")
        st.markdown("""
        ### 📖 Dashboard Features
        
        **Top 40 Styles:**
        - Ranked by sales units (fixed ranking)
        - Drill down to see customers who purchased each style
        - Corrected Gross Margin % calculation
        - Export filtered data to CSV
        
        **Top 40 Customers:**
        - Ranked by sales units
        - Drill down to see styles purchased by each customer
        - Segment by territory, category, and vendor
        - Export filtered data to CSV
        
        **Key Metrics:**
        - Sales Units, Returns, Net Units
        - Sales Dollars
        - Gross Profit
        - Corrected GM% = (Retail - Cost) / Retail
        """)
        return
    
    # Sidebar filters
    filters = render_sidebar_filters()
    
    # Main navigation
    tab1, tab2 = st.tabs(["👟 Top 40 Styles", "🏢 Top 40 Customers"])
    
    with tab1:
        render_top_40_styles(filters)
    
    with tab2:
        render_top_40_customers(filters)
    
    # Footer
    st.divider()
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 20px;'>
    <small>Drew Shoe Corporation | Prepared by: Megan Spencer | Data Source: NetSuite<br>
    ⚠️ Cost values are corrected from Merchandising inputs. NetSuite GM% is not used.</small>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
