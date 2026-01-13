import argparse
import json
import sys
import pandas as pd
import numpy as np

# Hardcoded sector peers for demonstration/fallback
# In a real app, this would be dynamic or a larger database
SECTOR_PEERS = {
    'Technology': ['AAPL', 'MSFT', 'NVDA', 'ORCL', 'ADBE', 'CRM'],
    'Communication Services': ['GOOGL', 'META', 'NFLX', 'DIS'],
    'Consumer Cyclical': ['AMZN', 'TSLA', 'HD', 'NKE', 'MCD'],
    'Financial Services': ['JPM', 'BAC', 'V', 'MA', 'GS'],
    'Healthcare': ['LLY', 'JNJ', 'UNH', 'PFE', 'ABBV']
}

THEMES = {
    'AI & Chips': ['NVDA', 'AMD', 'AVGO', 'SMCI', 'TSM', 'MSFT', 'GOOGL'],
    'Green Energy': ['FSLR', 'ENPH', 'NEE', 'TSLA'],
    'GLP-1 / Obesity': ['LLY', 'NVO']
}

def get_performance_stats(tickers):
    """
    Fetches basic stats for valid tickers.
    Returns: {ticker: {'price': float, 'return_6mo': float, 'sector': str}}
    """
    if not tickers: return {}
    try:
        import yfinance as yf
        stats = {}
        
        # We need sector and history.
        # Batch fetching info is tricky with yfinance as .tickers.info matches aren't guaranteed batch optimized
        # But we can try to be efficient.
        
        # 1. Fetch Price & History (vectorized)
        data = yf.download(tickers, period="6mo", progress=False)
        
        # Check if we got a multi-index dataframe or single
        if isinstance(data.columns, pd.MultiIndex):
             closes = data['Close']
        else:
             closes = pd.DataFrame(data['Close'])
             if len(tickers) == 1:
                 closes.columns = tickers
        
        for ticker in tickers:
            try:
                if ticker not in closes.columns: continue
                
                series = closes[ticker].dropna()
                if series.empty: continue
                
                current_price = series.iloc[-1]
                start_price = series.iloc[0]
                
                # Check for 0 division
                if start_price == 0: ret = 0
                else: ret = (current_price - start_price) / start_price
                
                stats[ticker] = {
                    'price': float(current_price),
                    'return_6mo': float(ret),
                    'sector': 'Unknown' # Default
                }
            except:
                pass

        # 2. Fetch Sector (Likely need individual info calls, slow but necessary for peer logic)
        # We can optimize by only fetching for stocks we own first
        for ticker in tickers:
             if ticker in stats:
                 try:
                     # This is the slow part
                     info = yf.Ticker(ticker).info
                     if 'sector' in info:
                         stats[ticker]['sector'] = info['sector']
                 except:
                     pass
                     
        return stats
    except Exception as e:
        return {}

def analyze_portfolio(portfolio_path):
    try:
        with open(portfolio_path, 'r') as f:
            holdings = json.load(f)
    except Exception as e:
        return {"error": f"Failed to load portfolio: {str(e)}"}
    
    if not holdings:
        return {"error": "Empty portfolio"}

    portfolio_tickers = [h['ticker'] for h in holdings]
    
    # 1. Gather all unique tickers involved (Holdings + Potential Peers + Themes)
    # Actually, let's just fetch holdings first to save time, then fetch peers on demand
    
    # Fetch stats for holdings
    holding_stats = get_performance_stats(portfolio_tickers)
    
    portfolio_data = []
    total_value = 0.0
    total_cost = 0.0
    
    suggestions = []

    # --- Portfolio Analysis Loop ---
    for item in holdings:
        ticker = item['ticker']
        quantity = item['quantity']
        cost_basis = item['cost_basis']
        
        stats = holding_stats.get(ticker, {})
        current_price = stats.get('price', 0)
        
        market_value = quantity * current_price
        
        unrealized_pl = market_value - (quantity * cost_basis)
        unrealized_pl_pct = (unrealized_pl / (quantity * cost_basis)) * 100 if cost_basis > 0 else 0
        
        portfolio_data.append({
            "ticker": ticker,
            "quantity": quantity,
            "cost_basis": cost_basis,
            "current_price": round(current_price, 2),
            "market_value": round(market_value, 2),
            "unrealized_pl": round(unrealized_pl, 2),
            "unrealized_pl_pct": round(unrealized_pl_pct, 2),
            "sector": stats.get('sector', 'Unknown'),
            "return_6mo": stats.get('return_6mo', 0)
        })
        
        total_value += market_value
        total_cost += (quantity * cost_basis)
        
        # Basic Suggestions
        # 1. Stop Loss
        if unrealized_pl_pct < -15:
            suggestions.append({
                "type": "warning",
                "ticker": ticker,
                "message": f"Stop loss warning: {ticker} is down {round(unrealized_pl_pct, 1)}%."
            })
        
        # 2. Profit Taking
        if unrealized_pl_pct > 50:
             suggestions.append({
                "type": "opportunity",
                "ticker": ticker,
                "message": f"Profit taking: {ticker} is up {round(unrealized_pl_pct, 1)}%. Consider trimming."
            })

    # Portfolio Level Metrics
    total_pl = total_value - total_cost
    total_pl_pct = (total_pl / total_cost) * 100 if total_cost > 0 else 0

    # --- Advanced Feature 1: Peer Comparison (Swap Logic) ---
    # Strategy: If a stock is negative P/L AND performing worse than sector peers
    
    # Identify underperformers
    losers = [p for p in portfolio_data if p['unrealized_pl_pct'] < 0]
    
    if losers:
        # Collect potential peers
        peers_to_check = set()
        for loser in losers:
            sector = loser['sector']
            # Find peers in that sector from our hardcoded list
            # In a full app, we'd query a DB
            candidates = SECTOR_PEERS.get(sector, [])
            for c in candidates: 
                if c not in portfolio_tickers: # Don't compare with self
                    peers_to_check.add(c)
        
        if peers_to_check:
             peer_stats = get_performance_stats(list(peers_to_check))
             
             for loser in losers:
                 sector = loser['sector']
                 loser_ret6m = loser['return_6mo']
                 
                 candidates = SECTOR_PEERS.get(sector, [])
                 best_peer = None
                 best_peer_ret = -999
                 
                 for c in candidates:
                     if c in peer_stats:
                         c_ret = peer_stats[c].get('return_6mo', -999)
                         # Simple logic: If peer has > 20% better momentum
                         if c_ret > (loser_ret6m + 0.20): 
                             if c_ret > best_peer_ret:
                                 best_peer = c
                                 best_peer_ret = c_ret
                                 
                 if best_peer:
                     suggestions.append({
                         "type": "swap_opportunity",
                         "ticker": loser['ticker'],
                         "message": f"Swap Opportunity: {loser['ticker']} ({round(loser_ret6m*100,1)}% 6mo) is lagging {best_peer} ({round(best_peer_ret*100,1)}% 6mo) in {sector}."
                     })


    # --- Advanced Feature 2: Market Opportunities (Themes) ---
    for theme, tickers in THEMES.items():
        # Check exposure
        has_exposure = any(t in portfolio_tickers for t in tickers)
        
        if not has_exposure:
            # Find best performer in theme to suggest
            # We need to fetch stats for these if we haven't already
            missing_tickers = [t for t in tickers if t not in holding_stats and t not in portfolio_tickers]
            
            # Fetch batch
            theme_stats = get_performance_stats(missing_tickers)
            
            best_theme_stock = None
            best_ret = -999
            
            for t in tickers:
                # Combine sources
                stats = holding_stats.get(t) or theme_stats.get(t)
                if stats:
                    ret = stats.get('return_6mo', -999)
                    if ret > best_ret:
                        best_ret = ret
                        best_theme_stock = t
            
            if best_theme_stock and best_ret > 0.10: # Only suggest if positive momentum
                 suggestions.append({
                     "type": "new_opportunity",
                     "ticker": best_theme_stock,
                     "message": f"Theme Opportunity: You have no exposure to '{theme}'. Consider {best_theme_stock} which is up {round(best_ret*100, 1)}% in 6mo."
                 })

    # --- Concentration Check ---
    for item in portfolio_data:
         weight = item['market_value'] / total_value if total_value > 0 else 0
         if weight > 0.20:
            suggestions.append({
                "type": "risk",
                "ticker": item['ticker'],
                "message": f"Concentration risk: {item['ticker']} makes up {round(weight*100, 1)}% of portfolio (>20%)."
            })

    return {
        "summary": {
            "total_value": round(total_value, 2),
            "total_cost": round(total_cost, 2),
            "total_pl": round(total_pl, 2),
            "total_pl_pct": round(total_pl_pct, 2)
        },
        "holdings": portfolio_data,
        "suggestions": suggestions
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--portfolio", required=True, help="Path to portfolio JSON file")
    args = parser.parse_args()
    
    result = analyze_portfolio(args.portfolio)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
