import os
import time
import datetime
import json
import pandas as pd
import numpy as np
import requests
import yfinance as yf

# Configure custom browser session to prevent Yahoo rate-limiting
session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, Gecko) Chrome/122.0.0.0 Safari/537.36"
})

# Market Universes Definition
MARKET_UNIVERSES = {
    "DOW30": {
        "name": "Dow Jones 30",
        "currency": "$",
        "tickers": [
            {"ticker": "AAPL", "name": "Apple Inc.", "sector": "Technology", "is_anchor": True},
            {"ticker": "AMGN", "name": "Amgen Inc.", "sector": "Healthcare", "is_anchor": False},
            {"ticker": "AMZN", "name": "Amazon.com Inc.", "sector": "Consumer Discretionary", "is_anchor": True},
            {"ticker": "AXP", "name": "American Express", "sector": "Financial Services", "is_anchor": False},
            {"ticker": "BA", "name": "Boeing Co.", "sector": "Aerospace & Defense", "is_anchor": False},
            {"ticker": "CAT", "name": "Caterpillar Inc.", "sector": "Industrials", "is_anchor": False},
            {"ticker": "CRM", "name": "Salesforce Inc.", "sector": "Technology", "is_anchor": False},
            {"ticker": "CSCO", "name": "Cisco Systems", "sector": "Technology", "is_anchor": False},
            {"ticker": "CVX", "name": "Chevron Corp.", "sector": "Energy", "is_anchor": True},
            {"ticker": "DIS", "name": "Walt Disney Co.", "sector": "Communication", "is_anchor": False},
            {"ticker": "GS", "name": "Goldman Sachs", "sector": "Financial Services", "is_anchor": True},
            {"ticker": "HD", "name": "Home Depot", "sector": "Consumer Discretionary", "is_anchor": True},
            {"ticker": "HON", "name": "Honeywell Int.", "sector": "Industrials", "is_anchor": False},
            {"ticker": "IBM", "name": "IBM Corp.", "sector": "Technology", "is_anchor": False},
            {"ticker": "JNJ", "name": "Johnson & Johnson", "sector": "Healthcare", "is_anchor": True},
            {"ticker": "JPM", "name": "JPMorgan Chase", "sector": "Financial Services", "is_anchor": True},
            {"ticker": "KO", "name": "Coca-Cola Co.", "sector": "Consumer Staples", "is_anchor": True},
            {"ticker": "MCD", "name": "McDonald's Corp.", "sector": "Consumer Discretionary", "is_anchor": True},
            {"ticker": "MMM", "name": "3M Co.", "sector": "Industrials", "is_anchor": False},
            {"ticker": "MRK", "name": "Merck & Co.", "sector": "Healthcare", "is_anchor": False},
            {"ticker": "MSFT", "name": "Microsoft Corp.", "sector": "Technology", "is_anchor": True},
            {"ticker": "NKE", "name": "Nike Inc.", "sector": "Consumer Discretionary", "is_anchor": False},
            {"ticker": "NVDA", "name": "NVIDIA Corp.", "sector": "Technology", "is_anchor": True},
            {"ticker": "PG", "name": "Procter & Gamble", "sector": "Consumer Staples", "is_anchor": True},
            {"ticker": "SHW", "name": "Sherwin-Williams", "sector": "Basic Materials", "is_anchor": False},
            {"ticker": "TRV", "name": "Travelers Companies", "sector": "Financial Services", "is_anchor": False},
            {"ticker": "UNH", "name": "UnitedHealth Group", "sector": "Healthcare", "is_anchor": True},
            {"ticker": "V", "name": "Visa Inc.", "sector": "Financial Services", "is_anchor": True},
            {"ticker": "WMT", "name": "Walmart Inc.", "sector": "Consumer Staples", "is_anchor": True},
            {"ticker": "XOM", "name": "Exxon Mobil Corp.", "sector": "Energy", "is_anchor": True}
        ]
    },
    "NASDAQ100": {
        "name": "Nasdaq 100 Leaders",
        "currency": "$",
        "tickers": [
            {"ticker": "AAPL", "name": "Apple Inc.", "sector": "Technology", "is_anchor": True},
            {"ticker": "MSFT", "name": "Microsoft Corp.", "sector": "Technology", "is_anchor": True},
            {"ticker": "NVDA", "name": "NVIDIA Corp.", "sector": "Technology", "is_anchor": True},
            {"ticker": "AMZN", "name": "Amazon.com Inc.", "sector": "Consumer Discretionary", "is_anchor": True},
            {"ticker": "GOOGL", "name": "Alphabet Inc.", "sector": "Communication Services", "is_anchor": True},
            {"ticker": "META", "name": "Meta Platforms", "sector": "Communication Services", "is_anchor": True},
            {"ticker": "TSLA", "name": "Tesla Inc.", "sector": "Consumer Discretionary", "is_anchor": False},
            {"ticker": "AVGO", "name": "Broadcom Inc.", "sector": "Technology", "is_anchor": True},
            {"ticker": "COST", "name": "Costco Wholesale", "sector": "Consumer Staples", "is_anchor": True},
            {"ticker": "ASML", "name": "ASML Holding", "sector": "Technology", "is_anchor": True},
            {"ticker": "AMD", "name": "Advanced Micro Devices", "sector": "Technology", "is_anchor": False},
            {"ticker": "TMUS", "name": "T-Mobile US", "sector": "Telecommunications", "is_anchor": False},
            {"ticker": "PEP", "name": "PepsiCo Inc.", "sector": "Consumer Staples", "is_anchor": True},
            {"ticker": "CSCO", "name": "Cisco Systems", "sector": "Technology", "is_anchor": False},
            {"ticker": "LIN", "name": "Linde plc", "sector": "Basic Materials", "is_anchor": False},
            {"ticker": "ADBE", "name": "Adobe Inc.", "sector": "Technology", "is_anchor": False},
            {"ticker": "NFLX", "name": "Netflix Inc.", "sector": "Communication Services", "is_anchor": False},
            {"ticker": "TXN", "name": "Texas Instruments", "sector": "Technology", "is_anchor": False},
            {"ticker": "QCOM", "name": "QUALCOMM Inc.", "sector": "Technology", "is_anchor": False},
            {"ticker": "AMAT", "name": "Applied Materials", "sector": "Technology", "is_anchor": False},
            {"ticker": "INTU", "name": "Intuit Inc.", "sector": "Technology", "is_anchor": False},
            {"ticker": "BKNG", "name": "Booking Holdings", "sector": "Consumer Discretionary", "is_anchor": False},
            {"ticker": "VRTX", "name": "Vertex Pharma", "sector": "Healthcare", "is_anchor": False},
            {"ticker": "REGN", "name": "Regeneron Pharma", "sector": "Healthcare", "is_anchor": False},
            {"ticker": "PANW", "name": "Palo Alto Networks", "sector": "Technology", "is_anchor": False},
            {"ticker": "MU", "name": "Micron Technology", "sector": "Technology", "is_anchor": False},
            {"ticker": "LRCX", "name": "Lam Research", "sector": "Technology", "is_anchor": False},
            {"ticker": "ADI", "name": "Analog Devices", "sector": "Technology", "is_anchor": False},
            {"ticker": "SNPS", "name": "Synopsys Inc.", "sector": "Technology", "is_anchor": False},
            {"ticker": "KLAC", "name": "KLA Corp.", "sector": "Technology", "is_anchor": False}
        ]
    },
    "SP500": {
        "name": "S&P 500 Top Leaders",
        "currency": "$",
        "tickers": [
            {"ticker": "AAPL", "name": "Apple Inc.", "sector": "Technology", "is_anchor": True},
            {"ticker": "MSFT", "name": "Microsoft Corp.", "sector": "Technology", "is_anchor": True},
            {"ticker": "NVDA", "name": "NVIDIA Corp.", "sector": "Technology", "is_anchor": True},
            {"ticker": "AMZN", "name": "Amazon.com Inc.", "sector": "Consumer Discretionary", "is_anchor": True},
            {"ticker": "GOOGL", "name": "Alphabet Inc.", "sector": "Communication Services", "is_anchor": True},
            {"ticker": "META", "name": "Meta Platforms", "sector": "Communication Services", "is_anchor": True},
            {"ticker": "BRK-B", "name": "Berkshire Hathaway", "sector": "Financial Services", "is_anchor": True},
            {"ticker": "LLY", "name": "Eli Lilly & Co.", "sector": "Healthcare", "is_anchor": True},
            {"ticker": "JPM", "name": "JPMorgan Chase", "sector": "Financial Services", "is_anchor": True},
            {"ticker": "AVGO", "name": "Broadcom Inc.", "sector": "Technology", "is_anchor": True},
            {"ticker": "WMT", "name": "Walmart Inc.", "sector": "Consumer Staples", "is_anchor": True},
            {"ticker": "UNH", "name": "UnitedHealth Group", "sector": "Healthcare", "is_anchor": True},
            {"ticker": "V", "name": "Visa Inc.", "sector": "Financial Services", "is_anchor": True},
            {"ticker": "PG", "name": "Procter & Gamble", "sector": "Consumer Staples", "is_anchor": True},
            {"ticker": "MA", "name": "Mastercard Inc.", "sector": "Financial Services", "is_anchor": True},
            {"ticker": "XOM", "name": "Exxon Mobil Corp.", "sector": "Energy", "is_anchor": True},
            {"ticker": "HD", "name": "Home Depot", "sector": "Consumer Discretionary", "is_anchor": True},
            {"ticker": "JNJ", "name": "Johnson & Johnson", "sector": "Healthcare", "is_anchor": True},
            {"ticker": "COST", "name": "Costco Wholesale", "sector": "Consumer Staples", "is_anchor": True},
            {"ticker": "ORCL", "name": "Oracle Corp.", "sector": "Technology", "is_anchor": False},
            {"ticker": "ABBV", "name": "AbbVie Inc.", "sector": "Healthcare", "is_anchor": False},
            {"ticker": "BAC", "name": "Bank of America", "sector": "Financial Services", "is_anchor": False},
            {"ticker": "CVX", "name": "Chevron Corp.", "sector": "Energy", "is_anchor": True},
            {"ticker": "KO", "name": "Coca-Cola Co.", "sector": "Consumer Staples", "is_anchor": True},
            {"ticker": "MRK", "name": "Merck & Co.", "sector": "Healthcare", "is_anchor": False},
            {"ticker": "NFLX", "name": "Netflix Inc.", "sector": "Communication Services", "is_anchor": False},
            {"ticker": "CRM", "name": "Salesforce Inc.", "sector": "Technology", "is_anchor": False},
            {"ticker": "AMD", "name": "Advanced Micro Devices", "sector": "Technology", "is_anchor": False},
            {"ticker": "PEP", "name": "PepsiCo Inc.", "sector": "Consumer Staples", "is_anchor": True},
            {"ticker": "TMO", "name": "Thermo Fisher Scientific", "sector": "Healthcare", "is_anchor": False}
        ]
    },
    "SGX": {
        "name": "SGX Mainboard",
        "currency": "S$",
        "tickers": [
            {"ticker": "D05.SI", "name": "DBS Group Holdings", "sector": "Banking", "is_anchor": True},
            {"ticker": "O39.SI", "name": "OCBC Bank", "sector": "Banking", "is_anchor": True},
            {"ticker": "U11.SI", "name": "UOB", "sector": "Banking", "is_anchor": True},
            {"ticker": "Z74.SI", "name": "Singtel", "sector": "Telecommunications", "is_anchor": True},
            {"ticker": "S68.SI", "name": "Singapore Exchange", "sector": "Financial Services", "is_anchor": True},
            {"ticker": "C6L.SI", "name": "Singapore Airlines", "sector": "Aviation", "is_anchor": False},
            {"ticker": "BN4.SI", "name": "Keppel Ltd", "sector": "Conglomerate", "is_anchor": False},
            {"ticker": "F34.SI", "name": "Wilmar International", "sector": "Consumer Goods", "is_anchor": False},
            {"ticker": "BS6.SI", "name": "Yangzijiang Shipbuilding", "sector": "Industrials", "is_anchor": False},
            {"ticker": "S63.SI", "name": "ST Engineering", "sector": "Industrials", "is_anchor": False},
            {"ticker": "G13.SI", "name": "Genting Singapore", "sector": "Consumer Services", "is_anchor": False},
            {"ticker": "Y92.SI", "name": "Thai Beverage", "sector": "Consumer Goods", "is_anchor": False},
            {"ticker": "9CI.SI", "name": "CapitaLand Investment", "sector": "Real Estate", "is_anchor": False},
            {"ticker": "C38U.SI", "name": "CapitaLand Int Comm Trust", "sector": "REIT", "is_anchor": True},
            {"ticker": "A17U.SI", "name": "CapitaLand Ascendas REIT", "sector": "REIT", "is_anchor": True},
            {"ticker": "M44U.SI", "name": "Mapletree Logistics Trust", "sector": "REIT", "is_anchor": False},
            {"ticker": "ME8U.SI", "name": "Mapletree Industrial Trust", "sector": "REIT", "is_anchor": False},
            {"ticker": "N2IU.SI", "name": "Mapletree Pan Asia Comm Trust", "sector": "REIT", "is_anchor": False},
            {"ticker": "J69U.SI", "name": "Frasers Centrepoint Trust", "sector": "REIT", "is_anchor": False},
            {"ticker": "BUOU.SI", "name": "Frasers Logistics & Comm Trust", "sector": "REIT", "is_anchor": False},
            {"ticker": "OV8.SI", "name": "Sheng Siong Group", "sector": "Consumer Staples", "is_anchor": False},
            {"ticker": "AIY.SI", "name": "iFAST Corporation", "sector": "Fintech / Wealth", "is_anchor": False},
            {"ticker": "MZH.SI", "name": "Nanofilm Technologies", "sector": "Technology", "is_anchor": False},
            {"ticker": "BSL.SI", "name": "Raffles Medical Group", "sector": "Healthcare", "is_anchor": False}
        ]
    }
}

def compute_rsi(series, period=14):
    if len(series) < period:
        return pd.Series([np.nan] * len(series), index=series.index)
    delta = series.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    avg_gain = gain.rolling(window=period, min_periods=period).mean()
    avg_loss = loss.rolling(window=period, min_periods=period).mean()
    rs = avg_gain / (avg_loss + 1e-9)
    return 100 - (100 / (1 + rs))

def format_pct(val):
    if val is None or pd.isna(val) or val == "N/A": return "N/A"
    try:
        num = float(val)
        return f"{num * 100:.2f}%" if abs(num) < 1.0 else f"{num:.2f}%"
    except: return "N/A"

def format_compact(val):
    if val is None or pd.isna(val) or val == "N/A": return "N/A"
    try:
        num = float(val)
        if abs(num) >= 1e9: return f"${num/1e9:.2f}B"
        if abs(num) >= 1e6: return f"${num/1e6:.2f}M"
        return f"${num:,.0f}"
    except: return "N/A"

def get_statement_row(df, possible_names):
    if df is None or not isinstance(df, pd.DataFrame) or df.empty: return None
    for name in possible_names:
        for idx in df.index:
            if str(idx).strip().lower() == name.strip().lower():
                return df.loc[idx]
    return None

def analyze_market_universe(market_key, market_info):
    stock_universe = market_info["tickers"]
    tickers = [item["ticker"] for item in stock_universe]
    print(f"⚡ Downloading 5-year price history for {market_info['name']} ({len(tickers)} tickers)...")

    try:
        batch_df
