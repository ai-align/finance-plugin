# Finance Plugin

A specialized Claude Code plugin designed for financial stock analysis and market insights.

## Features

### Stock Analyzer Skill
The plugin includes a **Stock Analyzer** skill that enables Claude to:
- **Technical Analysis**: Interpret indicators like RSI, MACD, and Moving Averages.
- **Fundamental Analysis**: Evaluate company financial health (balance sheets, income statements).
- **Market Trends**: Analyze sector performance and broader market movements.
- **Peer Comparison**: Compare stocks against industry competitors.

## Installation

You can install this plugin directly from the GitHub repository using the Claude Code CLI.

### Option 1: Install via Git URL which created by Claude
```bash
claude plugin install https://github.com/ai-align/finance-plugin
```

### Option 2: Clone and Install Locally
If you prefer to clone the repository first:

```bash
# Clone the repository
git clone https://github.com/ai-align/finance-plugin.git

# Navigate to the directory
cd finance-plugin

# Install the plugin from the current directory
claude plugin install .
```


## Requirements

To use the Stock Analyzer script reliably, we recommend installing the python dependencies:

```bash
pip install -r skills/stock-analyzer/requirements.txt
```

## Usage

Once installed, the **Stock Analyzer** skill allows you to ask Claude financial questions such as:
- "Analyze the recent performance of AAPL"
- "Is TSLA a good buy right now based on technicals?"
- "Compare the financials of Coke vs Pepsi"

