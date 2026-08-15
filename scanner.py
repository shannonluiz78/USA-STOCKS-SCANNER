import os
import time
import datetime
import json
import pandas as pd
import numpy as np
import requests
import yfinance as yf

# Configure custom headers for HTTP requests
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, Gecko) Chrome/122.0.0.0 Safari/537.36"
}

# Define Market Universes
MARKET_UNIVERSES = {
    "DOW30": {
        "name": "Dow Jones 30",
        "currency": "$",
        "tickers": [
            "AAPL", "AMGN", "AMZN", "AXP", "BA", "CAT", "CRM", "CSCO", "CVX", "DIS",
            "GS", "HD", "HON", "IBM", "JNJ", "JPM", "KO", "MCD", "MMM", "MRK",
            "MSFT", "NKE", "NVDA", "PG", "SHW", "TRV", "UNH", "V", "WMT", "XOM"
        ]
    },
    "NASDAQ100": {
        "name": "Nasdaq 100",
        "currency": "$",
        "tickers": [
            "AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "TSLA", "AVGO", "COST", "ASML",
            "AMD", "TMUS", "PEP", "CSCO", "LIN", "ADBE", "NFLX", "TXN", "QCOM", "AMAT",
            "AMGN", "ISRG", "HON", "INTU", "BKNG", "CMCSA", "VRTX", "REGN", "ADP", "PANW",
            "MDLZ", "MU", "LRCX", "ADI", "SNPS", "KLAC", "CDNS", "PYPL", "ORLY", "CSX",
            "MAR", "CRWD", "ABNB", "CTAS", "MNST", "PDD", "AEP", "MELI", "NTES", "MRVL"
        ]
    },
    "SP500": {
        "name": "S&P 500 Top Leaders",
        "currency": "$",
        "tickers": [
            "AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "BRK-B", "LLY", "JPM", "AVGO",
            "TSLA", "WMT", "UNH", "V", "PG", "MA", "XOM", "HD", "JNJ", "COST",
            "ORCL", "ABBV", "BAC", "CVX", "KO", "MRK", "NFLX", "CRM", "AMD", "PEP",
            "TMO", "LIN", "CSCO", "ADBE", "ACN", "MCD", "WFC", "ABT", "PM", "DIS",
            "TXN", "QCOM", "GE", "VZ", "CAT", "INTU", "INTC", "AMAT", "BKNG", "LOW"
        ]
    },
    "SGX": {
        "name": "SGX Mainboard",
        "currency": "S$",
        "tickers": [
            "D05.SI", "O39.SI", "U11.SI", "Z74.SI", "S68.SI", "C6L.SI", "BN4.SI", "F34.SI",
            "A17U.SI", "C38U.SI", "N2IU.SI", "ME8U.SI", "AJBU.SI", "M44U.SI", "K71U.SI",
            "BS6.SI", "G13.SI", "V03.SI", "U96.SI", "Y92.SI", "H78.SI"
        ]
    }
}

def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / (loss + 1e-9)
    return 100 - (100 / (1 + rs))

def fetch_and_analyze_market(market_key, market_info):
    tickers = market_info["tickers"]
    print(f"Fetching data for {market_info['name']} ({len(tickers)} stocks)...")
    
    try:
        data = yf.download(tickers, period="1y", interval="1d", group_by="ticker", progress=False)
    except Exception as e:
        print(f"Error fetching batch data for {market_key}: {e}")
        return []

    analyzed_stocks = []

    for ticker in tickers:
        try:
            df = data[ticker].dropna() if len(tickers) > 1 else data.dropna()
            if df.empty or len(df) < 50:
                continue

            close = df["Close"]
            current_price = float(close.iloc[-1])
            prev_close = float(close.iloc[-2])
            change_pct = ((current_price - prev_close) / prev_close) * 100

            sma_20 = float(close.rolling(20).mean().iloc[-1])
            sma_50 = float(close.rolling(50).mean().iloc[-1])
            sma_200 = float(close.rolling(200).mean().iloc[-1]) if len(close) >= 200 else sma_50
            rsi = float(calculate_rsi(close).iloc[-1])

            # Fetch metadata
            stock_obj = yf.Ticker(ticker)
            info = stock_obj.info or {}
            company_name = info.get("shortName") or info.get("longName") or ticker
            sector = info.get("sector") or "Equity"
            div_yield = (info.get("dividendYield") or 0) * 100
            pe_ratio = info.get("forwardPE") or info.get("trailingPE") or 0

            # Calculate horizon scores
            short_score = 0
            mid_score = 0
            long_score = 0

            # Short term scoring (oversold bounce or breakout momentum)
            if rsi < 40:
                short_score += 40
            elif 50 <= rsi <= 65:
                short_score += 25
            if current_price > sma_20:
                short_score += 30
            if change_pct > 0.5:
                short_score += 20

            # Mid term scoring (50D/200D SMA trend, Golden Cross)
            if sma_50 > sma_200:
                mid_score += 40
            if current_price > sma_50:
                mid_score += 35
            if 45 <= rsi <= 65:
                mid_score += 25

            # Long term scoring (Value, Dividends, Stability)
            if div_yield > 2.0:
                long_score += 35
            if pe_ratio > 0 and pe_ratio < 25:
                long_score += 35
            if current_price > sma_200:
                long_score += 30

            # Historical sparkline data (last 30 points)
            sparkline = [round(float(p), 2) for p in close.tail(30).values]
            sparkline_dates = [d.strftime("%b %d") for d in close.tail(30).index]

            analyzed_stocks.append({
                "ticker": ticker,
                "name": company_name,
                "sector": sector,
                "price": round(current_price, 2),
                "change_pct": round(change_pct, 2),
                "rsi": round(rsi, 1),
                "sma_50": round(sma_50, 2),
                "sma_200": round(sma_200, 2),
                "div_yield": round(div_yield, 2),
                "pe_ratio": round(pe_ratio, 1),
                "short_score": short_score,
                "mid_score": mid_score,
                "long_score": long_score,
                "sparkline": sparkline,
                "sparkline_dates": sparkline_dates
            })

        except Exception as err:
            continue

    return analyzed_stocks

def select_6_recommendations(stocks):
    """Allocates exactly 2 Short-Term, 2 Mid-Term, and 2 Long-Term non-overlapping picks."""
    allocated = {"short": [], "mid": [], "long": []}
    used_tickers = set()

    # 1. Select top 2 Short-Term
    sorted_short = sorted(stocks, key=lambda x: x["short_score"], reverse=True)
    for s in sorted_short:
        if len(allocated["short"]) < 2:
            allocated["short"].append(s)
            used_tickers.add(s["ticker"])

    # 2. Select top 2 Mid-Term
    sorted_mid = sorted([s for s in stocks if s["ticker"] not in used_tickers], key=lambda x: x["mid_score"], reverse=True)
    for s in sorted_mid:
        if len(allocated["mid"]) < 2:
            allocated["mid"].append(s)
            used_tickers.add(s["ticker"])

    # 3. Select top 2 Long-Term
    sorted_long = sorted([s for s in stocks if s["ticker"] not in used_tickers], key=lambda x: x["long_score"], reverse=True)
    for s in sorted_long:
        if len(allocated["long"]) < 2:
            allocated["long"].append(s)
            used_tickers.add(s["ticker"])

    return allocated

def send_telegram_alert(market_picks):
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not bot_token or not chat_id:
        print("Telegram tokens not set. Skipping alerts.")
        return

    msg = "📊 *DAILY MULTI-MARKET SCANNER REPORT*\n\n"
    for m_key, recs in market_picks.items():
        m_name = MARKET_UNIVERSES[m_key]["name"]
        curr = MARKET_UNIVERSES[m_key]["currency"]
        msg += f"🔹 *{m_name} Top 6 Recommendations*\n"
        
        msg += "⚡ *Short-Term Plays:*\n"
        for s in recs["short"]:
            msg += f"• `{s['ticker']}` ({s['name']}) - {curr}{s['price']} ({s['change_pct']:+0.2f}%)\n"

        msg += "📈 *Mid-Term Growth:*\n"
        for s in recs["mid"]:
            msg += f"• `{s['ticker']}` ({s['name']}) - {curr}{s['price']} ({s['change_pct']:+0.2f}%)\n"

        msg += "🛡️ *Long-Term Compounders:*\n"
        for s in recs["long"]:
            msg += f"• `{s['ticker']}` ({s['name']}) - {curr}{s['price']} ({s['change_pct']:+0.2f}%)\n"
        msg += "\n"

    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        requests.post(url, json={"chat_id": chat_id, "text": msg, "parse_mode": "Markdown"})
        print("✅ Telegram notification sent.")
    except Exception as e:
        print(f"Failed to send Telegram message: {e}")

def render_tabbed_dashboard(market_picks):
    now_str = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    html_head = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Global Market AI Scanner</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {{
            --bg-dark: #0f172a;
            --card-bg: #1e293b;
            --accent-blue: #38bdf8;
            --green: #4ade80;
            --red: #f87171;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --border: #334155;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--bg-dark);
            color: var(--text-main);
            margin: 0; padding: 20px;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        header {{
            display: flex; justify-content: space-between; align-items: center;
            padding-bottom: 20px; border-bottom: 1px solid var(--border); margin-bottom: 25px;
        }}
        h1 {{ margin: 0; font-size: 1.6rem; color: var(--accent-blue); }}
        .subtitle {{ font-size: 0.85rem; color: var(--text-muted); }}
        
        /* Tabs Styling */
        .tabs {{
            display: flex; gap: 10px; margin-bottom: 25px; border-bottom: 1px solid var(--border);
            padding-bottom: 10px; flex-wrap: wrap;
        }}
        .tab-btn {{
            background: #1e293b; border: 1px solid var(--border); color: var(--text-muted);
            padding: 10px 20px; border-radius: 8px; font-weight: 600; cursor: pointer;
            transition: all 0.2s ease;
        }}
        .tab-btn:hover {{ background: #334155; color: #fff; }}
        .tab-btn.active {{
            background: var(--accent-blue); color: #0f172a; border-color: var(--accent-blue);
        }}

        .tab-content {{ display: none; }}
        .tab-content.active {{ display: block; }}

        /* Section Layout */
        .horizon-title {{
            font-size: 1.2rem; margin: 25px 0 15px 0; color: #e2e8f0;
            display: flex; align-items: center; gap: 8px; border-left: 4px solid var(--accent-blue);
            padding-left: 10px;
        }}
        .grid {{
            display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 18px;
        }}
        
        .card {{
            background: var(--card-bg); border: 1px solid var(--border); border-radius: 12px;
            padding: 18px; transition: transform 0.2s ease, box-shadow 0.2s ease;
        }}
        .card:hover {{ transform: translateY(-3px); box-shadow: 0 8px 20px rgba(0,0,0,0.4); }}

        .card-header {{ display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px; }}
        .symbol {{ font-size: 1.3rem; font-weight: 700; color: #fff; }}
        .name {{ font-size: 0.82rem; color: var(--text-muted); }}
        .price {{ font-size: 1.2rem; font-weight: 700; text-align: right; }}
        .positive {{ color: var(--green); }}
        .negative {{ color: var(--red); }}

        .metrics {{
            display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px;
            background: #0f172a; padding: 10px; border-radius: 8px; margin: 12px 0;
            font-size: 0.8rem;
        }}
        .metric-item {{ text-align: center; }}
        .metric-label {{ color: var(--text-muted); margin-bottom: 2px; }}
        .metric-value {{ font-weight: 600; }}

        .btn-dive {{
            width: 100%; background: #334155; color: var(--text-main); border: none;
            padding: 8px; border-radius: 6px; cursor: pointer; font-weight: 600;
            transition: background 0.2s;
        }}
        .btn-dive:hover {{ background: var(--accent-blue); color: #0f172a; }}

        /* Modal */
        .modal {{
            display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.75); justify-content: center; align-items: center; z-index: 1000;
        }}
        .modal-content {{
            background: var(--card-bg); border-radius: 12px; width: 90%; max-width: 650px;
            padding: 24px; position: relative; border: 1px solid var(--border);
        }}
        .close-btn {{
            position: absolute; top: 15px; right: 20px; font-size: 1.5rem; color: var(--text-muted);
            cursor: pointer;
        }}
        .chart-container {{ height: 260px; margin-top: 15px; }}

        /* Action Buttons */
        .actions {{
            display: flex; gap: 10px; justify-content: flex-end; margin-top: 20px;
        }}
        .action-btn {{
            background: #1e293b; border: 1px solid var(--border); color: var(--text-main);
            padding: 8px 16px; border-radius: 6px; cursor: pointer; font-size: 0.85rem;
        }}
        .action-btn:hover {{ border-color: var(--accent-blue); color: var(--accent-blue); }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div>
                <h1>📈 Global Market Scanner</h1>
                <div class="subtitle">Last Scanned: {now_str}</div>
            </div>
            <div class="actions">
                <button class="action-btn" onclick="openTokenModal()">🔑 Configure Trigger</button>
                <button class="action-btn" onclick="triggerWorkflow()">⚡ Trigger Scan Now</button>
            </div>
        </header>

        <div class="tabs">
            <button class="tab-btn active" onclick="switchTab('DOW30')"> Dow 30</button>
            <button class="tab-btn" onclick="switchTab('NASDAQ100')">🚀 Nasdaq 100</button>
            <button class="tab-btn" onclick="switchTab('SP500')">🏛️ S&P 500</button>
            <button class="tab-btn" onclick="switchTab('SGX')">🇸🇬 SGX</button>
        </div>
"""

    html_tabs = ""
    is_first_tab = True

    for m_key, recs in market_picks.items():
        curr = MARKET_UNIVERSES[m_key]["currency"]
        active_class = "active" if is_first_tab else ""
        is_first_tab = False

        html_tabs += f'<div id="tab-{m_key}" class="tab-content {active_class}">'

        # Horizon Definitions
        horizons = [
            ("short", "⚡ Short-Term Tactical Plays (1–4 Weeks)", recs["short"]),
            ("mid", "📈 Mid-Term Growth & Trend (1–6 Months)", recs["mid"]),
            ("long", "🛡️ Long-Term Quality Compounders (6–12+ Months)", recs["long"])
        ]

        for h_key, h_title, stocks in horizons:
            html_tabs += f'<div class="horizon-title">{h_title}</div><div class="grid">'
            for s in stocks:
                chg_class = "positive" if s["change_pct"] >= 0 else "negative"
                chg_sign = "+" if s["change_pct"] >= 0 else ""
                spark_json = json.dumps(s["sparkline"])
                dates_json = json.dumps(s["sparkline_dates"])

                html_tabs += f"""
                <div class="card">
                    <div class="card-header">
                        <div>
                            <div class="symbol">{s['ticker']}</div>
                            <div class="name">{s['name']}</div>
                        </div>
                        <div class="price">
                            {curr}{s['price']}<br>
                            <span class="{chg_class}" style="font-size: 0.85rem;">{chg_sign}{s['change_pct']}%</span>
                        </div>
                    </div>
                    <div class="metrics">
                        <div class="metric-item">
                            <div class="metric-label">RSI (14)</div>
                            <div class="metric-value">{s['rsi']}</div>
                        </div>
                        <div class="metric-item">
                            <div class="metric-label">Div Yield</div>
                            <div class="metric-value">{s['div_yield']}%</div>
                        </div>
                        <div class="metric-item">
                            <div class="metric-label">P/E Ratio</div>
                            <div class="metric-value">{s['pe_ratio'] if s['pe_ratio'] > 0 else 'N/A'}</div>
                        </div>
                    </div>
                    <button class="btn-dive" onclick='openModal("{s['ticker']}", "{s['name']}", {spark_json}, {dates_json})'>Deep Dive Chart</button>
                </div>
                """
            html_tabs += '</div>'
        html_tabs += '</div>'

    html_footer = """
    </div>

    <div id="deepDiveModal" class="modal">
        <div class="modal-content">
            <span class="close-btn" onclick="closeModal()">&times;</span>
            <h3 id="modalTitle" style="margin:0 0 5px 0;"></h3>
            <div id="modalSubtitle" style="color: var(--text-muted); font-size:0.85rem;"></div>
            <div class="chart-container">
                <canvas id="priceChart"></canvas>
            </div>
        </div>
    </div>

    <script>
        let currentChart = null;

        function switchTab(tabId) {
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
            
            document.getElementById('tab-' + tabId).classList.add('active');
            event.currentTarget.classList.add('active');
        }

        function openModal(symbol, name, prices, dates) {
            document.getElementById('modalTitle').innerText = symbol + ' - Price Chart';
            document.getElementById('modalSubtitle').innerText = name;
            document.getElementById('deepDiveModal').style.display = 'flex';

            const ctx = document.getElementById('priceChart').getContext('2d');
            if (currentChart) currentChart.destroy();

            currentChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: dates,
                    datasets: [{
                        label: 'Price',
                        data: prices,
                        borderColor: '#38bdf8',
                        backgroundColor: 'rgba(56, 189, 248, 0.1)',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.2
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                        x: { grid: { color: '#334155' }, ticks: { color: '#94a3b8' } },
                        y: { grid: { color: '#334155' }, ticks: { color: '#94a3b8' } }
                    }
                }
            });
        }

        function closeModal() {
            document.getElementById('deepDiveModal').style.display = 'none';
        }

        function openTokenModal() {
            const username = prompt("Enter your GitHub Username:", localStorage.getItem("gh_user") || "");
            const token = prompt("Enter your GitHub PAT (Personal Access Token):", localStorage.getItem("gh_pat") || "");
            if (username && token) {
                localStorage.setItem("gh_user", username);
                localStorage.setItem("gh_pat", token);
                alert("Saved credentials to local browser storage!");
            }
        }

        async function triggerWorkflow() {
            const user = localStorage.getItem("gh_user");
            const token = localStorage.getItem("gh_pat");
            if (!user || !token) {
                alert("Please configure your GitHub Username and PAT first.");
                openTokenModal();
                return;
            }

            const repo = window.location.pathname.split('/')[1] || "sgx-stock-scanner";
            const url = `https://api.github.com/repos/${user}/${repo}/actions/workflows/scanner.yml/dispatches`;

            try {
                const response = await fetch(url, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Accept': 'application/vnd.github.v3+json',
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ ref: 'main' })
                });

                if (response.ok || response.status === 204) {
                    alert("🚀 Multi-Market scan triggered! View status in GitHub Actions.");
                } else {
                    alert("Error triggering workflow. Please check your PAT permissions or branch name.");
                }
            } catch (e) {
                alert("Failed to connect to GitHub API.");
            }
        }
    </script>
</body>
</html>
"""

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_head + html_tabs + html_footer)
    print("✅ Multi-Market tabbed dashboard generated: index.html")

def main():
    market_picks = {}
    for m_key, m_info in MARKET_UNIVERSES.items():
        stocks = fetch_and_analyze_market(m_key, m_info)
        recs = select_6_recommendations(stocks)
        market_picks[m_key] = recs

    render_tabbed_dashboard(market_picks)
    send_telegram_alert(market_picks)

if __name__ == "__main__":
    main()
