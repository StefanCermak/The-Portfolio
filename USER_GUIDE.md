# The Portfolio - User Guide

Welcome to The Portfolio, your personal stock portfolio management application! This guide will help you get started and make the most of all the features available.

## Table of Contents
- [What is The Portfolio?](#what-is-the-portfolio)
- [Getting Started](#getting-started)
- [Main Interface Overview](#main-interface-overview)
- [Step-by-Step Tutorials](#step-by-step-tutorials)
- [Feature Descriptions](#feature-descriptions)
- [Troubleshooting](#troubleshooting)
- [FAQ](#faq)

---

## What is The Portfolio?

The Portfolio is a desktop application that helps you track and manage your stock investments. Whether you're a beginner investor or an experienced trader, this application provides you with:

- **Real-time stock price tracking** - Stay updated with current market values
- **Portfolio performance analysis** - See how your investments are performing
- **Trade history tracking** - Keep records of all your buy and sell transactions
- **Profit/loss calculations** - Automatic calculation of your gains and losses
- **AI-powered analysis** - Get insights about your stocks (optional feature)
- **Easy data import** - Import your trades from PDF account statements

---

## Getting Started

### System Requirements

- **Operating System**: Windows, macOS, or Linux
- **Python**: Version 3.13 or higher
- **Internet Connection**: Required for stock price updates
- **Display**: Desktop environment with GUI support

### Installation

**Step 1: Install Python**
- Download Python 3.13 from [python.org](https://www.python.org/downloads/)
- During installation, make sure to check "Add Python to PATH"

**Step 2: Download The Portfolio**
- Download the application files to a folder on your computer
- Or clone from: `git clone https://github.com/StefanCermak/The-Portfolio.git`

**Step 3: Install Required Components**
Open a command prompt/terminal in the application folder and run:
```
pip install -r requirements.txt
```
This will install all necessary components (may take a few minutes).

**Step 4: Start the Application**
```
python main.py
```

The application window will open, and you're ready to start!

**Note**: This is a desktop application that requires a graphical user interface (GUI). It won't work in command-line only environments or headless servers.

### First Launch

When you first run The Portfolio:
1. The application will create a database file (`portfolio.db`) in the same folder
2. A configuration file (`config.json`) will be created with default settings
3. The main window will appear with six tabs at the top

---

## Main Interface Overview

The Portfolio has a clean, tabbed interface with six main sections:

### 🔵 Active Trades Tab
Shows your current stock positions that you still own. This is where you'll spend most of your time monitoring your investments.

### 📊 Trade History Tab  
Displays all your completed trades (stocks you've bought and sold). Perfect for reviewing your past investment decisions.

### 📈 Summary Tab
Provides statistics and overview of your portfolio performance, including total profits, losses, and investment summaries.

### ➕ Manual Trade Tab
Where you add new buy or sell transactions to your portfolio. This is your main data entry point.

### ⚙️ Configuration Tab
Settings and preferences, including stock name customization, AI features, and importing data from PDF statements.

### ℹ️ About Tab
Information about the application version and developer.

---

## Step-by-Step Tutorials

### Tutorial 1: Adding Your First Stock Purchase

**What you'll learn**: How to record a stock purchase in your portfolio.

1. **Click on the "Manual Trade" tab** at the top of the window
2. **Enter the stock information**:
   - **Stock Name**: Type a memorable name (e.g., "Apple Inc.")
   - **Ticker**: Enter the stock symbol (e.g., "AAPL")
   - **Date**: Select the purchase date using the calendar
3. **In the "Buy Stock" section**:
   - **Quantity**: Enter how many shares you bought
   - **Invest**: Enter the total amount you paid (including fees)
4. **Click "Buy Stock"** to save the transaction
5. **Switch to "Active Trades" tab** to see your new position

**Tips**: 
- Always use the official stock ticker symbol (you can find these on financial websites)
- Include all costs (commissions, fees) in the "Invest" amount for accurate tracking

### Tutorial 2: Selling Stock (Recording a Sale)

**What you'll learn**: How to record when you sell shares.

1. **Go to "Manual Trade" tab**
2. **Select your stock** from the Stock Name dropdown (it will show stocks you own)
3. **Choose the ticker** from the Ticker dropdown
4. **Set the sale date** using the calendar
5. **In the "Sell Stock" section**:
   - The "Quantity" will show how many shares you own
   - **Earnings**: Enter the total amount you received from the sale
6. **Click "Sell Stock"** to record the transaction
7. **Check "Trade History"** to see the completed trade with profit/loss

### Tutorial 3: Monitoring Your Portfolio Performance

**What you'll learn**: How to track your investment performance.

1. **Visit "Active Trades" tab**:
   - See current value of each stock position
   - View profit/loss for each holding
   - Check the "Profit" column (green=gain, red=loss)
2. **Check "Summary" tab for overall statistics**:
   - Total amount invested
   - Current portfolio value
   - Overall profit/loss percentage
3. **Use the "🧠stock analysis" button** (if AI is configured):
   - Get AI-powered insights about your stocks
   - Receive analysis of potential opportunities and risks

### Tutorial 4: Setting Up Automatic Stock Updates

**What you'll learn**: How to keep stock prices current.

The application automatically updates stock prices every 5 minutes when running. To ensure accurate data:

1. **Keep your internet connection active**
2. **Leave the application running** during market hours
3. **Stock prices update from Yahoo Finance** - this is free and automatic
4. **If a stock price shows "N/A"**, the ticker symbol might be incorrect

### Tutorial 5: Customizing Stock Names

**What you'll learn**: How to use friendly names instead of ticker symbols.

1. **Go to "Configuration" tab**
2. **In the "Ticker Symbol <-> Personal Stock Name Matching" section**:
   - **Select a stock** from the first dropdown
   - **Choose the corresponding ticker** from the second dropdown
   - **Enter your preferred name** in the text box (e.g., "My Apple Investment")
   - **Click "Store Long Name"**
3. **Your custom name will now appear** throughout the application instead of the ticker symbol

---

## Feature Descriptions

### Active Trades Features

| Column | Description |
|--------|-------------|
| **Stock Name** | Your custom name or ticker symbol |
| **++** | Chance/opportunity indicator |
| **--** | Risk indicator |
| **Quantity** | Number of shares you own |
| **Invest** | Total amount you paid for the shares |
| **Now** | Current market value of your position |
| **Profit** | Gain or loss (amount and percentage) |

**Color Coding**:
- 🟢 Green numbers = Profit/Gain
- 🔴 Red numbers = Loss
- ⚪ Blue/Black = Neutral

**Sorting**: Click on any column header to sort by that value.

### Trade History Features

Shows completed trades with:
- **Start Date**: When you first bought the stock
- **End Date**: When you sold all shares
- **Sum Buy**: Total amount invested
- **Sum Sell**: Total amount received from sales
- **Profit**: Net gain/loss from the completed trade
- **Profit %**: Percentage return
- **Profit %(Year)**: Annualized return rate

### Summary Statistics

**Active Trades Statistics**:
- Number of different stocks owned
- Total invested amount
- Current portfolio value
- Overall profit/loss

**Trade History Statistics**:
- Historical trading performance
- Average annual returns
- Total completed trades

### Manual Trade Options

**Buy Stock Section**:
- Record new purchases
- Add to existing positions
- Track investment costs

**Sell Stock Section**:
- Record partial or complete sales
- Automatically calculates remaining shares
- Shows total earnings

**Date Selection**: Use the calendar widget to select accurate transaction dates.

### Configuration Options

**Stock Name Matching**:
- Create readable names for ticker symbols
- Organize your portfolio with personal labels

**PDF Import** (Advanced Feature):
- Import trades from broker account statements
- Automatically parse PDF documents
- Bulk import multiple transactions

**AI Analysis** (Optional):
- Requires OpenAI API key
- Provides stock analysis and insights
- Offers investment recommendations

---

## Troubleshooting

### Common Issues

**Problem**: "Application won't start" or "ModuleNotFoundError"
- **Solution**: 
  - Make sure Python 3.13+ is installed and all requirements are installed (`pip install -r requirements.txt`)
  - If you get import errors, try reinstalling dependencies: `pip install --upgrade -r requirements.txt`
  - Ensure you have a GUI environment (desktop) - the application won't work in command-line only environments

**Problem**: "Stock prices show as 'N/A' or don't update"
- **Solution**: 
  - Check your internet connection
  - Verify the ticker symbol is correct (try looking it up on Yahoo Finance)
  - Some international stocks may not be available

**Problem**: "Can't see the application window"
- **Solution**: 
  - Make sure you have a desktop environment (GUI)
  - On Linux, install: `sudo apt install python3-tk`
  - Try resizing or moving the window (it might be off-screen)

**Problem**: "Database errors or data loss"
- **Solution**:
  - The database file `portfolio.db` stores all your data
  - Make regular backups of this file
  - Don't delete or modify this file manually

**Problem**: "AI analysis not working"
- **Solution**:
  - You need an OpenAI API key
  - Go to Configuration tab and enter your API key
  - This feature is optional and requires a paid OpenAI account

### Performance Tips

- **Close other programs** if the application runs slowly
- **Restart the application** if stock updates stop working
- **Keep the application updated** for the latest features
- **Backup your database file** regularly (portfolio.db)

### Data Safety

**Important**: Your investment data is stored locally in the `portfolio.db` file. This file contains all your trades, profits, and statistics. 

**Backup Recommendations**:
- Copy `portfolio.db` to a safe location regularly
- Consider cloud storage for automatic backups
- Keep copies before major updates or changes

---

## FAQ

**Q: Is my financial data secure?**
A: Yes! All your data is stored locally on your computer. Nothing is sent to external servers except for stock price updates from Yahoo Finance.

**Q: Do I need to pay for stock data?**
A: No, stock prices are provided free through Yahoo Finance. The AI analysis feature requires an OpenAI API key (which has costs).

**Q: Can I use this for international stocks?**
A: Yes, if the stocks are available on Yahoo Finance. Use the appropriate ticker symbol for the exchange.

**Q: What if I make a mistake entering a trade?**
A: Currently, you'll need to manually correct trades by adding offsetting entries. A future version may include edit/delete functionality.

**Q: Can I import data from my broker?**
A: Yes! The application can import from PDF account statements. Go to the Configuration tab and use the PDF import feature.

**Q: How accurate are the profit calculations?**
A: Very accurate, as long as you enter all costs (including fees and commissions) in the "Invest" amount when recording trades.

**Q: Can multiple people use the same installation?**
A: Each installation creates its own database. For multiple users, create separate folders with separate installations.

**Q: What happens if Yahoo Finance is down?**
A: Stock prices will show the last cached values (up to 5 minutes old) or "N/A" if no recent data is available. Your existing data is not affected.

**Q: Is there a mobile version?**
A: Currently, this is a desktop-only application. It requires a computer with Python and GUI support.

---

## Getting Help

If you encounter issues not covered in this guide:

1. **Check the console/terminal** where you started the application for error messages
2. **Verify your Python version** is 3.13 or higher: `python --version`
3. **Ensure all requirements are installed**: `pip install -r requirements.txt`
4. **Try restarting the application** - this fixes many temporary issues
5. **Check your internet connection** for stock price updates

Remember: The Portfolio is designed to be simple and reliable. Most issues are related to setup or internet connectivity rather than the application itself.

---

## License and Credits

The Portfolio is free software licensed under the GNU General Public License v3.0. 

**Developed by**: Stefan Cermak  
**Version**: 0.1.0  
**License**: GPLv3 - You can freely use, modify, and distribute this software.

**Data Sources**:
- Stock prices: Yahoo Finance (free)
- AI analysis: OpenAI (optional, requires API key)

---

*Happy investing! 📈*