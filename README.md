# AI Stock Analyzer - Complete Setup Guide

A comprehensive stock analysis tool with web-researched AI recommendations, technical indicators, backtesting, and price alerts.

> **⚠️ IMPORTANT DISCLAIMER**: This is AI-powered software. AI can make mistakes and should not be trusted completely for making financial decisions. Always conduct your own research and consult with qualified financial advisors before making investment choices. Past performance does not guarantee future results.

## 📋 Table of Contents

- [Features](#features)
- [System Requirements](#system-requirements)
- [Step-by-Step Setup Guide](#step-by-step-setup-guide)
- [Getting a Groq API Key](#getting-a-groq-api-key)
- [Running the Application](#running-the-application)
- [How to Use the Dashboard](#how-to-use-the-dashboard)
- [Features Explained](#features-explained)
- [Troubleshooting](#troubleshooting)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

## ✨ Features

- **🌐 Web-Researched Stock Selection**: AI searches current news, earnings, analyst ratings, and market catalysts to find opportunities
- **📊 Technical Analysis**: RSI, MACD, MA20, Volume signals with backtesting performance
- **🤖 AI Recommendations**: Data-driven BUY/SELL/HOLD ratings based on news + technicals
- **📈 Market Benchmarking**: Performance vs S&P 500 with visual charts
- **🚨 Smart Alerts**: Persistent price alerts saved to CSV with automatic checking
- **💬 Personal Analyst Q&A**: Interactive follow-up questions about analysis, changes, or viability
- **🎨 Color-Coded Output**: Visual indicators for positive/negative data, signals, and recommendations
- **📊 Interactive Charts**: Auto-opening performance visualizations with save/delete options
- **🔧 Multiple API Key Methods**: Store in api_key.txt, environment variable, .env file, or enter manually

## 🖥️ System Requirements

### Minimum Requirements
- **Operating System**: Windows 10+, macOS 10.15+, or Linux (Ubuntu 18.04+)
- **Python**: Version 3.8 or higher
- **RAM**: 2GB minimum, 4GB recommended
- **Storage**: 500MB free space
- **Internet**: Required for stock data and AI features

### Recommended Setup
- **Python**: Version 3.10 or higher
- **RAM**: 8GB or more
- **Internet**: Stable broadband connection

## 🚀 Step-by-Step Setup Guide

### Step 1: Install Python

First, you need to install Python on your computer.

#### Windows
1. Go to [python.org](https://python.org)
2. Download the latest Python 3.10+ installer
3. Run the installer
4. **Important**: Check "Add Python to PATH" during installation
5. Verify installation: Open Command Prompt and type `python --version`

#### macOS
1. Install Homebrew (if not already installed):
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```
2. Install Python:
   ```bash
   brew install python
   ```
3. Verify: `python3 --version`

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
python3 --version
```

### Step 2: Download the Project

#### Option A: Clone from GitHub (Recommended)
```bash
git clone https://github.com/yourusername/stock-dashboard.git
cd stock-dashboard
```

#### Option B: Download ZIP
1. Go to the GitHub repository
2. Click "Code" → "Download ZIP"
3. Extract the ZIP file to a folder
4. Open terminal/command prompt in that folder

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install all required packages:
- Flask (web framework)
- yfinance (stock data)
- groq (AI API)
- matplotlib (charts)
- pandas, numpy (data processing)

### Step 4: Set Up Groq API Key

The AI features require a Groq API key. Here's how to get and set it up:

#### 4.1 Get a Groq API Key

1. Go to [Groq Console](https://console.groq.com/)
2. Click "Sign Up" and create an account
3. Verify your email
4. Go to "API Keys" section
5. Click "Create API Key"
6. Copy the generated key (it starts with `gsk_`)

#### 4.2 Set Up the API Key

Choose one of these methods:

**Method A: API Key File (Easiest)**
1. Open the `api_key.txt` file in the project folder
2. Add your API key after `Key =` (e.g., `Key = gsk_your_actual_key_here`)
3. Save the file

**Method B: Environment Variable**
```bash
# Windows Command Prompt
set GROQ_API_KEY=your_api_key_here

# Windows PowerShell
$env:GROQ_API_KEY="your_api_key_here"

# Linux/Mac
export GROQ_API_KEY=your_api_key_here
```

**Method C: .env File**
```bash
# Copy the example file
cp .env.example .env

# Edit the .env file and add your key
# Open .env in a text editor and replace:
GROQ_API_KEY=your_actual_api_key_here
```

**Method D: Let the App Ask**
Just run the app - it will prompt you to enter the API key if none is found.

### Step 5: Run the Setup Script (Optional)

For an interactive setup experience:

```bash
python setup.py
```

This script will:
- Check your Python version
- Help you create a .env file
- Install any missing dependencies
- Guide you through API key setup

## 🎯 Running the Application

### Method 1: Direct Python Execution (Recommended)

```bash
python app.py
```

### Method 2: Using Launcher Scripts

**Windows:**
```bash
run_dashboard.bat
```

**Linux/Mac:**
```bash
./run_dashboard.sh
```

### Method 3: Create Executable (Advanced)

```bash
# Install PyInstaller
pip install pyinstaller

# Create executable
python -m pyinstaller --onefile --windowed --name StockDashboard --add-data "templates;templates" --add-data "static;static" app.py

# Run the executable
./dist/StockDashboard.exe  # Windows
./dist/StockDashboard      # Linux/Mac
```

### What Happens When You Run It

1. The app displays the active AI model being used
2. Checks for triggered price alerts from previous sessions
3. Shows the main menu with three options
4. After analysis, opens chart automatically and prompts to save/delete
5. Enters interactive Q&A mode for follow-up questions
6. Returns to main menu for new analyses or exit

## 📖 How to Use the Analyzer

### 1. Launch the Application

Run the application using one of these methods:

**Windows:**
```cmd
run_dashboard.bat
```

**macOS/Linux:**
```bash
./run_dashboard.sh
```

**Direct Python:**
```bash
python app.py
```

### 2. Main Menu

Choose from three options:
- **1. Analyze specific stocks**: Enter tickers manually for detailed analysis
- **2. Get AI recommendations**: AI researches and selects stocks based on your criteria
- **3. Exit**: Close the application

### 3. Stock Selection

**Specific Stock Analysis:**
- Enter comma-separated ticker symbols (e.g., `AAPL,MSFT,GOOGL`)

**AI Recommendations:**
- Describe what you're looking for (industries, market focus, stock types)
- AI searches web for current opportunities and selects 5 relevant stocks

### 4. Analysis Period

Select timeframe: `1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max`

### 5. View Results

The app displays:
- Technical indicators for each stock
- Backtesting performance
- AI recommendations based on current news + technicals
- Performance chart (opens automatically)

### 6. Set Alerts (Optional)

After analysis, you can set price alerts for BUY/SELL targets, which are saved to `alerts.csv`.

### 7. Interactive Q&A

Enter Q&A mode to ask your personal analyst questions like:
- "What if I bought AAPL at $150?"
- "Is this a good time to invest in tech stocks?"
- "How viable is switching to NVDA instead?"
- "What are the risks of this recommendation?"

Type 'done', 'exit', or 'quit' to return to the main menu.

### 8. Chart Management

Charts open in your default image viewer. Choose to save or delete them.

## 🔍 Features Explained

### Technical Indicators

- **RSI (Relative Strength Index)**: Measures price momentum
  - Above 70: Overbought (SELL signal)
  - Below 30: Oversold (BUY signal)
  - 30-70: Neutral

- **MACD**: Shows relationship between moving averages
  - Bullish when MACD line crosses above signal line
  - Bearish when MACD line crosses below signal line

- **MA20 (20-day Moving Average)**: Trend indicator
  - Price above MA20: Bullish trend
  - Price below MA20: Bearish trend

- **Volume Analysis**: Compares current trading volume to average
  - HIGH: Unusual activity
  - NORMAL: Typical volume
  - LOW: Below average activity

### Professional Backtesting Strategy

The app now includes professional-grade backtesting with multiple strategies:

**Strategies Available:**
- **RSI Strategy**: Buy when RSI < 30 (oversold), sell when RSI > 70 (overbought)
- **MACD Strategy**: Buy when MACD crosses above signal line, sell when it crosses below
- **MA Strategy**: Buy when price > MA20 and MA20 > MA50 (bullish trend)
- **Combined Strategy**: All signals combined for more robust entries

**Professional Features:**
- **Position Sizing**: Configurable % of capital per trade (default 100%)
- **Stop Loss**: Automatic exit at configurable % loss (default 10%)
- **Take Profit**: Automatic exit at configurable % gain (default 20%)
- **Risk Metrics**:
  - Sharpe Ratio: Risk-adjusted return (>1 good, >2 excellent)
  - Max Drawdown: Largest peak-to-trough decline
  - Profit Factor: Ratio of wins to losses (>1.5 good, >2 excellent)
- **Strategy Comparison**: Compare multiple strategies side-by-side
- **vs Buy & Hold**: Outperformance comparison against passive holding

**Results Include:**
- Total return vs buy-and-hold
- Win rate percentage
- Number of trades executed
- Sharpe ratio, max drawdown, profit factor
- Detailed trade log with entry/exit prices and exit reasons (STOP_LOSS, TAKE_PROFIT, SIGNAL, EOD)

### AI Analysis

Powered by Groq's `groq/compound-mini` model with web search capabilities:
- **Stock Selection**: Searches recent news, earnings reports, analyst upgrades, and market catalysts
- **Recommendations**: Combines current market news with technical analysis and backtesting data
- **Output**: Direct BUY/SELL/HOLD ratings with specific reasons, top picks, and market observations
- **Data-Driven**: Ignores hype, focuses on recent developments and fundamentals
- **Interactive Q&A**: Follow-up questions answered by your personal analyst using full analysis context
- **Automatic Fallback**: If the primary model fails, automatically retries with `llama-3.3-70b-versatile`

## 🐛 Troubleshooting

### "Python is not recognized"
- Reinstall Python and check "Add to PATH"
- Try `python3` instead of `python`

### "Module not found" errors
```bash
pip install -r requirements.txt
```

### "API key not found"
- Check your .env file
- Set environment variable: `set GROQ_API_KEY=your_key`
- Or enter it when prompted

### "Port 5000 already in use"
```bash
# Kill process using port 5000
# Windows:
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/Mac:
lsof -ti:5000 | xargs kill -9
```

### Charts not displaying
- Ensure matplotlib is installed
- Check that static folder exists
- Try refreshing the page

### Slow performance
- Check your internet connection
- Some stock data APIs may be slow during market hours
- Consider using shorter time periods for faster loading

### Application won't start
1. Check Python version: `python --version`
2. Verify dependencies: `pip list`
3. Check API key setup
4. Try running: `python -c "import app"`

### Common Windows Issues
- Run Command Prompt as Administrator
- Disable antivirus temporarily (may block the app)
- Check firewall settings

### Common macOS Issues
- Allow app through firewall
- Check System Preferences > Security & Privacy

## 📁 Project Structure

```
stock_dashboard/
├── app.py                 # Main CLI application
├── setup.py              # Interactive setup script
├── build_exe.py          # Executable builder script
├── requirements.txt      # Python dependencies list
├── api_key.txt           # Store your Groq API key here
├── .env.example          # API key template
├── .gitignore           # Git ignore rules
├── README.md            # This comprehensive guide
├── run_dashboard.bat    # Windows launcher
├── run_dashboard.sh     # Linux/Mac launcher
├── alerts.csv           # Saved price alerts (created automatically)
└── chart_*.png          # Generated charts (saved on demand)
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Test thoroughly
5. Commit: `git commit -am 'Add feature'`
6. Push: `git push origin feature-name`
7. Submit a Pull Request

### Development Setup
```bash
git clone https://github.com/yourusername/stock-dashboard.git
cd stock-dashboard
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows
pip install -r requirements.txt
python setup.py
```

## 📄 License

This project is for educational purposes. Please ensure compliance with:
- [Groq API Terms of Service](https://console.groq.com/docs/terms)
- [Yahoo Finance Terms of Service](https://policies.yahoo.com/us/en/yahoo/terms/index.htm)
- Local securities regulations

## 📞 Support

If you encounter issues:
1. Check the [Troubleshooting](#troubleshooting) section
2. Search existing GitHub issues
3. Create a new issue with:
   - Your operating system
   - Python version
   - Error messages
   - Steps to reproduce

## 🙏 Acknowledgments

- [Groq](https://groq.com/) for AI API
- [Yahoo Finance](https://finance.yahoo.com/) for stock data
- [yfinance](https://github.com/ranaroussi/yfinance) for data fetching
- [colorama](https://github.com/tartley/colorama) for colored terminal output

---

**Happy Trading! 📈🚀**

*Last updated: April 18, 2026*