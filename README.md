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

To install this plugin, you must first add its marketplace, then install the plugin.

### Option 1: Install from GitHub
```bash
# 1. Add the marketplace
claude plugin marketplace add https://github.com/ai-align/finance-plugin

# 2. Install the plugin
claude plugin install finance-plugin@finance-marketplace
```

### Option 2: Install Locally (Development)
If you have cloned the repository:

```bash
# 1. Add the local directory as a marketplace
cd finance-plugin
claude plugin marketplace add ./

# 2. Install the plugin
claude plugin install finance-plugin@finance-marketplace
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

