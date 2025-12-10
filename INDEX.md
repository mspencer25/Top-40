# Top 40 Dashboard - Complete Package

## 📦 What's Included

This package contains everything needed to deploy the Top 40 Styles and Customers Dashboard for Drew Shoe Corporation.

## 📁 File Structure

```
top40-dashboard/
│
├── 🚀 GETTING STARTED
│   ├── QUICKSTART.md          ← Start here! 5-minute setup guide
│   ├── install.sh              ← Mac/Linux installation script
│   └── install.bat             ← Windows installation script
│
├── 📱 APPLICATION FILES
│   ├── app.py                  ← Main Streamlit dashboard
│   ├── netsuite_connector.py   ← NetSuite API integration
│   ├── data_processor.py       ← Business logic & calculations
│   ├── utils.py                ← Formatting utilities
│   └── test_dashboard.py       ← Automated testing
│
├── 🔧 NETSUITE FILES
│   └── netsuite_restlet.js     ← Deploy this to NetSuite
│
├── ⚙️ CONFIGURATION
│   ├── requirements.txt        ← Python dependencies
│   ├── secrets.toml.template   ← Credentials template
│   ├── .streamlit/
│   │   └── config.toml         ← UI configuration
│   └── .gitignore              ← Security exclusions
│
└── 📚 DOCUMENTATION
    ├── INDEX.md                ← This file
    ├── PROJECT_SUMMARY.md      ← Executive summary
    ├── README.md               ← Full technical docs
    └── DEPLOYMENT.md           ← Production deployment guide
```

## 🎯 Quick Navigation

### For Business Users
- **"I want to use the dashboard"** → QUICKSTART.md
- **"What does this dashboard do?"** → PROJECT_SUMMARY.md (Section: Overview)
- **"How do I export data?"** → QUICKSTART.md (Section: Common Tasks)

### For Developers
- **"How do I install it?"** → QUICKSTART.md OR run `./install.sh`
- **"How does it work?"** → README.md
- **"How do I test it?"** → Run `python test_dashboard.py`
- **"How do I customize it?"** → README.md (Section: Customization)

### For IT/DevOps
- **"How do I deploy to production?"** → DEPLOYMENT.md
- **"What are the security requirements?"** → DEPLOYMENT.md (Section: Security)
- **"What infrastructure is needed?"** → DEPLOYMENT.md (Section: Deployment Options)

### For NetSuite Admins
- **"How do I set up the RESTlet?"** → README.md (Section: NetSuite Setup)
- **"What permissions are needed?"** → README.md (Section: NetSuite Setup)
- **"How do I troubleshoot API issues?"** → README.md (Section: Troubleshooting)

## 🚀 Installation Steps

### Quick Install (Recommended)

**Mac/Linux:**
```bash
chmod +x install.sh
./install.sh
```

**Windows:**
```batch
install.bat
```

### Manual Install

1. **Install Python 3.11+**
   - Download from python.org

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Mac/Linux
   venv\Scripts\activate     # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure credentials**
   ```bash
   cp secrets.toml.template .streamlit/secrets.toml
   # Edit .streamlit/secrets.toml with your NetSuite credentials
   ```

5. **Deploy NetSuite RESTlet**
   - Upload `netsuite_restlet.js` to NetSuite
   - Create Script Record
   - Deploy and get URL
   - Update URL in `netsuite_connector.py`

6. **Run dashboard**
   ```bash
   streamlit run app.py
   ```

## 📊 Key Features

### Top 40 Styles
- ✅ Ranked by sales units (fixed)
- ✅ Corrected Gross Margin calculations
- ✅ Drill down to see customers who purchased
- ✅ Filter by category, vendor, brand
- ✅ Export to CSV

### Top 40 Customers
- ✅ Ranked by sales units (fixed)
- ✅ Corrected Gross Margin calculations
- ✅ Drill down to see styles purchased
- ✅ Filter by category, vendor, brand, territory
- ✅ Export to CSV

### Derived Metrics
- **Net Units** = Sales Units - Returns
- **Gross Profit** = Retail - Cost
- **GM%** = (Retail - Cost) / Retail

## ⚙️ Technology Stack

| Component | Technology |
|-----------|------------|
| Frontend | Streamlit 1.29.0 |
| Backend | Python 3.11+ |
| Data Processing | Pandas 2.1.4 |
| Visualization | Plotly 5.18.0 |
| API | NetSuite RESTlet |
| Authentication | OAuth 1.0 |

## 🔐 Security Checklist

Before deploying to production:

- [ ] Credentials stored in secrets manager (not in code)
- [ ] .gitignore includes secrets.toml
- [ ] NetSuite RESTlet restricted by role
- [ ] HTTPS enabled (production)
- [ ] Rate limiting configured
- [ ] Logging enabled
- [ ] Backup plan documented

## 🧪 Testing

Run automated tests:
```bash
python test_dashboard.py
```

Tests cover:
- ✅ NetSuite connection
- ✅ Sales transactions retrieval
- ✅ Item master data
- ✅ Customer master data
- ✅ Data processing & calculations
- ✅ Drilldown functionality
- ✅ Filtering

## 📞 Support

### Contacts
- **Technical:** Megan Spencer
- **Business Rules:** Annie Bumgarner (Merch), Terry Wilson (Sales)
- **Data Rules:** Troy

### Resources
- **Documentation:** See files in this package
- **Testing:** `python test_dashboard.py`
- **Issues:** Report to Megan Spencer

### Common Issues

| Issue | Solution |
|-------|----------|
| Connection failed | Check credentials, verify RESTlet deployed |
| No data showing | Verify date range, check filters |
| Wrong GM% | Ensure cost/retail data synced from Annie |
| Slow performance | Narrow date range, enable caching |

## 🎓 Training Materials

### For End Users
1. Watch: Getting Started video (TBD)
2. Read: QUICKSTART.md
3. Practice: Use with test data first
4. Reference: README.md for details

### For Developers
1. Read: README.md (technical architecture)
2. Review: Code comments in Python files
3. Test: Run test_dashboard.py
4. Experiment: Modify and test locally

### For Admins
1. Read: DEPLOYMENT.md
2. Review: NetSuite RESTlet code
3. Plan: Choose deployment strategy
4. Execute: Follow deployment guide

## 📅 Roadmap

### ✅ Phase 1 (Current)
- Top 40 Styles dashboard
- Top 40 Customers dashboard
- Corrected GM calculations
- Drilldown capability
- CSV export

### 🔄 Phase 2 (Q1 2026)
- Inventory dashboard
- Size/width distributions
- Advanced visualizations
- Automated alerts

### 🚀 Phase 3 (Q2 2026)
- AI-powered forecasting
- Mobile app
- Integration with other systems
- Predictive analytics

## 📖 Documentation Guide

| Document | Length | Purpose | Audience |
|----------|--------|---------|----------|
| INDEX.md | 5 min | Navigation & overview | Everyone |
| QUICKSTART.md | 5 min | Get started fast | End users |
| PROJECT_SUMMARY.md | 10 min | Executive overview | Management |
| README.md | 20 min | Technical details | Developers |
| DEPLOYMENT.md | 30 min | Production setup | DevOps/IT |

## ✅ Pre-Deployment Checklist

Before going live:

### Technical
- [ ] All Python dependencies installed
- [ ] NetSuite connection tested
- [ ] RESTlet deployed and accessible
- [ ] Test script passes all tests
- [ ] Data validates against NetSuite exports
- [ ] Performance is acceptable (<5 sec)

### Business
- [ ] GM calculations verified by Annie
- [ ] Drilldowns match expectations
- [ ] Filters work correctly
- [ ] Export functionality tested
- [ ] Users trained on dashboard

### Security
- [ ] Credentials secured (not in code)
- [ ] Access controls configured
- [ ] Logging enabled
- [ ] Backup plan documented
- [ ] Security review completed

### Documentation
- [ ] All docs reviewed and accurate
- [ ] Known issues documented
- [ ] Support contacts updated
- [ ] User guide distributed
- [ ] Change log updated

## 🎉 Success Criteria

Dashboard is successful when:

- ✅ Daily usage by Merchandising team
- ✅ Weekly usage by Sales team
- ✅ 80% reduction in manual exports
- ✅ Correct GM% calculations validated
- ✅ Data-driven decisions being made
- ✅ Positive user feedback
- ✅ Foundation for future enhancements

## 📝 Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-12-10 | Initial release |

## 🙏 Acknowledgments

**Business Requirements:**
- Annie Bumgarner (Merchandising)
- Terry Wilson (Sales)
- Shirley Mortland (DTC)
- Marc Tishkoff (Leadership)

**Technical Implementation:**
- Megan Spencer (Developer)
- Troy (Data Rules)

**Based On:**
- CRISP Methodology
- Merchandising Quick Wins Initiative
- Fireflies meeting transcripts

---

## 🚀 Ready to Start?

1. **First time?** → Read QUICKSTART.md
2. **Deploying?** → Read DEPLOYMENT.md
3. **Questions?** → Read README.md
4. **Need help?** → Contact Megan Spencer

**Let's get started! 🎯**

---

**Drew Shoe Corporation**  
**Merchandising Quick Wins Initiative**  
**December 10, 2025**
