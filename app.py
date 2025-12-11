"""
Top 40 Styles & Customers Dashboard
Drew Shoe - Merchandising Quick Wins
Author: Megan Spencer
Last Updated: Dec 10, 2025
"""

import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add modules to path
sys.path.append(str(Path(__file__).parent))

from netsuite_connector import NetSuiteConnector
from data_processor import DataProcessor
from utils import format_currency, format_number, format_percentage

# ──────────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ──────────────────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Top 40 Dashboard - Drew Shoe",
    page_icon="👟",
    layout="wide",
)

# ──────────────────────────────────────────────────────────────────────────────
# SESSION STATE INITIALIZATION
# ──────────────────────────────────────────────────────────────────────────────

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

# ──────────────────────────────────────────────────────────────────────────────
# SIDEBAR - SETTINGS & CONNECTION
# ──────────────────────────────────────────────────────────────────────────────

st.sidebar.header("⚙️ Settings")

def initialize_connection():
    """Initialize NetSuite connection"""
    
    # Try to use secrets first (for Streamlit Cloud)
    if 'netsuite' in st.secrets:
        try:
            connector = NetSuiteConnector(
                account_id=st.secrets["netsuite"]["account_id"],
                consumer_key=st.secrets["netsuite"]["consumer_key"],
                consumer_secret=st.secrets["netsuite"]["consumer_secret"],
                token_id=st.secrets["netsuite"]["token_id"],
                token_secret=st.secrets["netsuite"]["token_secret"],
                restlet_url=st.secrets["netsuite"]["restlet_url"]
            )
            st.session_state.netsuite_connector = connector
            st.session_state.data_processor = DataProcessor(connector)
            st.sidebar.success("✅ Connected to NetSuite")
            return True
        except Exception as e:
            st.sidebar.error(f"❌ Connection failed: {str(e)}")
            return False
    
    # Fallback to manual entry
    with st.sidebar.expander("🔐 NetSuite Connection", expanded=True):
        st.caption("Enter NetSuite credentials")
        
        account_id = st.text_input("Account ID", type="password", key="account_id")
        consumer_key = st.text_input("Consumer Key", type="password", key="consumer_key")
        consumer_secret = st.text_input("Consumer Secret", type="password", key="consumer_secret")
        token_id = st.text_input("Token ID", type="password", key="token_id")
        token_secret = st.text_input("Token Secret", type="password", key="token_secret")
        
        if st.button("Connect"):
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
                    st.success("✅ Connected!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Failed: {str(e)}")
            else:
                st.warning("⚠️ Fill in all fields")
    
    return st.session_state.netsuite_connector is not None

# Initialize connection
is_connected = initialize_connection()

# Refresh button
st.sidebar.markdown("---")
if st.sidebar.button("🔄 Refresh Data", type="primary", use_container_width=True):
    st.cache_data.clear()
    st.session_state.styles_data = None
    st.session_state.customers_data = None
    st.session_state.drilldown_data = None
    st.rerun()

# Developer mode
st.sidebar.markdown("---")
show_debug = st.sidebar.checkbox("🔧 Developer Mode", value=False)

st.sidebar.markdown("---")

# ──────────────────────────────────────────────────────────────────────────────
# HEADER
# ──────────────────────────────────────────────────────────────────────────────

st.title("👟 Top 40 Dashboard")
st.caption("Drew Shoe Corporation | Merchandising Quick Wins")

if not is_connected:
    st.info("👈 Please configure NetSuite connection in the sidebar to get started")
    st.markdown("""
    ### 📖 Dashboard Features
    
    **Top 40 Styles:**
    - Ranked by sales units (fixed ranking)
    - Drill down to customers who purchased each style
    - Corrected Gross Margin % calculation
    - Export filtered data to CSV
    
    **Top 40 Customers:**
    - Ranked by sales units
    - Drill down to styles purchased by each customer
    - Segment by territory, category, and vendor
    - Export filtered data to CSV
    """)
    st.stop()

# ──────────────────────────────────────────────────────────────────────────────
# FILTERS (SIDEBAR)
# ──────────────────────────────────────────────────────────────────────────────

st.sidebar.header("🔍 Filters")

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

# Manual date entry
with st.sidebar.expander("✍️ Manual Date Entry"):
    manual_start = st.text_input("Start (YYYY-MM-DD)", value=start_date.strftime("%Y-%m-%d"))
    manual_end = st.text_input("End (YYYY-MM-DD)", value=end_date.strftime("%Y-%m-%d"))
    if st.button("Apply Manual Dates"):
        try:
            start_date = datetime.strptime(manual_start, "%Y-%m-%d").date()
            end_date = datetime.strptime(manual_end, "%Y-%m-%d").date()
            st.success("✅ Dates applied")
            st.rerun()
        except:
            st.error("❌ Invalid date format")

st.sidebar.markdown("---")

# Category Filter
categories = ["All", "MEN'S OXFORD", "WOMEN'S CASUAL", "BOOTS", "SANDALS", "ATHLETIC"]
category = st.sidebar.multiselect(
    "Category",
    options=categories,
    default=["All"]
)

# Vendor Filter
vendors = ["All", "WEST NEW WING", "DREW SHOE", "COMFORT PLUS", "OTHER"]
vendor = st.sidebar.multiselect(
    "Vendor",
    options=vendors,
    default=["All"]
)

# Brand Filter
brands = ["All", "DREW", "PARAMOUNT", "PRIVATE LABEL"]
brand = st.sidebar.multiselect(
    "Brand",
    options=brands,
    default=["All"]
)

# Territory Filter (for customers)
territories = ["All", "SOUTHWEST", "NORTHEAST", "MIDWEST", "WEST"]
territory = st.sidebar.multiselect(
    "Sales Territory",
    options=territories,
    default=["All"]
)

filters = {
    'start_date': start_date,
    'end_date': end_date,
    'category': category,
    'vendor': vendor,
    'brand': brand,
    'territory': territory
}

# ──────────────────────────────────────────────────────────────────────────────
# MAIN CONTENT - TABS
# ──────────────────────────────────────────────────────────────────────────────

tab1, tab2 = st.tabs(["👟 Top 40 Styles", "🏢 Top 40 Customers"])

# ──────────────────────────────────────────────────────────────────────────────
# TOP 40 STYLES TAB
# ──────────────────────────────────────────────────────────────────────────────

with tab1:
    st.markdown("---")
    
    # Load data
    if st.session_state.styles_data is None:
        with st.spinner("📡 Fetching Top 40 Styles data from NetSuite..."):
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
                if show_debug:
                    st.exception(e)
                st.stop()
    
    data = st.session_state.styles_data
    
    if data is None or data.empty:
        st.warning("⚠️ No data available for the selected filters")
    else:
        # KPI Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        total_sales = data['sales_dollars'].sum()
        total_units = data['sales_units'].sum()
        total_gp = data['gross_profit'].sum()
        avg_gm = (total_gp / total_sales * 100) if total_sales > 0 else 0
        
        with col1:
            st.metric("Total Sales", format_currency(total_sales))
        
        with col2:
            st.metric("Total Units", format_number(total_units))
        
        with col3:
            st.metric("Gross Profit", format_currency(total_gp))
        
        with col4:
            st.metric("Avg GM%", format_percentage(avg_gm))
        
        st.markdown("---")
        
        # Data Table
        st.subheader("📋 Top 40 Styles by Units")
        
        # Format for display
        display_df = data.copy()
        display_df['Sales $'] = display_df['sales_dollars'].apply(lambda x: f"${x:,.2f}")
        display_df['Gross Profit'] = display_df['gross_profit'].apply(lambda x: f"${x:,.2f}")
        display_df['GM%'] = display_df['gm_percent'].apply(lambda x: f"{x:.1f}%")
        display_df['Sales Units'] = display_df['sales_units'].apply(lambda x: f"{x:,.0f}")
        display_df['Returns'] = display_df['returns'].apply(lambda x: f"{x:,.0f}")
        display_df['Net Units'] = display_df['net_units'].apply(lambda x: f"{x:,.0f}")
        
        display_cols = [
            'rank', 'style', 'material_desc', 'color_desc', 'category', 'vendor',
            'Sales Units', 'Returns', 'Net Units', 'Sales $', 'Gross Profit', 'GM%'
        ]
        display_cols = [col for col in display_cols if col in display_df.columns]
        
        st.dataframe(
            display_df[display_cols],
            use_container_width=True,
            height=400,
            hide_index=True
        )
        
        st.metric("Total Styles", len(data))
        
        # Download button
        csv = data.to_csv(index=False)
        st.download_button(
            label="📥 Download Filtered Data as CSV",
            data=csv,
            file_name=f"top_40_styles_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
        
        # Drilldown Section
        st.markdown("---")
        st.subheader("🔍 Drilldown: View Customers")
        
        selected_style = st.selectbox(
            "Select a style to view customer purchases:",
            options=data['style'].unique(),
            key="style_selector"
        )
        
        if st.button("View Customers for this Style", key="drill_style"):
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
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
        
        # Display drilldown
        if st.session_state.drilldown_data is not None and st.session_state.drilldown_type == "style":
            st.markdown("---")
            st.subheader(f"🎯 Customers purchasing: {selected_style}")
            
            drill_df = st.session_state.drilldown_data.copy()
            drill_df['Sales $'] = drill_df['sales_dollars'].apply(lambda x: f"${x:,.2f}")
            drill_df['Gross Profit'] = drill_df['gross_profit'].apply(lambda x: f"${x:,.2f}")
            drill_df['GM%'] = drill_df['gm_percent'].apply(lambda x: f"{x:.1f}%")
            
            st.dataframe(drill_df, use_container_width=True, hide_index=True, height=300)
            
            # Chart
            if len(drill_df) > 0:
                chart_data = drill_df.head(10)
                chart = alt.Chart(chart_data).mark_bar().encode(
                    x=alt.X('sales_units:Q', title='Sales Units'),
                    y=alt.Y('customer:N', sort='-x', title='Customer'),
                    tooltip=['customer', 'sales_units', 'sales_dollars', 'gm_percent']
                ).properties(height=300, title=f'Top 10 Customers for {selected_style}')
                
                st.altair_chart(chart, use_container_width=True)
            
            # Download
            csv = drill_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Drilldown Data",
                data=csv,
                file_name=f"customers_{selected_style}_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )

# ──────────────────────────────────────────────────────────────────────────────
# TOP 40 CUSTOMERS TAB
# ──────────────────────────────────────────────────────────────────────────────

with tab2:
    st.markdown("---")
    
    # Load data
    if st.session_state.customers_data is None:
        with st.spinner("📡 Fetching Top 40 Customers data from NetSuite..."):
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
                if show_debug:
                    st.exception(e)
                st.stop()
    
    data = st.session_state.customers_data
    
    if data is None or data.empty:
        st.warning("⚠️ No data available for the selected filters")
    else:
        # KPI Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        total_sales = data['sales_dollars'].sum()
        total_units = data['sales_units'].sum()
        total_gp = data['gross_profit'].sum()
        avg_gm = (total_gp / total_sales * 100) if total_sales > 0 else 0
        
        with col1:
            st.metric("Total Sales", format_currency(total_sales))
        
        with col2:
            st.metric("Total Units", format_number(total_units))
        
        with col3:
            st.metric("Gross Profit", format_currency(total_gp))
        
        with col4:
            st.metric("Avg GM%", format_percentage(avg_gm))
        
        st.markdown("---")
        
        # Data Table
        st.subheader("📋 Top 40 Customers by Units")
        
        # Format for display
        display_df = data.copy()
        display_df['Sales $'] = display_df['sales_dollars'].apply(lambda x: f"${x:,.2f}")
        display_df['Gross Profit'] = display_df['gross_profit'].apply(lambda x: f"${x:,.2f}")
        display_df['GM%'] = display_df['gm_percent'].apply(lambda x: f"{x:.1f}%")
        display_df['Sales Units'] = display_df['sales_units'].apply(lambda x: f"{x:,.0f}")
        display_df['Returns'] = display_df['returns'].apply(lambda x: f"{x:,.0f}")
        display_df['Net Units'] = display_df['net_units'].apply(lambda x: f"{x:,.0f}")
        
        display_cols = [
            'rank', 'customer', 'category', 'vendor', 'territory',
            'Sales Units', 'Returns', 'Net Units', 'Sales $', 'Gross Profit', 'GM%'
        ]
        display_cols = [col for col in display_cols if col in display_df.columns]
        
        st.dataframe(
            display_df[display_cols],
            use_container_width=True,
            height=400,
            hide_index=True
        )
        
        st.metric("Total Customers", len(data))
        
        # Download button
        csv = data.to_csv(index=False)
        st.download_button(
            label="📥 Download Filtered Data as CSV",
            data=csv,
            file_name=f"top_40_customers_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
        
        # Drilldown Section
        st.markdown("---")
        st.subheader("🔍 Drilldown: View Styles")
        
        selected_customer = st.selectbox(
            "Select a customer to view purchased styles:",
            options=data['customer'].unique(),
            key="customer_selector"
        )
        
        if st.button("View Styles for this Customer", key="drill_customer"):
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
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
        
        # Display drilldown
        if st.session_state.drilldown_data is not None and st.session_state.drilldown_type == "customer":
            st.markdown("---")
            st.subheader(f"🎯 Styles purchased by: {selected_customer}")
            
            drill_df = st.session_state.drilldown_data.copy()
            drill_df['Sales $'] = drill_df['sales_dollars'].apply(lambda x: f"${x:,.2f}")
            drill_df['Gross Profit'] = drill_df['gross_profit'].apply(lambda x: f"${x:,.2f}")
            drill_df['GM%'] = drill_df['gm_percent'].apply(lambda x: f"{x:.1f}%")
            
            st.dataframe(drill_df, use_container_width=True, hide_index=True, height=300)
            
            # Chart
            if len(drill_df) > 0:
                chart_data = drill_df.head(10)
                chart = alt.Chart(chart_data).mark_bar().encode(
                    x=alt.X('sales_units:Q', title='Sales Units'),
                    y=alt.Y('style:N', sort='-x', title='Style'),
                    tooltip=['style', 'sales_units', 'sales_dollars', 'gm_percent']
                ).properties(height=300, title=f'Top 10 Styles for {selected_customer}')
                
                st.altair_chart(chart, use_container_width=True)
            
            # Download
            csv = drill_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Drilldown Data",
                data=csv,
                file_name=f"styles_{selected_customer.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )

# ──────────────────────────────────────────────────────────────────────────────
# FOOTER
# ──────────────────────────────────────────────────────────────────────────────

st.markdown("---")
st.caption(f"💾 Data last refreshed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
st.caption("Drew Shoe Corporation | Prepared by: Megan Spencer | Data Source: NetSuite")
st.caption("⚠️ Cost values are corrected from Merchandising inputs. NetSuite GM% is not used.")
