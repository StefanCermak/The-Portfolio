# Installation Manual for The Portfolio

The Portfolio is a Python-based stock portfolio management application with a graphical user interface. This manual provides detailed installation instructions for Linux, macOS, and Windows systems.

## Prerequisites

- Python 3.13 or higher
- Internet connection for downloading dependencies and fetching stock data
- Display/GUI support (GUI applications require a desktop environment)

## Python 3.13 Installation

### Linux

#### Ubuntu/Debian Systems
```bash
# Update package list
sudo apt update

# Install dependencies
sudo apt install software-properties-common

# Add deadsnakes PPA for Python 3.13
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update

# Install Python 3.13
sudo apt install python3.13 python3.13-venv python3.13-pip

# Install tkinter for GUI support
sudo apt install python3.13-tk

# Verify installation
python3.13 --version
```

#### Fedora/CentOS/RHEL Systems
```bash
# Install Python 3.13 (may need to compile from source or use alternative repositories)
sudo dnf install python3.13 python3.13-pip python3.13-tkinter

# If not available in repositories, compile from source:
sudo dnf groupinstall "Development Tools"
sudo dnf install zlib-devel bzip2-devel openssl-devel ncurses-devel sqlite-devel readline-devel tk-devel gdbm-devel db4-devel libpcap-devel xz-devel expat-devel

# Download and compile Python 3.13
wget https://www.python.org/ftp/python/3.13.0/Python-3.13.0.tgz
tar xzf Python-3.13.0.tgz
cd Python-3.13.0
./configure --enable-optimizations
make -j$(nproc)
sudo make altinstall

# Verify installation
python3.13 --version
```

#### Arch Linux
```bash
# Update system
sudo pacman -Syu

# Install Python 3.13
sudo pacman -S python python-pip tk

# Verify installation
python --version
```

### macOS

#### Using Homebrew (Recommended)
```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python 3.13
brew install python@3.13

# Add to PATH (add to your ~/.zshrc or ~/.bash_profile)
export PATH="/opt/homebrew/bin:$PATH"

# Verify installation
python3.13 --version
```

#### Using Official Python Installer
1. Download Python 3.13 from [python.org](https://www.python.org/downloads/macos/)
2. Run the installer package
3. During installation, ensure "Add Python to PATH" is checked
4. Install Tcl/Tk for GUI support:
   ```bash
   brew install tcl-tk
   ```

### Windows

#### Using Official Python Installer (Recommended)
1. Download Python 3.13 from [python.org](https://www.python.org/downloads/windows/)
2. Run the installer executable
3. **Important:** Check "Add Python to PATH" during installation
4. Choose "Install Now" for default installation
5. Verify installation by opening Command Prompt:
   ```cmd
   python --version
   pip --version
   ```

#### Using Microsoft Store
1. Open Microsoft Store
2. Search for "Python 3.13"
3. Install the official Python package
4. Open Command Prompt to verify:
   ```cmd
   python --version
   ```

## Installing The Portfolio Application

### 1. Download the Application
```bash
# Clone the repository
git clone https://github.com/StefanCermak/The-Portfolio.git
cd The-Portfolio
```

### 2. Create Virtual Environment (Recommended)

#### Linux/macOS
```bash
# Create virtual environment
python3.13 -m venv portfolio_env

# Activate virtual environment
source portfolio_env/bin/activate
```

#### Windows
```cmd
# Create virtual environment
python -m venv portfolio_env

# Activate virtual environment
portfolio_env\Scripts\activate
```

### 3. Install Required Dependencies

Install all required Python packages using pip:

#### Option A: Using requirements.txt (Recommended)
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### Option B: Manual installation
```bash
pip install --upgrade pip
pip install yfinance yahooquery tkcalendar openai duckduckgo-search feedparser requests pdfplumber
```

#### Individual Package Descriptions:
- **yfinance**: Yahoo Finance API for stock data
- **yahooquery**: Alternative Yahoo Finance API
- **tkcalendar**: Date picker widget for the GUI
- **openai**: OpenAI API integration for AI-powered stock analysis
- **duckduckgo-search**: Search functionality for news and information
- **feedparser**: RSS feed parsing for financial news
- **requests**: HTTP library for web requests
- **pdfplumber**: PDF processing for importing account statements

### 4. Verify Installation

Test that all dependencies are correctly installed:

#### Linux/macOS
```bash
python3.13 -c "import tkinter, yfinance, yahooquery, tkcalendar, openai, ddgs, feedparser, requests, pdfplumber; print('All dependencies installed successfully')"
```

#### Windows
```cmd
python -c "import tkinter, yfinance, yahooquery, tkcalendar, openai, ddgs, feedparser, requests, pdfplumber; print('All dependencies installed successfully')"
```

## Running The Portfolio

### Starting the Application

#### Linux/macOS
```bash
# Ensure virtual environment is activated
source portfolio_env/bin/activate

# Run the application
python3.13 main.py
```

#### Windows
```cmd
# Ensure virtual environment is activated
portfolio_env\Scripts\activate

# Run the application
python main.py
```

### First Run Setup

On first run, the application will:
1. Create a SQLite database file (`portfolio.db`)
2. Create a configuration file (`config.json`)
3. Display the main GUI interface

## Configuration

### Basic Configuration

The application creates a `config.json` file with default settings:

```json
{
    "USE_SQLITE": true,
    "USE_MARIADB": false,
    "MARIADB_HOST": "localhost",
    "MARIADB_PORT": 3306,
    "MARIADB_USER": "guest",
    "MARIADB_PASSWORD": "guest",
    "MARIADB_DB": "portfolio",
    "OPEN_AI_API_KEY": ""
}
```

### Optional Features

#### OpenAI Integration (Optional)
For AI-powered stock analysis:
1. Get an API key from [OpenAI Platform](https://platform.openai.com/account/api-keys)
2. Enter the API key in the application's Configuration tab
3. Use the "🧠stock analysis" feature

#### MariaDB Database (Optional)
To use MariaDB instead of SQLite:
1. Install and configure MariaDB server
2. Update the `config.json` file with your MariaDB credentials
3. Set `"USE_MARIADB": true`

## Troubleshooting

### Common Issues

#### GUI Not Displaying (Linux)
If you get "can't connect to display" errors:
```bash
# Install X11 forwarding for SSH
ssh -X username@hostname

# Or install a desktop environment
sudo apt install ubuntu-desktop-minimal
```

#### Missing tkinter
```bash
# Ubuntu/Debian
sudo apt install python3.13-tk

# Fedora/CentOS
sudo dnf install python3.13-tkinter

# macOS with Homebrew
brew install tcl-tk
```

#### SSL Certificate Errors
```bash
# Linux - Update certificates
sudo apt update && sudo apt install ca-certificates

# macOS - Update certificates
brew install ca-certificates
```

#### Permission Errors
```bash
# Ensure proper permissions for the application directory
chmod +x main.py
```

### Performance Notes

- The application caches stock data for 5 minutes to improve performance
- Large portfolios may take longer to load current prices
- Internet connection is required for stock data updates

### Supported File Formats

- PDF account statements (for import functionality)
- SQLite database files
- JSON configuration files

## Getting Help

If you encounter issues:
1. Check the console output for error messages
2. Ensure all dependencies are properly installed
3. Verify your Python version is 3.13 or higher
4. Check that your system supports GUI applications

## License

The Portfolio is free software licensed under the GNU General Public License v3.0.