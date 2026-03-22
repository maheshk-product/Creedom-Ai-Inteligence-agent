@echo off
REM Creedom AI Intelligence Agent - Quick Installation Script for Windows
REM This script helps beginners set up everything automatically

echo ==================================
echo 🤖 Creedom AI Agent Setup
echo ==================================
echo.
echo This script will help you set up the Creedom AI Agent
echo Everything is 100%% FREE!
echo.

REM Check if Python is installed
echo 📋 Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed!
    echo.
    echo Please install Python first:
    echo   Download from: https://python.org/downloads
    echo   IMPORTANT: Check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo ✅ Found %PYTHON_VERSION%
echo.

REM Check if pip is installed
echo 📋 Checking pip installation...
pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip is not installed!
    echo Installing pip...
    python -m ensurepip --default-pip
)
echo ✅ pip is ready
echo.

REM Install required packages
echo 📦 Installing required Python packages...
echo This may take 1-2 minutes...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo ❌ Package installation failed
    echo Try running manually: pip install praw requests python-dateutil
    pause
    exit /b 1
)
echo ✅ All packages installed successfully
echo.

REM Create config.py if it doesn't exist
if exist config.py (
    echo ⚠️  config.py already exists - skipping creation
    echo.
) else (
    echo 📝 Creating configuration file...
    copy config_template.py config.py >nul
    echo ✅ Created config.py from template
    echo.
)

REM Check if config.py is filled in
findstr /C:"your_client_id_here" config.py >nul
if not errorlevel 1 (
    echo ⚠️  IMPORTANT: You need to configure config.py!
    echo.
    echo 📖 Next steps:
    echo 1. Open config.py in Notepad or any text editor
    echo 2. Follow SETUP_GUIDE.md to get:
    echo    - Reddit API credentials ^(Step 3^)
    echo    - Gmail App Password ^(Step 4^)
    echo 3. Fill in your information in config.py
    echo 4. Run: python run_agent.py
    echo.
    echo 📚 For detailed instructions, see SETUP_GUIDE.md
    echo.

    REM Offer to open the guide
    set /p OPEN_GUIDE="Would you like to open SETUP_GUIDE.md now? (y/n): "
    if /i "%OPEN_GUIDE%"=="y" (
        start SETUP_GUIDE.md
    )
) else (
    echo ✅ config.py appears to be configured!
    echo.
    echo 🚀 Ready to run! Try: python run_agent.py
    echo.

    REM Offer to run the agent
    set /p RUN_NOW="Would you like to run the agent now? (y/n): "
    if /i "%RUN_NOW%"=="y" (
        echo.
        echo ==================================
        echo 🤖 Running Creedom Agent...
        echo ==================================
        echo.
        python run_agent.py
    )
)

echo.
echo ==================================
echo ✅ Setup Complete!
echo ==================================
echo.
echo 📖 Resources:
echo   - SETUP_GUIDE.md - Complete beginner's guide
echo   - GITHUB_ACTIONS_GUIDE.md - Run in the cloud for free
echo   - README.md - Technical documentation
echo.
echo 🎯 Quick commands:
echo   - Run agent: python run_agent.py
echo   - View stats: python run_agent.py --stats
echo   - Test config: python config.py
echo.
echo 💡 Need help? See SETUP_GUIDE.md or open a GitHub issue
echo.
pause
