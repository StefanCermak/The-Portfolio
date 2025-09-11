# The Portfolio - Stock Portfolio Management Application

The Portfolio is a Python tkinter desktop GUI application for managing stock portfolios. It uses SQLite for data storage and integrates with Yahoo Finance APIs for real-time stock data, OpenAI for analysis, and supports PDF parsing for importing account statements.

**CRITICAL**: Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the information provided here.

## Working Effectively

### Bootstrap and Setup
Run these commands in exact order to set up the development environment:

```bash
# Install system dependencies
sudo apt-get update && sudo apt-get install -y python3-tk

# Install Python dependencies (takes ~60 seconds, NEVER CANCEL)
pip3 install -r requirements.txt
```

**TIMING**: Dependency installation takes approximately 60 seconds. Set timeout to 120+ seconds and NEVER CANCEL.

### Requirements
The application requires these Python packages (already defined in requirements.txt):
- `yfinance` - Yahoo Finance API for stock data
- `yahooquery` - Additional Yahoo Finance functionality  
- `tkcalendar` - Calendar widget for tkinter
- `requests` - HTTP requests
- `pdfplumber` - PDF parsing for account statements
- `openai` - OpenAI API integration for stock analysis
- `ddgs` - DuckDuckGo search API
- `feedparser` - RSS/XML feed parsing

### Running the Application

```bash
# Run the main application
python3 main.py
```

**IMPORTANT**: The application requires a GUI display. In headless environments:
```bash
# Install and start virtual display
sudo apt-get install -y xvfb
Xvfb :99 -screen 0 1024x768x24 &
DISPLAY=:99 python3 main.py
```

**TIMING**: Application startup takes ~1.3 seconds. The GUI will launch and create `portfolio.db` SQLite database on first run.

### Core Components

#### Entry Point
- `main.py` - Application entry point that imports and runs BrokerApp

#### GUI and Application Logic  
- `Gui.py` - Main tkinter GUI class (BrokerApp) with all interface components
- `globals.py` - Global constants, configuration management, app metadata

#### Database Layer
- `Db.py` - Database wrapper class (singleton pattern) for abstraction
- `Db_Sqlite.py` - SQLite implementation with all database operations
- Database file: `portfolio.db` (auto-created, SQLite format)

#### Data Integration
- `stockdata.py` - Yahoo Finance API integration for stock prices and currency conversion
- `import_account_statements.py` - PDF parsing for importing brokerage statements
- `daily_report.py` - OpenAI and DuckDuckGo integration for market analysis

#### Utilities
- `tools.py` - Utility functions including caching decorators

## Validation and Testing

### Manual Validation Scenarios
After making changes, ALWAYS test these complete scenarios:

1. **Basic Application Start**:
   ```bash
   # Test app launches without errors
   DISPLAY=:99 timeout 10 python3 main.py &
   sleep 3
   pkill -f "python3 main.py"
   ```

2. **Database Functionality**:
   ```bash
   python3 -c "
   import Db
   db = Db.Db()
   print('Database initialized:', db.get_stock_set())
   db.close()
   "
   ```

3. **Core Module Loading**:
   ```bash
   python3 -c "
   import globals, Db, stockdata, tools
   print('All core modules loaded successfully')
   "
   ```

4. **Stock Data API** (network dependent):
   ```bash
   python3 -c "
   from stockdata import get_stock_price
   result = get_stock_price('AAPL')
   print('Stock API test:', result)
   "
   ```

### Component Testing
- **NO UNIT TESTS EXIST** - This project has no test infrastructure
- Validation must be done through manual testing and running the application
- Always test GUI functionality by launching the full application

### Code Quality
- **NO LINTING CONFIGURED** - No flake8, pylint, or other code quality tools are set up
- **NO CI/CD** - No GitHub Actions or automated testing workflows exist
- Manual code review and testing is the only validation method

## Database and Configuration

### Database Setup
- Uses SQLite by default via `portfolio.db` file (auto-created)
- Configuration stored in `config.json` (auto-created with defaults)
- Database schema is managed automatically by `Db_Sqlite.py`

### Configuration Options
The app supports these configuration options in `config.json`:
- `USE_SQLITE`: true (default)
- `USE_MARIADB`: false (MariaDB support exists but not commonly used)
- `OPEN_AI_API_KEY`: "" (required for AI analysis features)
- MariaDB connection settings (if enabled)

### Data Storage
- `/portfolio.db` - SQLite database (ignored in .gitignore)
- `/account_statements/` - Directory for imported PDF statements (ignored)
- `/*.json` - Config and cache files (ignored)
- `*.log` - Application logs (ignored)

## Common Issues and Troubleshooting

### Missing Dependencies
If you get `ModuleNotFoundError`, ensure all requirements are installed:
```bash
pip3 install -r requirements.txt
```

### GUI Display Issues
In headless environments, you'll get `TclError: no display`. Use virtual display:
```bash
sudo apt-get install -y xvfb
Xvfb :99 -screen 0 1024x768x24 &
export DISPLAY=:99
```

### Stock Data API Failures
Stock price fetching may fail due to:
- Network connectivity issues
- Yahoo Finance API rate limiting
- Invalid ticker symbols
The app handles these gracefully, returning None values.

### Database File Permissions
Ensure the current directory is writable for SQLite database creation.

## Development Guidelines

### Making Changes
- Test changes by running the full application with GUI
- Always validate database operations don't corrupt existing data  
- Test stock data integration if modifying `stockdata.py`
- The application is single-threaded GUI app - avoid blocking operations in main thread

### Code Structure
- GUI code is concentrated in `Gui.py` (large file ~2000 lines)
- Database operations use singleton pattern via `Db.Db()`
- Stock data uses caching decorators from `tools.py`
- Configuration loaded once on startup via `globals.py`

### File Organization
```
.
├── main.py              # Entry point
├── Gui.py               # Main GUI application
├── Db.py                # Database abstraction layer  
├── Db_Sqlite.py         # SQLite implementation
├── globals.py           # Configuration and constants
├── stockdata.py         # Yahoo Finance integration
├── import_account_statements.py  # PDF parsing
├── daily_report.py      # AI/search integration
├── tools.py             # Utility functions
├── requirements.txt     # Python dependencies
├── .gitignore          # Git ignore patterns
└── portfolio.db        # SQLite database (auto-created)
```

## Network Dependencies
The application requires internet connectivity for:
- Yahoo Finance stock price data (`yfinance`, `yahooquery`)
- OpenAI API for analysis features (requires API key)
- DuckDuckGo search integration
- RSS feed parsing for market news

The app will function offline but with limited functionality (local database operations only).

## Example: Complete Setup and Validation Workflow

Here's a complete example of how to set up and validate the environment:

```bash
# 1. Install system dependencies
sudo apt-get update && sudo apt-get install -y python3-tk xvfb

# 2. Install Python dependencies (NEVER CANCEL - takes ~60 seconds)
pip3 install -r requirements.txt  # Set timeout to 120+ seconds

# 3. Start virtual display for headless environments
Xvfb :99 -screen 0 1024x768x24 &
export DISPLAY=:99

# 4. Validate core functionality
python3 -c "
import globals, Db, stockdata, tools
print('✓ Core modules loaded')
db = Db.Db()
print('✓ Database initialized')
db.close()
"

# 5. Test GUI application
python3 -c "
from Gui import BrokerApp
app = BrokerApp()
print('✓ GUI application ready')
"

# 6. Run full application (for testing)
# python3 main.py  # Use this for actual usage
```

**Expected Results:**
- System setup: ~30 seconds
- Dependency installation: ~60 seconds (fresh) or ~1-2 seconds (cached)
- Database creation: Automatic on first run
- GUI initialization: ~1.3 seconds
- Total fresh setup time: ~90-120 seconds