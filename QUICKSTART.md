# Quick Start Guide - Top 40 Dashboard

## Get Started in 5 Minutes

### Step 1: Install Python (if not already installed)

Download Python 3.11+ from [python.org](https://www.python.org/downloads/)

Verify installation:
```bash
python --version
```

### Step 2: Set Up Project

```bash
# Create project directory
mkdir top40-dashboard
cd top40-dashboard

# Copy all project files to this directory

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Configure NetSuite

#### A. Get Your Credentials

You need 5 pieces of information from NetSuite:

1. **Account ID** - Your NetSuite account number
   - Format: `1234567` or `1234567_SB1` (for sandbox)
   
2. **Consumer Key & Secret** - From Integration Record
   - Setup > Integration > Manage Integrations > New
   - Enable "Token-Based Authentication"
   - Save the Consumer Key and Consumer Secret
   
3. **Token ID & Secret** - From Access Token
   - Setup > Users/Roles > Access Tokens > New
   - Select your integration
   - Save the Token ID and Token Secret

#### B. Deploy RESTlet

1. Upload `netsuite_restlet.js` to NetSuite File Cabinet
   - Documents > Files > File Cabinet > SuiteScripts > (create folder: Top40)
   
2. Create Script Record
   - Customization > Scripting > Scripts > New
   - Script Type: RESTlet
   - File: Select uploaded netsuite_restlet.js
   - POST Function: `post`
   - Save
   
3. Deploy Script
   - Click "Deploy Script"
   - Status: Released
   - Log Level: Debug (for testing)
   - Audience: Select appropriate roles/users
   - Save
   - **Copy the External URL**

#### C. Update Configuration

Open `netsuite_connector.py` and update line 36:

```python
self.restlet_url = restlet_url or "YOUR_RESTLET_URL_HERE"
```

### Step 4: Run the Dashboard

```bash
streamlit run app.py
```

The dashboard will open automatically at: `http://localhost:8501`

### Step 5: Connect to NetSuite

1. Click the sidebar expansion arrow `>`
2. Expand "🔐 NetSuite Connection"
3. Enter your credentials:
   - Account ID
   - Consumer Key
   - Consumer Secret
   - Token ID
   - Token Secret
4. Click "Connect to NetSuite"

✅ You should see: "Connected to NetSuite successfully!"

### Step 6: Use the Dashboard

1. **Select Date Range**
   - Use calendar pickers or manual entry
   
2. **Apply Filters** (optional)
   - Category
   - Vendor
   - Brand
   - Territory
   
3. **Choose Report Tab**
   - "Top 40 Styles" - Best selling styles
   - "Top 40 Customers" - Top purchasing customers
   
4. **View Data**
   - See KPI tiles at top
   - Browse table of results
   
5. **Drill Down**
   - Select a style to see which customers bought it
   - Select a customer to see which styles they purchased
   
6. **Export**
   - Click "📥 Export to CSV" to download data

## Troubleshooting

### Issue: "Connection failed"

**Check:**
- Are all credentials correct?
- Is RESTlet deployed and released?
- Does user have appropriate role permissions?
- Is token expired? (Create new token)

**Solution:**
```bash
# Test connection manually
python test_dashboard.py
```

### Issue: "No data available"

**Check:**
- Date range has actual sales data
- Filters aren't too restrictive
- NetSuite saved searches are working

**Solution:**
- Try wider date range (last 90 days)
- Reset all filters to "All"
- Check NetSuite data directly

### Issue: "Module not found"

**Check:**
- Virtual environment is activated
- All dependencies installed

**Solution:**
```bash
# Reactivate virtual environment
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: "Port 8501 already in use"

**Solution:**
```bash
# Use different port
streamlit run app.py --server.port 8502
```

## Common Tasks

### Change RESTlet URL

Edit `netsuite_connector.py`, line 36:
```python
self.restlet_url = "new_url_here"
```

### Update Date Range

Sidebar > Date Range > Select new dates

### Export All Data

1. Set filters as needed
2. Click "Export to CSV"
3. File saves to Downloads folder

### Clear Cache

Sidebar > "🔄 Refresh Data"

## Need Help?

### Resources
- 📖 Full documentation: `README.md`
- 🚀 Deployment guide: `DEPLOYMENT.md`
- 🧪 Run tests: `python test_dashboard.py`

### Contacts
- **Technical:** Megan Spencer
- **Business Rules:** Annie Bumgarner, Terry Wilson
- **Data Rules:** Troy

### Support Checklist

Before asking for help, please:
- [ ] Check this Quick Start Guide
- [ ] Run `python test_dashboard.py`
- [ ] Review application logs
- [ ] Check NetSuite script execution logs
- [ ] Verify all credentials are current
- [ ] Try with "All" filters

### Reporting Issues

Include:
1. Error message (full text)
2. What you were trying to do
3. Steps to reproduce
4. Screenshots (if UI issue)
5. Test results (from test_dashboard.py)

## Next Steps

Once you're comfortable with basics:

1. **Schedule Automated Reports**
   - Set up regular data exports
   - Email reports to stakeholders

2. **Add Authentication**
   - Restrict dashboard access
   - Use corporate SSO

3. **Deploy to Production**
   - See `DEPLOYMENT.md`
   - Use Streamlit Cloud or Docker

4. **Customize**
   - Add more KPI tiles
   - Create visualizations
   - Add alerts for anomalies

## Pro Tips

### Keyboard Shortcuts
- `R` - Refresh/rerun app
- `C` - Clear cache
- `/` - Focus search

### Performance
- Use narrower date ranges for faster loading
- Apply filters before loading data
- Export large datasets instead of viewing in browser

### Data Quality
- Check GM% calculations match expectations
- Verify drilldowns sum correctly
- Report any Item Master inconsistencies to Megan

### Best Practices
- Refresh data weekly
- Export important snapshots
- Document any manual adjustments
- Report bugs/issues promptly

---

**Ready to Go!** 🚀

You should now have a working dashboard. If you encounter any issues, refer to the troubleshooting section or contact support.

**Last Updated:** Dec 10, 2025
