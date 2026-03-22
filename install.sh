#!/bin/bash

# Creedom AI Intelligence Agent - Quick Installation Script
# This script helps beginners set up everything automatically

echo "=================================="
echo "🤖 Creedom AI Agent Setup"
echo "=================================="
echo ""
echo "This script will help you set up the Creedom AI Agent"
echo "Everything is 100% FREE!"
echo ""

# Check if Python is installed
echo "📋 Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed!"
    echo ""
    echo "Please install Python first:"
    echo "  - Windows: https://python.org/downloads"
    echo "  - Mac: python3 should be pre-installed"
    echo "  - Linux: sudo apt install python3 python3-pip"
    echo ""
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo "✅ Found $PYTHON_VERSION"
echo ""

# Check if pip is installed
echo "📋 Checking pip installation..."
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip is not installed!"
    echo "Installing pip..."
    python3 -m ensurepip --default-pip
fi
echo "✅ pip is ready"
echo ""

# Install required packages
echo "📦 Installing required Python packages..."
echo "This may take 1-2 minutes..."
pip3 install -r requirements.txt --quiet
if [ $? -eq 0 ]; then
    echo "✅ All packages installed successfully"
else
    echo "❌ Package installation failed"
    echo "Try running manually: pip3 install praw requests python-dateutil"
    exit 1
fi
echo ""

# Create config.py if it doesn't exist
if [ -f "config.py" ]; then
    echo "⚠️  config.py already exists - skipping creation"
    echo ""
else
    echo "📝 Creating configuration file..."
    cp config_template.py config.py
    echo "✅ Created config.py from template"
    echo ""
fi

# Check if config.py is filled in
if grep -q "your_client_id_here" config.py; then
    echo "⚠️  IMPORTANT: You need to configure config.py!"
    echo ""
    echo "📖 Next steps:"
    echo "1. Open config.py in a text editor"
    echo "2. Follow SETUP_GUIDE.md to get:"
    echo "   - Reddit API credentials (Step 3)"
    echo "   - Gmail App Password (Step 4)"
    echo "3. Fill in your information in config.py"
    echo "4. Run: python3 run_agent.py"
    echo ""
    echo "📚 For detailed instructions, see SETUP_GUIDE.md"
    echo ""

    # Offer to open the guide
    read -p "Would you like to open SETUP_GUIDE.md now? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if command -v xdg-open &> /dev/null; then
            xdg-open SETUP_GUIDE.md
        elif command -v open &> /dev/null; then
            open SETUP_GUIDE.md
        else
            echo "Please open SETUP_GUIDE.md manually"
        fi
    fi
else
    echo "✅ config.py appears to be configured!"
    echo ""
    echo "🚀 Ready to run! Try: python3 run_agent.py"
    echo ""

    # Offer to run the agent
    read -p "Would you like to run the agent now? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo ""
        echo "=================================="
        echo "🤖 Running Creedom Agent..."
        echo "=================================="
        echo ""
        python3 run_agent.py
    fi
fi

echo ""
echo "=================================="
echo "✅ Setup Complete!"
echo "=================================="
echo ""
echo "📖 Resources:"
echo "  - SETUP_GUIDE.md - Complete beginner's guide"
echo "  - GITHUB_ACTIONS_GUIDE.md - Run in the cloud for free"
echo "  - README.md - Technical documentation"
echo ""
echo "🎯 Quick commands:"
echo "  - Run agent: python3 run_agent.py"
echo "  - View stats: python3 run_agent.py --stats"
echo "  - Test config: python3 config.py"
echo ""
echo "💡 Need help? See SETUP_GUIDE.md or open a GitHub issue"
echo ""
