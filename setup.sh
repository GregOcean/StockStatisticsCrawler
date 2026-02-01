#!/bin/bash
# Setup script for Stock Statistics Crawler

set -e  # Exit on error

echo "================================"
echo "Stock Crawler - Setup Script"
echo "================================"
echo ""

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "✓ Virtual environment already exists"
else
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

echo ""
echo "Activating virtual environment..."
source venv/bin/activate

echo "✓ Virtual environment activated"
echo ""

echo "Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
echo "✓ pip upgraded"
echo ""

echo "Installing dependencies..."
pip install -r requirements.txt
echo "✓ Dependencies installed"
echo ""

echo "================================"
echo "Setup Complete!"
echo "================================"
echo ""
echo "To activate the virtual environment in the future:"
echo "  source venv/bin/activate"
echo ""
echo "To run the application:"
echo "  python test_setup.py        # Run tests"
echo "  python src/main.py --mode once  # Run once"
echo "  make once                   # Using Makefile"
echo ""
echo "To deactivate:"
echo "  deactivate"
echo ""

