#!/bin/bash

# Top 40 Dashboard Installation Script
# Drew Shoe Corporation
# Run this script to set up your dashboard environment

echo "========================================"
echo "  Top 40 Dashboard Setup"
echo "  Drew Shoe Corporation"
echo "========================================"
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | grep -oP '(?<=Python )\d+\.\d+')
required_version="3.11"

if [ -z "$python_version" ]; then
    echo "❌ Python 3 not found. Please install Python 3.11 or higher."
    exit 1
fi

echo "✅ Python $python_version found"

# Create virtual environment
echo ""
echo "Creating virtual environment..."
if [ -d "venv" ]; then
    echo "⚠️  Virtual environment already exists. Skipping..."
else
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo "✅ Dependencies installed"

# Create secrets directory if it doesn't exist
echo ""
echo "Setting up configuration..."
mkdir -p .streamlit

if [ -f ".streamlit/secrets.toml" ]; then
    echo "⚠️  secrets.toml already exists. Skipping..."
else
    echo "📝 Creating secrets template..."
    cp secrets.toml.template .streamlit/secrets.toml
    echo "✅ secrets.toml created"
    echo ""
    echo "⚠️  IMPORTANT: Edit .streamlit/secrets.toml with your NetSuite credentials!"
fi

# Test import of all modules
echo ""
echo "Testing module imports..."
python3 -c "import streamlit; import pandas; import plotly; import requests" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ All modules imported successfully"
else
    echo "❌ Some modules failed to import"
    exit 1
fi

echo ""
echo "========================================"
echo "  Installation Complete! ✅"
echo "========================================"
echo ""
echo "Next Steps:"
echo ""
echo "1. Configure NetSuite credentials:"
echo "   nano .streamlit/secrets.toml"
echo ""
echo "2. Deploy RESTlet to NetSuite:"
echo "   See README.md section 'NetSuite Setup'"
echo ""
echo "3. Test the connection:"
echo "   python test_dashboard.py"
echo ""
echo "4. Run the dashboard:"
echo "   streamlit run app.py"
echo ""
echo "For more information, see:"
echo "  - QUICKSTART.md - 5-minute guide"
echo "  - README.md - Full documentation"
echo "  - DEPLOYMENT.md - Production deployment"
echo ""
echo "Need help? Contact: Megan Spencer"
echo ""
