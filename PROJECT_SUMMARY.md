# Top 40 Dashboard - Project Summary

## 📊 Project Overview

**Project Name:** Top 40 Styles & Customers Dashboard  
**Business Unit:** Merchandising / Sales  
**Epic:** Merchandising Quick Wins  
**Jira Story:** DS-XX  
**Status:** Ready for Development  
**Prepared By:** Megan Spencer  
**Date:** December 10, 2025  

## 🎯 Business Objectives

### Primary Goal
Provide a unified, accurate, and drillable view of:
1. **Top 40 selling styles** ranked by units
2. **Top 40 customers** ranked by units

### Key Improvements Over Current State
- ✅ Eliminates manual NetSuite exports
- ✅ Corrects unreliable GM% calculations
- ✅ Provides drill-down visibility
- ✅ Enables quick filtering and export
- ✅ Supports daily/weekly decision-making

### Primary Users
- **Annie Bumgarner** - Merchandising
- **Terry Wilson** - Sales
- **Shirley Mortland** - DTC
- **Marc Tishkoff** - Leadership

## 📦 Deliverables

### Core Components

1. **Streamlit Dashboard Application** (`app.py`)
   - Interactive web interface
   - Two main tabs: Top 40 Styles & Top 40 Customers
   - Dynamic filtering and drilldown
   - CSV export functionality

2. **NetSuite API Connector** (`netsuite_connector.py`)
   - OAuth 1.0 authentication
   - RESTlet communication
   - Transaction data retrieval
   - Master data access

3. **Data Processor** (`data_processor.py`)
   - Business logic implementation
   - Derived metric calculations
   - Null handling per CRISP rules
   - Filter application

4. **NetSuite RESTlet** (`netsuite_restlet.js`)
   - Server-side data access
   - Saved search execution
   - Custom field handling
   - Cost/retail data retrieval

5. **Supporting Files**
   - `utils.py` - Formatting utilities
   - `requirements.txt` - Python dependencies
   - `.streamlit/config.toml` - UI configuration
   - `.gitignore` - Security exclusions

### Documentation

1. **README.md** - Comprehensive technical documentation
2. **DEPLOYMENT.md** - Production deployment guide
3. **QUICKSTART.md** - 5-minute getting started guide
4. **secrets.toml.template** - Configuration template
5. **test_dashboard.py** - Automated testing script

## 🔧 Technical Architecture

### Technology Stack

**Frontend:**
- Streamlit 1.29.0
- Plotly 5.18.0 (for visualizations)

**Backend:**
- Python 3.11+
- Pandas 2.1.4 (data processing)
- Requests 2.31.0 (API calls)

**Integration:**
- NetSuite RESTlet API
- OAuth 1.0 authentication
- HMAC-SHA256 signing

### Data Flow

```
User Input (Filters/Date Range)
    ↓
Streamlit UI (app.py)
    ↓
Data Processor (business logic)
    ↓
NetSuite Connector (OAuth)
    ↓
NetSuite RESTlet (server-side)
    ↓
NetSuite Data (transactions, items, customers)
    ↓
← Data Processing ←
    ↓
Calculated Metrics
    ↓
UI Display + Export
```

### Key Features

**Filtering:**
- Date Range (manual entry + calendar)
- Category (multi-select)
- Vendor (multi-select)
- Brand (multi-select)
- Territory (multi-select, customers only)

**Drilldowns:**
- Style → List of customers who purchased
- Customer → List of styles purchased

**Calculations:**
- Net Units = Sales Units - Returns
- Gross Profit = Retail - Cost
- GM% = (Retail - Cost) / Retail

**Exports:**
- CSV format
- Preserves filter context
- Timestamped filenames

## 📋 Business Rules (from CRISP)

### Ranking Logic
- **Fixed ranking by Sales Units** (no toggles)
- Always descending order
- Top 40 only (not configurable)

### Null Handling

| Field | Rule |
|-------|------|
| Sales Units, Dollars, Returns | Default to 0 |
| Cost | Default to 0 (flag for review) |
| Retail | Use NetSuite retail price |
| Category, Vendor, Territory | "Unknown" |
| Material/Color Description | "Unknown" |

### Data Quality Issues

**Known Issues:**
1. NetSuite cost values unreliable (tariff/duty manipulation)
2. Color codes inconsistent across teams
3. Item Master parent items may have color/width values
4. NetSuite tables inconsistently named

**Solutions Implemented:**
1. Use Merchandising-provided corrected costs
2. Prefer Material Description over color codes
3. Ongoing cleanup by Megan
4. RESTlet normalizes field names

## 🚀 Deployment Options

### Option 1: Streamlit Cloud (Recommended)
- Push to GitHub
- Deploy via Streamlit Cloud
- Manage secrets in cloud UI
- Automatic HTTPS
- Free for internal use

### Option 2: Docker Container
- Build Docker image
- Deploy to AWS ECS, Azure ACI, or local
- Use environment variables for secrets
- Scalable and portable

### Option 3: Traditional Server
- Python virtual environment
- Nginx reverse proxy
- Systemd service management
- SSL certificate required

## 🔐 Security Considerations

### Credentials
- **NEVER** commit to version control
- Use Streamlit secrets or environment variables
- Rotate tokens regularly
- Restrict RESTlet access by role

### Network
- Deploy in private subnet (production)
- Use HTTPS only
- Implement rate limiting
- Enable CORS protection

### Authentication
- Add SSO for enterprise deployment
- Implement role-based access control
- Log all data access
- Session timeout after inactivity

## 📈 Success Metrics

### Immediate (Week 1)
- ✅ Dashboard deployed and accessible
- ✅ All users successfully connected
- ✅ Data validated against NetSuite exports
- ✅ Drilldowns working correctly

### Short Term (Month 1)
- 📊 Daily usage by Merchandising team
- 📊 Weekly usage by Sales team
- 📊 Reduced manual export time by 80%
- 📊 Correct GM% calculations verified

### Long Term (Quarter 1)
- 📈 Data-driven merchandising decisions
- 📈 Improved style selection accuracy
- 📈 Better customer targeting
- 📈 Foundation for AI forecasting

## 🛠️ Maintenance Plan

### Daily
- Monitor application logs
- Check NetSuite API rate limits

### Weekly
- Verify cost/retail data sync from Annie
- Validate calculations with business users
- Review error logs

### Monthly
- Update Python dependencies
- Clean up Item Master inconsistencies
- Optimize slow queries

### Quarterly
- Full security audit
- Performance optimization
- User feedback session
- Documentation updates

## ⚠️ Known Limitations

1. **NetSuite Rate Limits**
   - Solution: Implement caching, throttling

2. **Cost Data Accuracy**
   - Dependency on Annie's manual updates
   - Solution: Automate cost/retail sync

3. **Large Date Ranges**
   - May cause performance issues
   - Solution: Implement pagination, optimize queries

4. **Real-Time Data**
   - Not truly real-time (API calls)
   - Solution: Acceptable for daily/weekly use

## 🔄 Future Enhancements

### Phase 2 (Q1 2026)
1. **Inventory Dashboard**
   - Size/width distribution
   - Stock levels by style
   - Reorder recommendations

2. **Advanced Visualizations**
   - Trend charts
   - Heat maps
   - Geographic sales maps

3. **Automated Alerts**
   - Low stock warnings
   - Margin threshold alerts
   - Anomaly detection

### Phase 3 (Q2 2026)
1. **AI-Powered Forecasting**
   - 12-month demand predictions
   - Seasonal pattern recognition
   - Buy recommendation engine

2. **Mobile App**
   - Native iOS/Android
   - Offline capability
   - Push notifications

3. **Integration Expansion**
   - Direct Google Drive sync
   - Slack notifications
   - Email scheduled reports

## 📞 Support & Contacts

### Technical Support
- **Developer:** Megan Spencer
- **Data Rules:** Troy
- **NetSuite Admin:** [To be assigned]

### Business Support
- **Merchandising:** Annie Bumgarner
- **Sales:** Terry Wilson
- **DTC:** Shirley Mortland
- **Leadership:** Marc Tishkoff

### Escalation Path
1. Check documentation (README, QUICKSTART)
2. Run test script (`python test_dashboard.py`)
3. Contact Megan Spencer (technical)
4. Contact Troy (data rules)
5. Escalate to Marc Tishkoff (if business critical)

## 📚 Documentation Index

| Document | Purpose | Audience |
|----------|---------|----------|
| README.md | Technical documentation | Developers |
| DEPLOYMENT.md | Deployment guide | DevOps/IT |
| QUICKSTART.md | Getting started | End users |
| test_dashboard.py | Automated testing | QA/Developers |
| netsuite_restlet.js | Server-side script | NetSuite admins |
| CRISP.md | Business requirements | All stakeholders |

## ✅ Acceptance Criteria

Dashboard is considered complete and ready for production when:

- [ ] All Python dependencies installed successfully
- [ ] NetSuite connection established and tested
- [ ] RESTlet deployed and accessible
- [ ] Top 40 Styles report loads with correct data
- [ ] Top 40 Customers report loads with correct data
- [ ] All filters function correctly
- [ ] Drilldowns work in both directions
- [ ] GM% calculations verified as correct
- [ ] CSV exports work with all data
- [ ] All unit tests pass
- [ ] Documentation complete and accurate
- [ ] Users trained on dashboard usage
- [ ] Security review passed
- [ ] Performance acceptable (<5 sec load time)
- [ ] Backup/recovery plan in place

## 📝 Change Log

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2025-12-10 | 1.0.0 | Initial release | Megan Spencer |

## 🎉 Conclusion

This dashboard represents a significant upgrade to Drew Shoe's merchandising analytics capabilities. By providing accurate, timely, and actionable insights, it empowers the Merchandising and Sales teams to make better decisions and identify opportunities more quickly.

The modular architecture and comprehensive documentation ensure the solution is maintainable and extensible for future enhancements.

**Status:** Ready for deployment and testing  
**Next Steps:** Deploy to development environment for user acceptance testing

---

**Drew Shoe Corporation**  
**Merchandising Quick Wins Initiative**  
**Prepared by:** Megan Spencer  
**Date:** December 10, 2025
