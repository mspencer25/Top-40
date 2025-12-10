# Top 40 Dashboard - Drew Shoe

Streamlit dashboard for Top 40 Styles and Top 40 Customers, connected to NetSuite via RESTlet API.

## 📋 Overview

This dashboard provides:
- **Top 40 Styles** ranked by sales units
- **Top 40 Customers** ranked by sales units
- Corrected Gross Margin calculations (not using NetSuite's built-in formula)
- Drilldown capabilities (Style → Customers, Customer → Styles)
- Dynamic filtering by date range, category, vendor, brand, and territory
- CSV export functionality

## 🏗️ Architecture

```
┌─────────────────┐
│  Streamlit UI   │
│    (app.py)     │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│ Data Processor  │
│(data_processor) │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│   NetSuite      │
│   Connector     │
│(netsuite_conn.) │
└────────┬────────┘
         │
         ↓ OAuth 1.0
┌─────────────────┐
│   NetSuite      │
│    RESTlet      │
└─────────────────┘
```

## 📁 File Structure

```
top40-dashboard/
├── app.py                    # Main Streamlit application
├── netsuite_connector.py     # NetSuite API connector with OAuth 1.0
├── data_processor.py         # Business logic and calculations
├── utils.py                  # Formatting utilities
├── requirements.txt          # Python dependencies
├── netsuite_restlet.js       # NetSuite RESTlet script (deploy in NS)
├── README.md                 # This file
└── .streamlit/
    └── config.toml           # Streamlit configuration
```

## 🚀 Setup Instructions

### 1. NetSuite Setup

#### A. Create Integration Record
1. Navigate to: **Setup > Integration > Manage Integrations > New**
2. Name: "Top 40 Dashboard Integration"
3. Enable **Token-Based Authentication**
4. Note the **Consumer Key** and **Consumer Secret**

#### B. Deploy RESTlet
1. Upload `netsuite_restlet.js` to NetSuite File Cabinet
2. Create new Script Record:
   - Type: RESTlet
   - Script File: (select uploaded file)
   - POST Function: `post`
3. Deploy Script:
   - Deployment Title: "Top 40 Dashboard RESTlet"
   - Status: Released
   - Audience: Select appropriate roles
4. **Copy the External URL** from deployment

#### C. Create Access Token
1. Navigate to: **Setup > Users/Roles > Access Tokens > New**
2. Application Name: Top 40 Dashboard Integration
3. User: (select user)
4. Role: (select role with data access)
5. Note the **Token ID** and **Token Secret**

#### D. Custom Fields (if not already present)
Ensure these custom fields exist in NetSuite:
- **Items:**
  - `custitem_style` - Style name
  - `custitem_material_desc` - Material description
  - `custitem_color_desc` - Color description
  - `custitem_corrected_cost` - Corrected cost value (from Annie)

- **Customers:**
  - `custentity_territory` - Sales territory

### 2. Python Environment Setup

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration

Update `netsuite_connector.py` line 36 with your actual RESTlet URL:

```python
self.restlet_url = restlet_url or "https://YOUR-ACCOUNT-ID.restlets.api.netsuite.com/app/site/hosting/restlet.nl?script=XXX&deploy=X"
```

### 4. Running the Dashboard

```bash
streamlit run app.py
```

The dashboard will open in your browser at `http://localhost:8501`

## 🔐 Security Notes

### Credentials Management

**DO NOT** hardcode credentials in the code. The dashboard requires:
- Account ID
- Consumer Key
- Consumer Secret
- Token ID
- Token Secret

These should be entered via the sidebar UI on first use.

### For Production Deployment

Use environment variables or a secure secrets manager:

```python
# Example using Streamlit secrets
import streamlit as st

account_id = st.secrets["netsuite"]["account_id"]
consumer_key = st.secrets["netsuite"]["consumer_key"]
# etc.
```

Create `.streamlit/secrets.toml`:
```toml
[netsuite]
account_id = "YOUR_ACCOUNT_ID"
consumer_key = "YOUR_CONSUMER_KEY"
consumer_secret = "YOUR_CONSUMER_SECRET"
token_id = "YOUR_TOKEN_ID"
token_secret = "YOUR_TOKEN_SECRET"
```

**IMPORTANT:** Add `.streamlit/secrets.toml` to `.gitignore`

## 📊 Business Rules

### Derived Metrics

1. **Net Units** = Sales Units - Returns
2. **Gross Profit** = Retail - Cost
3. **GM%** = (Retail - Cost) / Retail

### Null Handling

| Field | Rule |
|-------|------|
| Sales Units, Dollars, Returns | Default to 0 |
| Cost | Default to 0 (flag for review) |
| Retail | Use NetSuite retail price |
| Category, Vendor | "Unknown" |
| Material Description | "Unknown" |

### Ranking Logic

- **Top 40 Styles:** Ranked by Sales Units (descending)
- **Top 40 Customers:** Ranked by Sales Units (descending)
- Rankings are **fixed** (no toggle between units/dollars)

## 🔍 Features

### Filters
- **Date Range:** Calendar picker + manual entry
- **Category:** Multi-select
- **Vendor:** Multi-select
- **Brand:** Multi-select (where applicable)
- **Territory:** Multi-select (customers only)

### Drilldowns
- Click any **Style** → View all customers who purchased it
- Click any **Customer** → View all styles they purchased

### Exports
- CSV export maintains current filter context
- Includes all visible columns
- Timestamped filenames

### KPI Tiles
Optional summary tiles showing:
- Total Sales Dollars
- Total Units
- Total Gross Profit
- Average GM%

## 🛠️ Troubleshooting

### Connection Issues

**Problem:** "OAuth authentication failed"
- Verify all credentials are correct
- Ensure token is not expired
- Check that integration is active in NetSuite
- Verify user has appropriate role permissions

**Problem:** "RESTlet URL not found"
- Confirm RESTlet is deployed and released
- Check that deployment status is "Released"
- Verify URL in `netsuite_connector.py` matches deployment

### Data Issues

**Problem:** "No data returned"
- Check date range (data exists for selected period?)
- Verify saved search IDs in RESTlet are correct
- Check NetSuite field IDs match custom fields
- Review NetSuite script execution log

**Problem:** "Incorrect GM% values"
- Ensure `custitem_corrected_cost` field is populated
- Verify cost/retail data source (Annie's master file)
- Check that RESTlet's `getCostRetailData()` function is properly implemented

### Performance Issues

**Problem:** "Dashboard is slow to load"
- Consider caching data with `@st.cache_data`
- Reduce date range for initial testing
- Add pagination for large result sets
- Optimize NetSuite saved searches

## 📝 Known Limitations

From CRISP documentation:

1. **NetSuite Cost Values:** Unreliable due to tariff/duty manipulation
   - **Solution:** Use corrected cost values from Merchandising

2. **Color Codes:** Inconsistent meaning across teams
   - **Solution:** Use Material Description instead

3. **Item Master Inconsistencies:** Parent items may have color/width values
   - **Solution:** Ongoing cleanup by Megan

4. **Table Naming:** NetSuite tables inconsistently named across modules
   - **Solution:** RESTlet normalizes field names

## 🔄 Maintenance

### Regular Tasks

1. **Weekly:** Verify cost/retail data sync from Annie's master
2. **Monthly:** Review and clean up Item Master inconsistencies
3. **Quarterly:** Audit customer category assignments
4. **As Needed:** Update territory mappings

### Future Enhancements

Per CRISP documentation:

1. **Inventory Dashboard:** Size/width reporting with subtotals
2. **AI-Powered Forecasting:** 12-month predictions using historical data
3. **Automated Anomaly Detection:** Flag unusual patterns
4. **Advanced Visualizations:** Charts and graphs (optional)

## 👥 Support

**Primary Users:**
- Annie Bumgarner (Merchandising)
- Terry Wilson (Sales)
- Shirley Mortland (DTC)
- Marc Tishkoff (Leadership)

**Technical Contact:**
- Megan Spencer (Data/Analytics)
- Troy (Data Rules Review)

## 📄 References

- **CRISP Documentation:** See `Top 40 Styles & Customers - Finalized.md`
- **Fireflies Transcript:** Reference timestamps 24:00-26:30 (GM calculation), 39:30-41:20 (drilldowns)
- **Jira Story:** DS-XX
- **Epic:** Merchandising Quick Wins

## 📅 Change Log

| Date | Version | Changes |
|------|---------|---------|
| 2025-12-10 | 1.0.0 | Initial release |

---

**Drew Shoe Corporation** | Merchandising Quick Wins Initiative
