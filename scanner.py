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
        batch_df = yf.download(tickers, period="5y", group_by="ticker", threads=True, progress=False, session=session)
    except Exception as e:
        print(f"⚠️ Warning during batch download for {market_key}: {e}")
        batch_df = pd.DataFrame()

    analyzed_stocks = []

    for item in stock_universe:
        symbol = item["ticker"]
        name = item["name"]
        sector = item["sector"]
        is_anchor = item.get("is_anchor", False)

        data = {
            "ticker": symbol, "name": name, "sector": sector, "is_anchor": is_anchor,
            "price": "N/A", "change": 0.0, "p_change": 0.0, "pe_ratio": "N/A", "pb_ratio": "N/A",
            "div_yield": 0.0, "mkt_cap": "N/A", "mkt_cap_raw": 0,
            "ma50": "N/A", "ma200": "N/A", "rsi": "N/A", "vol_surge": False,
            "intrinsic_val": "N/A", "target_price": "N/A", "moat": "Medium",
            "short_debt": "N/A", "long_debt": "N/A",
            "hist_prices": [], "hist_labels": [],
            "daily_prices": [], "daily_dates": [],
            "years": [], "revenue": [], "net_income": [],
            "ocf": [], "fcf": [], "dividends": [], "hist_div_yield": [],
            "assets_cash": "N/A", "assets_ppe": "N/A",
            "signal": "NEUTRAL", "scores": {"short": 0, "mid": 0, "long": 0}
        }

        ticker_obj = yf.Ticker(symbol, session=session)

        # 1. Price extraction & Technical indicators
        try:
            hist = None
            if not batch_df.empty:
                if len(tickers) == 1:
                    hist = batch_df.dropna(how="all")
                elif symbol in batch_df.columns.levels[0]:
                    hist = batch_df[symbol].dropna(how="all")

            if hist is None or hist.empty or len(hist) < 2:
                try: hist = ticker_obj.history(period="5y")
                except Exception: hist = None

            if hist is not None and not hist.empty and len(hist) >= 2:
                last_close = float(hist["Close"].iloc[-1])
                prev_close = float(hist["Close"].iloc[-2])
                data["price"] = last_close
                data["change"] = last_close - prev_close
                data["p_change"] = (data["change"] / (prev_close + 1e-9)) * 100

                data["daily_prices"] = [round(float(p), 2) for p in hist["Close"].tolist()]
                data["daily_dates"] = [d.strftime("%Y-%m-%d") if hasattr(d, 'strftime') else str(d) for d in hist.index]

                one_yr_hist = hist.tail(252)
                sample_step = max(1, len(one_yr_hist) // 20)
                sampled_df = one_yr_hist.iloc[::sample_step]
                data["hist_prices"] = [round(float(p), 2) for p in sampled_df["Close"].tolist()]
                data["hist_labels"] = [d.strftime("%b %y") if hasattr(d, 'strftime') else str(d) for d in sampled_df.index]

                if len(hist) >= 50:
                    ma50_s = hist["Close"].rolling(50).mean()
                    c_ma50 = ma50_s.iloc[-1]
                    data["ma50"] = round(float(c_ma50), 2) if not pd.isna(c_ma50) else "N/A"

                if len(hist) >= 200:
                    ma200_s = hist["Close"].rolling(200).mean()
                    c_ma200 = ma200_s.iloc[-1]
                    data["ma200"] = round(float(c_ma200), 2) if not pd.isna(c_ma200) else "N/A"

                rsi_s = compute_rsi(hist["Close"], 14)
                c_rsi = rsi_s.iloc[-1] if not rsi_s.empty else np.nan
                data["rsi"] = round(float(c_rsi), 1) if not pd.isna(c_rsi) else "N/A"

                c_vol = float(hist["Volume"].iloc[-1]) if "Volume" in hist.columns else 0
                avg_vol_20 = float(hist["Volume"].tail(20).mean()) if "Volume" in hist.columns and len(hist) >= 20 else 1
                data["vol_surge"] = bool(c_vol > 1.5 * avg_vol_20)

                if data["ma50"] != "N/A" and data["ma200"] != "N/A":
                    if data["ma50"] > data["ma200"]:
                        data["signal"] = "BULLISH TREND"
                if data["signal"] == "NEUTRAL" and isinstance(c_rsi, (int, float)):
                    if c_rsi <= 30: data["signal"] = "OVERSOLD"
                    elif c_rsi >= 70: data["signal"] = "OVERBOUGHT"
                if data["vol_surge"]:
                    data["signal"] += " + VOL SURGE"
            else:
                try:
                    fast_p = ticker_obj.fast_info.last_price
                    if fast_p and not pd.isna(fast_p): data["price"] = float(fast_p)
                except Exception: pass
        except Exception as e:
            print(f"⚠️ Note: Price computation skipped for {symbol}: {e}")

        # 2. Metadata & Accurate TTM Dividend Yield
        try:
            time.sleep(0.12)
            info = {}
            try: info = ticker_obj.info or {}
            except Exception: pass

            data["mkt_cap_raw"] = info.get("marketCap", 0) or 0
            data["mkt_cap"] = format_compact(data["mkt_cap_raw"])
            data["pe_ratio"] = round(info.get("trailingPE"), 2) if info.get("trailingPE") else "N/A"
            data["pb_ratio"] = round(info.get("priceToBook"), 2) if info.get("priceToBook") else "N/A"

            # Calculation of TTM Dividend Yield from payout events
            ttm_yield = 0.0
            try:
                divs_series = ticker_obj.dividends
                if divs_series is not None and not divs_series.empty:
                    now_dt = datetime.datetime.now()
                    one_yr_ago = now_dt - datetime.timedelta(days=365)
                    divs_clean = divs_series.copy()
                    if hasattr(divs_clean.index, 'tz') and divs_clean.index.tz is not None:
                        divs_clean.index = divs_clean.index.tz_localize(None)
                    recent_divs = divs_clean[divs_clean.index >= one_yr_ago]
                    ttm_dps = float(recent_divs.sum()) if not recent_divs.empty else 0.0
                    if isinstance(data["price"], (int, float)) and data["price"] > 0 and ttm_dps > 0:
                        ttm_yield = ttm_dps / data["price"]
            except Exception: pass

            if ttm_yield > 0:
                data["div_yield"] = ttm_yield
            else:
                raw_dy = info.get("dividendYield") or info.get("trailingAnnualDividendYield") or 0.0
                raw_dy = float(raw_dy)
                if raw_dy > 1.0: raw_dy = raw_dy / 100.0
                data["div_yield"] = raw_dy

            eps = info.get("trailingEps")
            if eps and eps > 0: data["intrinsic_val"] = f"${eps * 15.5:.2f}"

            target_mean = info.get("targetMeanPrice")
            if target_mean and not pd.isna(target_mean):
                data["target_price"] = f"${float(target_mean):.2f}"
            elif data["intrinsic_val"] != "N/A":
                data["target_price"] = data["intrinsic_val"]
            elif isinstance(data["price"], (int, float)):
                data["target_price"] = f"${data['price'] * 1.15:.2f}"

            if is_anchor or data["mkt_cap_raw"] > 1e10: data["moat"] = "WIDE MOAT"
            elif data["mkt_cap_raw"] > 2e9: data["moat"] = "NARROW MOAT"
            else: data["moat"] = "MODERATE MOAT"

            # 3. 5-Year Financial Statements
            try:
                fin = ticker_obj.financials
                if fin is not None and not fin.empty:
                    cols = list(fin.columns[:5])
                    data["years"] = [d.strftime("%Y") if hasattr(d, 'strftime') else str(d) for d in cols][::-1]
                    rev_row = get_statement_row(fin, ["Total Revenue", "Operating Revenue", "Revenue"])
                    net_row = get_statement_row(fin, ["Net Income", "Net Income Common Stockholders"])
                    data["revenue"] = [format_compact(rev_row[c]) if rev_row is not None and c in rev_row else "N/A" for c in cols][::-1]
                    data["net_income"] = [format_compact(net_row[c]) if net_row is not None and c in net_row else "N/A" for c in cols][::-1]
            except Exception: pass

            # 4. 5-Year Cash Flow
            try:
                cf = ticker_obj.cashflow
                if cf is not None and not cf.empty:
                    cols = list(cf.columns[:5])
                    ocf_row = get_statement_row(cf, ["Operating Cash Flow", "Total Cash From Operating Activities"])
                    capex_row = get_statement_row(cf, ["Capital Expenditure", "Capital Expenditures"])
                    ocf_vals = [ocf_row[c] if ocf_row is not None and c in ocf_row else 0 for c in cols]
                    capex_vals = [abs(capex_row[c]) if capex_row is not None and c in capex_row else 0 for c in cols]
                    fcf_vals = [o - ca for o, ca in zip(ocf_vals, capex_vals)]
                    data["ocf"] = [format_compact(v) for v in ocf_vals][::-1]
                    data["fcf"] = [format_compact(v) for v in fcf_vals][::-1]
            except Exception: pass

            # 5. 5-Year Historical Dividends & Annual Yield %
            try:
                divs = ticker_obj.dividends
                if divs is not None and not divs.empty:
                    if hasattr(divs.index, 'tz') and divs.index.tz is not None:
                        divs.index = divs.index.tz_localize(None)
                    yearly_dps = divs.groupby(divs.index.year).sum()
                    dps_list, yield_list = [], []
                    for yr in data["years"]:
                        try:
                            yr_int = int(yr)
                            if yr_int in yearly_dps.index:
                                val = float(yearly_dps.loc[yr_int])
                                dps_list.append(f"${val:.3f}")
                                if hist is not None and not hist.empty:
                                    yr_hist = hist[hist.index.year == yr_int]
                                    if not yr_hist.empty:
                                        yr_close = float(yr_hist["Close"].iloc[-1])
                                        dps_yield = (val / (yr_close + 1e-9)) * 100
                                        yield_list.append(f"{dps_yield:.2f}%")
                                    else: yield_list.append("N/A")
                                else: yield_list.append("N/A")
                            else:
                                dps_list.append("$0.000")
                                yield_list.append("0.00%")
                        except Exception:
                            dps_list.append("N/A")
                            yield_list.append("N/A")
                    data["dividends"] = dps_list
                    data["hist_div_yield"] = yield_list
                else:
                    data["dividends"] = ["$0.000"] * len(data["years"])
                    data["hist_div_yield"] = ["0.00%"] * len(data["years"])
            except Exception: pass

            # 6. Balance Sheet Breakdown
            try:
                bs = ticker_obj.balance_sheet
                if bs is not None and not bs.empty:
                    c0 = bs.columns[0]
                    st_debt = get_statement_row(bs, ["Current Debt", "Current Debt And Capital Lease Obligation", "Short Term Debt"])
                    lt_debt = get_statement_row(bs, ["Long Term Debt", "Long Term Debt And Capital Lease Obligation"])
                    cash = get_statement_row(bs, ["Cash And Cash Equivalents", "Cash Cash Equivalents And Short Term Investments"])
                    ppe = get_statement_row(bs, ["Gross PPE", "Net PPE", "Properties"])
                    data["short_debt"] = format_compact(st_debt[c0]) if st_debt is not None and c0 in st_debt else "N/A"
                    data["long_debt"] = format_compact(lt_debt[c0]) if lt_debt is not None and c0 in lt_debt else "N/A"
                    data["assets_cash"] = format_compact(cash[c0]) if cash is not None and c0 in cash else "N/A"
                    data["assets_ppe"] = format_compact(ppe[c0]) if ppe is not None and c0 in ppe else "N/A"
            except Exception: pass

        except Exception as e:
            print(f"⚠️ Note: Fundamentals skipped for {symbol}: {e}")

        # Allocation Scoring
        short_score = 0
        if "BULLISH TREND" in data["signal"]: short_score += 30
        if data["vol_surge"]: short_score += 20
        if isinstance(data["rsi"], (int, float)) and data["rsi"] <= 35: short_score += 40
        data["scores"]["short"] = short_score

        mid_score = 0
        if data["signal"] == "BULLISH TREND": mid_score += 40
        if data["moat"] != "MODERATE MOAT": mid_score += 20
        if isinstance(data["rsi"], (int, float)) and 40 <= data["rsi"] <= 65: mid_score += 25
        data["scores"]["mid"] = mid_score

        long_score = (data["div_yield"] * 50) + (25 if data["moat"] == "WIDE MOAT" else 10) + (15 if is_anchor else 0)
        data["scores"]["long"] = long_score

        analyzed_stocks.append(data)

    return analyzed_stocks

def allocate_6_recommendations(stock_data_list):
    """Allocates 2 Short-Term, 2 Mid-Term, and 2 Long-Term opportunities without duplicates."""
    selected = set()
    recs = []

    sorted_short = sorted(stock_data_list, key=lambda x: x["scores"]["short"], reverse=True)
    p_short = [s for s in sorted_short if s["ticker"] not in selected][:2]
    for s in p_short:
        selected.add(s["ticker"])
        recs.append({"bucket": "⚡ SHORT-TERM PLAY", "badge_class": "b-momentum", "data": s})

    sorted_mid = sorted(stock_data_list, key=lambda x: x["scores"]["mid"], reverse=True)
    p_mid = [s for s in sorted_mid if s["ticker"] not in selected][:2]
    for s in p_mid:
        selected.add(s["ticker"])
        recs.append({"bucket": "📈 MID-TERM GROWTH", "badge_class": "b-growth", "data": s})

    sorted_long = sorted(stock_data_list, key=lambda x: x["scores"]["long"], reverse=True)
    p_long = [s for s in sorted_long if s["ticker"] not in selected][:2]
    for s in p_long:
        selected.add(s["ticker"])
        recs.append({"bucket": "🛡️ LONG-TERM COMPOUNDER", "badge_class": "b-compounder", "data": s})

    return recs

def send_telegram_alert(all_markets_recs):
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not bot_token or not chat_id: return

    date_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    msg_lines = [f"🚨 <b>GLOBAL MULTI-MARKET SCANNER ALERTS</b> ({date_str})\n"]

    for m_key, recs in all_markets_recs.items():
        m_name = MARKET_UNIVERSES[m_key]["name"]
        curr = MARKET_UNIVERSES[m_key]["currency"]
        msg_lines.append(f"🌐 <b>{m_name} TOP 6 OPPORTUNITIES:</b>")
        for rec in recs:
            s = rec["data"]
            price_str = f"{curr}{s['price']:.2f}" if isinstance(s['price'], (int, float)) else "N/A"
            msg_lines.append(
                f"• [{rec['bucket']}] <b>{s['ticker']} ({s['name']})</b>\n"
                f"  <b>Price:</b> {price_str} | <b>Signal:</b> <code>{s['signal']}</code>\n"
                f"  <b>RSI:</b> {s['rsi']} | <b>Div Yield:</b> {format_pct(s['div_yield'])}\n"
            )
        msg_lines.append("")

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": "\n".join(msg_lines), "parse_mode": "HTML", "disable_web_page_preview": True}
    try: requests.post(url, json=payload, timeout=10)
    except Exception: pass

def render_html_dashboard(all_market_data, all_market_recs):
    timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    tab_buttons_html = ""
    tab_contents_html = ""
    is_first = True

    for m_key, m_info in MARKET_UNIVERSES.items():
        active_cls = "active" if is_first else ""
        curr = m_info["currency"]
        tab_buttons_html += f'<button class="tab-btn {active_cls}" onclick="switchTab(event, \'{m_key}\')">{m_info["name"]}</button>'

        recs = all_market_recs[m_key]
        stocks = all_market_data[m_key]

        rec_cards_html = ""
        for rec in recs:
            stk = rec["data"]
            price_str = f"{curr}{stk['price']:.2f}" if isinstance(stk['price'], (int, float)) else "N/A"
            div_str = format_pct(stk["div_yield"])
            canvas_id = f"chart_{m_key}_{stk['ticker'].replace('.', '_')}"

            rec_cards_html += f"""
            <div class="rec-card" onclick="openModal('{m_key}', '{stk['ticker']}')">
                <div class="bucket-tag {rec['badge_class']}">{rec['bucket']}</div>
                <div class="rec-header">
                    <div>
                        <div class="rec-ticker">{stk['ticker']}</div>
                        <div class="rec-name">{stk['name']}</div>
                    </div>
                    <div class="rec-price">{price_str}</div>
                </div>
                <div class="rec-stats">
                    <span>Signal: <strong>{stk['signal']}</strong></span>
                    <span>Target: <strong>{stk['target_price']}</strong></span>
                    <span>Div Yield: <strong>{div_str}</strong></span>
                    <span>Moat: <strong>{stk['moat']}</strong></span>
                </div>
                <div class="chart-container">
                    <canvas id="{canvas_id}"></canvas>
                </div>
            </div>
            """

        table_rows_html = ""
        for stk in stocks:
            price_str = f"{curr}{stk['price']:.2f}" if isinstance(stk['price'], (int, float)) else "N/A"
            div_str = format_pct(stk["div_yield"])
            chg = stk["change"]
            p_chg = stk["p_change"]

            if chg > 0: badge = f'<span class="badge pos">+{curr}{chg:.2f} (+{p_chg:.2f}%)</span>'
            elif chg < 0: badge = f'<span class="badge neg">-{curr}{abs(chg):.2f} ({p_chg:.2f}%)</span>'
            else: badge = f'<span class="badge neu">{curr}0.00 (0.00%)</span>'

            table_rows_html += f"""
            <tr onclick="openModal('{m_key}', '{stk['ticker']}')" style="cursor: pointer;">
                <td><strong>{stk['ticker']}</strong></td>
                <td>{stk['name']}<br><small class="text-muted">{stk['sector']}</small></td>
                <td><strong>{price_str}</strong></td>
                <td>{badge}</td>
                <td><span class="signal-tag">{stk['signal']}</span></td>
                <td>{div_str}</td>
                <td>{stk['target_price']}</td>
                <td>{stk['mkt_cap']}</td>
                <td><button class="btn-detail">Deep Dive & Chart</button></td>
            </tr>
            """

        tab_contents_html += f"""
        <div id="tab-{m_key}" class="tab-content {active_cls}">
            <div class="section-title">⭐ Top 6 Recommended Opportunities</div>
            <div class="rec-grid">
                {rec_cards_html}
            </div>

            <div class="section-title">📊 Full {m_info['name']} Universe Scan</div>
            <div class="table-card">
                <table>
                    <thead>
                        <tr>
                            <th>Ticker</th>
                            <th>Company & Sector</th>
                            <th>Price</th>
                            <th>Day Change</th>
                            <th>Signal</th>
                            <th>Div Yield</th>
                            <th>Target Price</th>
                            <th>Market Cap</th>
                            <th>Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        {table_rows_html}
                    </tbody>
                </table>
            </div>
        </div>
        """
        is_first = False

    json_all_data = {m_key: {s["ticker"]: s for s in stocks} for m_key, stocks in all_market_data.items()}
    json_all_recs = {m_key: [r["data"]["ticker"] for r in recs] for m_key, recs in all_market_recs.items()}

    html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Global Stock Scanner Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * { box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 24px; background: #0b1120; color: #f8fafc; }
        .container { max-width: 1380px; margin: 0 auto; }
        .header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #1e293b; padding-bottom: 16px; margin-bottom: 20px; position: relative; z-index: 10; }
        h1 { font-size: 1.8rem; margin: 0; color: #38bdf8; }
        .text-muted { color: #94a3b8; font-size: 0.85rem; }
        
        /* Tabs */
        .tabs { display: flex; gap: 10px; margin-bottom: 24px; border-bottom: 1px solid #1e293b; padding-bottom: 12px; }
        .tab-btn { background: #1e293b; border: 1px solid #334155; color: #cbd5e1; padding: 10px 20px; border-radius: 8px; font-weight: 700; cursor: pointer; transition: all 0.2s; font-size: 0.9rem; }
        .tab-btn:hover { background: #334155; color: #fff; }
        .tab-btn.active { background: #0284c7; color: #fff; border-color: #38bdf8; }
        
        .tab-content { display: none; }
        .tab-content.active { display: block; }

        .btn-trigger { background: #0284c7; color: white; border: none; padding: 10px 18px; border-radius: 8px; font-weight: 700; cursor: pointer; font-size: 0.88rem; transition: background 0.2s; }
        .btn-trigger:hover { background: #0369a1; }
        
        .section-title { font-size: 1.2rem; font-weight: 700; color: #f1f5f9; margin-bottom: 16px; margin-top: 10px; }
        .rec-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 16px; margin-bottom: 36px; }
        .rec-card { background: #1e293b; border-radius: 12px; border: 1px solid #334155; padding: 16px; cursor: pointer; transition: transform 0.2s, border-color 0.2s; }
        .rec-card:hover { transform: translateY(-3px); border-color: #38bdf8; }
        .bucket-tag { display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 0.7rem; font-weight: 800; text-transform: uppercase; margin-bottom: 10px; }
        .b-momentum { background: rgba(250, 204, 21, 0.2); color: #facc15; }
        .b-growth { background: rgba(74, 222, 128, 0.2); color: #4ade80; }
        .b-compounder { background: rgba(192, 132, 252, 0.2); color: #c084fc; }
        .rec-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px; }
        .rec-ticker { font-size: 1.1rem; font-weight: 800; color: #f8fafc; }
        .rec-name { font-size: 0.8rem; color: #94a3b8; }
        .rec-price { font-size: 1.2rem; font-weight: 700; color: #f8fafc; }
        .rec-stats { display: grid; grid-template-columns: 1fr 1fr; gap: 6px; font-size: 0.75rem; color: #cbd5e1; margin-bottom: 12px; background: #0f172a; padding: 8px; border-radius: 6px; }
        .chart-container { height: 90px; width: 100%; }
        
        .table-card { background: #1e293b; border-radius: 12px; border: 1px solid #334155; overflow-x: auto; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3); }
        table { width: 100%; border-collapse: collapse; text-align: left; font-size: 0.88rem; }
        th { background: #0f172a; padding: 14px 16px; color: #cbd5e1; font-weight: 600; border-bottom: 1px solid #334155; text-transform: uppercase; font-size: 0.75rem; }
        td { padding: 12px 16px; border-bottom: 1px solid #334155; vertical-align: middle; }
        tr:hover { background: #26354a; }
        .badge { display: inline-block; padding: 4px 8px; border-radius: 6px; font-size: 0.75rem; font-weight: 600; }
        .pos { background: rgba(34, 197, 94, 0.15); color: #4ade80; }
        .neg { background: rgba(239, 68, 68, 0.15); color: #f87171; }
        .neu { background: rgba(148, 163, 184, 0.15); color: #cbd5e1; }
        .signal-tag { font-weight: 700; font-size: 0.75rem; color: #38bdf8; }
        .btn-detail { background: #0284c7; color: white; border: none; padding: 6px 12px; border-radius: 6px; font-weight: 600; cursor: pointer; font-size: 0.75rem; }
        
        /* Modal Styles */
        .modal { display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.85); justify-content: center; align-items: center; z-index: 1000; padding: 20px; }
        .modal-content { background: #1e293b; max-width: 900px; width: 100%; max-height: 92vh; border-radius: 12px; border: 1px solid #475569; overflow-y: auto; padding: 24px; position: relative; color: #f8fafc; }
        .close-btn { position: absolute; top: 16px; right: 20px; font-size: 1.5rem; color: #94a3b8; cursor: pointer; }
        .form-group { margin-bottom: 14px; text-align: left; }
        .form-group label { display: block; margin-bottom: 4px; font-weight: 600; font-size: 0.85rem; color: #cbd5e1; }
        .form-control { width: 100%; padding: 10px 12px; background: #0f172a; border: 1px solid #334155; border-radius: 6px; color: #f8fafc; font-size: 0.9rem; }
        
        .data-table { width: 100%; margin-top: 12px; border: 1px solid #334155; }
        .data-table th, .data-table td { border: 1px solid #334155; padding: 8px; text-align: center; font-size: 0.8rem; }
        .modal-chart-box { background: #0f172a; padding: 16px; border-radius: 8px; margin: 16px 0; }
        .tf-btn-group { display: flex; gap: 8px; margin-bottom: 12px; justify-content: flex-end; }
        .tf-btn { background: #334155; color: #cbd5e1; border: none; padding: 5px 12px; border-radius: 4px; font-weight: 600; font-size: 0.75rem; cursor: pointer; transition: all 0.2s; }
        .tf-btn.active, .tf-btn:hover { background: #0284c7; color: white; }
        .big-chart-container { height: 260px; width: 100%; position: relative; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div>
                <h1>Global Stock Scanner Dashboard</h1>
                <div class="text-muted">Multi-Market Analysis • Dow 30, Nasdaq 100, S&P 500 & SGX</div>
                <div class="text-muted">Updated: __TIMESTAMP__</div>
            </div>
            <div>
                <button class="btn-trigger" onclick="openTriggerModal()">⚡ Trigger Scan Now</button>
            </div>
        </div>

        <div class="tabs">
            __TAB_BUTTONS__
        </div>

        __TAB_CONTENTS__
    </div>

    <div id="deepDiveModal" class="modal">
        <div class="modal-content">
            <span class="close-btn" onclick="closeModal()">&times;</span>
            <h2 id="m-title" style="margin:0; color:#38bdf8;">Stock Detail</h2>
            <div id="m-subtitle" class="text-muted" style="margin-bottom:12px;">Sector</div>
            
            <div class="modal-chart-box">
                <div class="tf-btn-group">
                    <button class="tf-btn" onclick="updateModalChart('1M')">1M</button>
                    <button class="tf-btn" onclick="updateModalChart('3M')">3M</button>
                    <button class="tf-btn" onclick="updateModalChart('6M')">6M</button>
                    <button class="tf-btn active" onclick="updateModalChart('1Y')">1Y</button>
                    <button class="tf-btn" onclick="updateModalChart('3Y')">3Y</button>
                    <button class="tf-btn" onclick="updateModalChart('5Y')">5Y</button>
                </div>
                <div class="big-chart-container">
                    <canvas id="modalChartCanvas"></canvas>
                </div>
            </div>

            <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px; background:#0f172a; padding:16px; border-radius:8px;">
                <div>Short-Term Debt: <strong id="m-st-debt">N/A</strong></div>
                <div>Long-Term Debt: <strong id="m-lt-debt">N/A</strong></div>
                <div>Cash Assets: <strong id="m-cash">N/A</strong></div>
                <div>PPE / Buildings: <strong id="m-ppe">N/A</strong></div>
                <div>Target Price: <strong id="m-target">N/A</strong></div>
                <div>Economic Moat: <strong id="m-moat">N/A</strong></div>
            </div>

            <h3 style="font-size:1rem; margin-top:16px;">5-Year Financials & Dividend History</h3>
            <table class="data-table">
                <thead>
                    <tr id="m-hist-years"><th>Metric</th></tr>
                </thead>
                <tbody>
                    <tr id="m-hist-rev"><td>Revenue</td></tr>
                    <tr id="m-hist-net"><td>Net Income</td></tr>
                    <tr id="m-hist-ocf"><td>Op. Cash Flow</td></tr>
                    <tr id="m-hist-fcf"><td>Free Cash Flow</td></tr>
                    <tr id="m-hist-div"><td>Div / Share (DPS)</td></tr>
                    <tr id="m-hist-yield"><td>Hist. Div Yield</td></tr>
                </tbody>
            </table>
        </div>
    </div>

    <div id="triggerModal" class="modal">
        <div class="modal-content" style="max-width: 480px;">
            <span class="close-btn" onclick="closeTriggerModal()">&times;</span>
            <h2 style="margin-top:0; color:#38bdf8;">⚡ Trigger Fresh Stock Scan</h2>
            <p class="text-muted" style="margin-bottom:14px;">Enter your GitHub details to start the workflow. Saved locally in browser.</p>
            
            <div class="form-group">
                <label>GitHub Username / Org:</label>
                <input type="text" id="ghUser" class="form-control" placeholder="e.g. john-doe">
            </div>
            <div class="form-group">
                <label>Repository Name:</label>
                <input type="text" id="ghRepo" class="form-control" placeholder="e.g. sgx-stock-scanner">
            </div>
            <div class="form-group">
                <label>GitHub Personal Access Token (PAT):</label>
                <input type="password" id="ghToken" class="form-control" placeholder="github_pat_11A...">
            </div>

            <button id="btnRunAction" class="btn-trigger" style="width:100%; margin-top:8px;" onclick="executeScanTrigger()">
                🚀 Start Scan Now
            </button>
        </div>
    </div>

    <script>
        const allMarketData = __ALL_MARKET_DATA__;
        const allMarketRecs = __ALL_MARKET_RECS__;
        let activeMarket = 'DOW30';
        let modalChartInstance = null;
        let activeModalTicker = null;
        let activeModalMarket = null;

        window.onload = function() {
            if (localStorage.getItem("gh_user")) document.getElementById('ghUser').value = localStorage.getItem("gh_user");
            if (localStorage.getItem("gh_repo")) document.getElementById('ghRepo').value = localStorage.getItem("gh_repo");
            if (localStorage.getItem("gh_token")) document.getElementById('ghToken').value = localStorage.getItem("gh_token");

            renderAllMiniCharts();
        };

        function switchTab(evt, marketKey) {
            activeMarket = marketKey;
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));

            const contentEl = document.getElementById('tab-' + marketKey);
            if (contentEl) contentEl.classList.add('active');
            
            if (evt && evt.currentTarget) evt.currentTarget.classList.add('active');
            renderAllMiniCharts();
        }

        function renderAllMiniCharts() {
            const recTickers = allMarketRecs[activeMarket] || [];
            const marketData = allMarketData[activeMarket] || {};

            recTickers.forEach(ticker => {
                const item = marketData[ticker];
                if (item && item.hist_prices && item.hist_prices.length > 0) {
                    const canvasId = `chart_${activeMarket}_${ticker.replace('.', '_')}`;
                    const ctx = document.getElementById(canvasId);
                    if (ctx && !ctx.getAttribute('data-chart-rendered')) {
                        new Chart(ctx, {
                            type: 'line',
                            data: {
                                labels: item.hist_labels,
                                datasets: [{
                                    data: item.hist_prices,
                                    borderColor: '#38bdf8',
                                    borderWidth: 2,
                                    fill: false,
                                    pointRadius: 0
                                }]
                            },
                            options: {
                                responsive: true,
                                maintainAspectRatio: false,
                                plugins: { legend: { display: false } },
                                scales: { x: { display: false }, y: { display: false } }
                            }
                        });
                        ctx.setAttribute('data-chart-rendered', 'true');
                    }
                }
            });
        }

        function openModal(marketKey, ticker) {
            const item = (allMarketData[marketKey] || {})[ticker];
            if (!item) return;

            activeModalMarket = marketKey;
            activeModalTicker = ticker;

            document.getElementById('m-title').innerText = item.ticker + ' - ' + item.name;
            document.getElementById('m-subtitle').innerText = item.sector + ' | ' + item.mkt_cap + ' Market Cap';
            document.getElementById('m-st-debt').innerText = item.short_debt;
            document.getElementById('m-lt-debt').innerText = item.long_debt;
            document.getElementById('m-cash').innerText = item.assets_cash;
            document.getElementById('m-ppe').innerText = item.assets_ppe;
            document.getElementById('m-target').innerText = item.target_price;
            document.getElementById('m-moat').innerText = item.moat;

            const yearsHeader = '<th>Metric</th>' + (item.years && item.years.length > 0 ? item.years.map(y => `<th>${y}</th>`).join('') : '<th>N/A</th>');
            document.getElementById('m-hist-years').innerHTML = yearsHeader;
            
            document.getElementById('m-hist-rev').innerHTML = '<td>Revenue</td>' + (item.revenue && item.revenue.length > 0 ? item.revenue.map(v => `<td>${v}</td>`).join('') : '<td>N/A</td>');
            document.getElementById('m-hist-net').innerHTML = '<td>Net Income</td>' + (item.net_income && item.net_income.length > 0 ? item.net_income.map(v => `<td>${v}</td>`).join('') : '<td>N/A</td>');
            document.getElementById('m-hist-ocf').innerHTML = '<td>Op Cashflow</td>' + (item.ocf && item.ocf.length > 0 ? item.ocf.map(v => `<td>${v}</td>`).join('') : '<td>N/A</td>');
            document.getElementById('m-hist-fcf').innerHTML = '<td>Free Cashflow</td>' + (item.fcf && item.fcf.length > 0 ? item.fcf.map(v => `<td>${v}</td>`).join('') : '<td>N/A</td>');
            document.getElementById('m-hist-div').innerHTML = '<td>Div / Share (DPS)</td>' + (item.dividends && item.dividends.length > 0 ? item.dividends.map(v => `<td>${v}</td>`).join('') : '<td>N/A</td>');
            document.getElementById('m-hist-yield').innerHTML = '<td>Hist. Div Yield</td>' + (item.hist_div_yield && item.hist_div_yield.length > 0 ? item.hist_div_yield.map(v => `<td>${v}</td>`).join('') : '<td>N/A</td>');

            document.getElementById('deepDiveModal').style.display = 'flex';
            updateModalChart('1Y');
        }

        function updateModalChart(timeframe) {
            if (!activeModalMarket || !activeModalTicker) return;
            const item = (allMarketData[activeModalMarket] || {})[activeModalTicker];
            if (!item) return;

            const dates = item.daily_dates || [];
            const prices = item.daily_prices || [];
            if (dates.length === 0 || prices.length === 0) return;

            const buttons = document.querySelectorAll('.tf-btn');
            buttons.forEach(btn => {
                if (btn.innerText === timeframe) btn.classList.add('active');
                else btn.classList.remove('active');
            });

            let count = dates.length;
            if (timeframe === '1M') count = Math.min(21, dates.length);
            else if (timeframe === '3M') count = Math.min(63, dates.length);
            else if (timeframe === '6M') count = Math.min(126, dates.length);
            else if (timeframe === '1Y') count = Math.min(252, dates.length);
            else if (timeframe === '3Y') count = Math.min(756, dates.length);
            else if (timeframe === '5Y') count = dates.length;

            const filteredDates = dates.slice(-count);
            const filteredPrices = prices.slice(-count);

            const ctx = document.getElementById('modalChartCanvas').getContext('2d');
            if (modalChartInstance) modalChartInstance.destroy();

            modalChartInstance = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: filteredDates,
                    datasets: [{
                        label: 'Price',
                        data: filteredPrices,
                        borderColor: '#38bdf8',
                        backgroundColor: 'rgba(56, 189, 248, 0.1)',
                        borderWidth: 2,
                        fill: true,
                        pointRadius: 1,
                        tension: 0.1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                        x: { grid: { color: '#1e293b' }, ticks: { color: '#94a3b8', maxTicksLimit: 8 } },
                        y: { grid: { color: '#1e293b' }, ticks: { color: '#94a3b8' } }
                    }
                }
            });
        }

        function closeModal() {
            document.getElementById('deepDiveModal').style.display = 'none';
        }

        function openTriggerModal() {
            document.getElementById('triggerModal').style.display = 'flex';
        }

        function closeTriggerModal() {
            document.getElementById('triggerModal').style.display = 'none';
        }

        async function executeScanTrigger() {
            const user = document.getElementById('ghUser').value.trim();
            const repo = document.getElementById('ghRepo').value.trim();
            const token = document.getElementById('ghToken').value.trim();

            if (!user || !repo || !token) {
                alert("Please fill in Username, Repository Name, and Token.");
                return;
            }

            localStorage.setItem("gh_user", user);
            localStorage.setItem("gh_repo", repo);
            localStorage.setItem("gh_token", token);

            const btn = document.getElementById("btnRunAction");
            btn.innerText = "⏳ Triggering...";
            btn.disabled = true;

            try {
                const res = await fetch(`https://api.github.com/repos/${user}/${repo}/actions/workflows/scanner.yml/dispatches`, {
                    method: "POST",
                    headers: {
                        "Accept": "application/vnd.github+json",
                        "Authorization": `Bearer ${token}`,
                        "X-GitHub-Api-Version": "2022-11-28"
                    },
                    body: JSON.stringify({ ref: "main" })
                });

                if (res.status === 204) {
                    alert("🚀 Multi-Market scan triggered successfully!\n\nGitHub Actions will process live data for all markets and update this dashboard in ~2 minutes.");
                    closeTriggerModal();
                } else {
                    const err = await res.text();
                    alert("⚠️ Trigger failed (Status " + res.status + "): " + err);
                }
            } catch (err) {
                alert("⚠️ Error triggering workflow: " + err.message);
            } finally {
                btn.innerText = "🚀 Start Scan Now";
                btn.disabled = false;
            }
        }
    </script>
</body>
</html>"""

    html_doc = html_template.replace("__TIMESTAMP__", timestamp)\
                           .replace("__TAB_BUTTONS__", tab_buttons_html)\
                           .replace("__TAB_CONTENTS__", tab_contents_html)\
                           .replace("__ALL_MARKET_DATA__", json.dumps(json_all_data))\
                           .replace("__ALL_MARKET_RECS__", json.dumps(json_all_recs))

    output_filename = "index.html"
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(html_doc)
    print(f"✅ Dashboard generated successfully: {output_filename}")

def main():
    print("Starting Global Multi-Market Scanner...")
    all_market_data = {}
    all_market_recs = {}

    for m_key, m_info in MARKET_UNIVERSES.items():
        analyzed = analyze_market_universe(m_key, m_info)
        recs = allocate_6_recommendations(analyzed)
        all_market_data[m_key] = analyzed
        all_market_recs[m_key] = recs

    render_html_dashboard(all_market_data, all_market_recs)
    send_telegram_alert(all_market_recs)

if __name__ == "__main__":
    main()
