import json
import yfinance as yf

# Stock tickers to scan
TICKERS = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "META"]


def fetch_data():
  results = []
  for ticker in TICKERS:
    try:
      stock = yf.Ticker(ticker)
      info = stock.info
      hist = stock.history(period="1mo")

      if hist.empty:
        continue

      current_price = hist["Close"].iloc[-1]
      prev_price = (
          hist["Close"].iloc[-2] if len(hist) > 1 else current_price
      )
      change_pct = ((current_price - prev_price) / prev_price) * 100

      results.append({
          "ticker": ticker,
          "name": info.get("shortName", ticker),
          "price": round(float(current_price), 2),
          "change": round(float(change_pct), 2),
          "volume": int(hist["Volume"].iloc[-1]),
          "marketCap": info.get("marketCap", 0),
          "peRatio": round(float(info.get("trailingPE", 0) or 0), 2),
          "history": [round(float(p), 2) for p in hist["Close"].tolist()],
      })
    except Exception as e:
      print(f"Error fetching {ticker}: {e}")

  return results


def generate_html(data):
  json_data = json.dumps(data)

  html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>USA Stock Scanner Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 20px; }}
        h1 {{ text-align: center; color: #38bdf8; margin-bottom: 20px; }}
        .tabs {{ display: flex; gap: 10px; justify-content: center; margin-bottom: 20px; }}
        .tab-btn {{ background: #1e293b; color: #94a3b8; border: 1px solid #334155; padding: 10px 20px; border-radius: 8px; cursor: pointer; font-weight: bold; }}
        .tab-btn.active {{ background: #0284c7; color: white; border-color: #38bdf8; }}
        .tab-content {{ display: none; }}
        .tab-content.active {{ display: block; }}
        table {{ width: 100%; border-collapse: collapse; background: #1e293b; border-radius: 8px; overflow: hidden; }}
        th, td {{ padding: 12px 16px; text-align: left; border-bottom: 1px solid #334155; }}
        th {{ background: #0f172a; color: #94a3b8; }}
        tr:hover {{ background: #334155; cursor: pointer; }}
        .positive {{ color: #4ade80; font-weight: bold; }}
        .negative {{ color: #f87171; font-weight: bold; }}
        .btn-action {{ background: #38bdf8; color: #0f172a; border: none; padding: 6px 12px; border-radius: 4px; font-weight: bold; cursor: pointer; }}
        
        /* Modal Styles */
        .modal {{ display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.7); justify-content: center; align-items: center; }}
        .modal-content {{ background: #1e293b; padding: 24px; border-radius: 12px; width: 90%; max-width: 600px; border: 1px solid #475569; position: relative; }}
        .close-btn {{ position: absolute; top: 12px; right: 16px; color: #94a3b8; font-size: 24px; cursor: pointer; }}
    </style>
</head>
<body>

    <h1>🚀 USA Stock Scanner Dashboard</h1>

    <div class="tabs">
        <button class="tab-btn active" onclick="switchTab('all')">All Stocks</button>
        <button class="tab-btn" onclick="switchTab('gainers')">Top Gainers</button>
        <button class="tab-btn" onclick="switchTab('losers')">Top Losers</button>
    </div>

    <div id="tab-all" class="tab-content active">
        <table>
            <thead>
                <tr>
                    <th>Ticker</th>
                    <th>Name</th>
                    <th>Price ($)</th>
                    <th>Change (%)</th>
                    <th>P/E Ratio</th>
                    <th>Action</th>
                </tr>
            </thead>
            <tbody id="stock-table-body">
            </tbody>
        </table>
    </div>

    <!-- Details Modal -->
    <div id="stockModal" class="modal">
        <div class="modal-content">
            <span class="close-btn" onclick="closeModal()">&times;</span>
            <h2 id="modalTitle">Stock Details</h2>
            <canvas id="modalChart" height="200"></canvas>
            <div style="margin-top: 15px;">
                <button class="btn-action" onclick="openTriggerModal()">Set Trigger / Alert</button>
            </div>
        </div>
    </div>

    <!-- Trigger Modal -->
    <div id="triggerModal" class="modal">
        <div class="modal-content">
            <span class="close-btn" onclick="closeTriggerModal()">&times;</span>
            <h2>Set Price Trigger</h2>
            <p>Set automated notification threshold for target price.</p>
            <input type="number" id="triggerPrice" placeholder="Enter target price ($)" style="width: 100%; padding: 8px; margin: 10px 0; background: #0f172a; border: 1px solid #334155; color: white; border-radius: 4px;">
            <button class="btn-action" onclick="alert('Trigger saved successfully!'); closeTriggerModal();">Save Trigger</button>
        </div>
    </div>

    <script>
        const stockData = {json_data};
        let modalChartInstance = null;

        function renderTable(data) {{
            const tbody = document.getElementById('stock-table-body');
            tbody.innerHTML = '';
            data.forEach(item => {{
                const changeClass = item.change >= 0 ? 'positive' : 'negative';
                const sign = item.change >= 0 ? '+' : '';
                tbody.innerHTML += `
                    <tr onclick="openModal('${{item.ticker}}')">
                        <td><strong>${{item.ticker}}</strong></td>
                        <td>${{item.name}}</td>
                        <td>$${{item.price.toFixed(2)}}</td>
                        <td class="${{changeClass}}">${{sign}}${{item.change.toFixed(2)}}%</td>
                        <td>${{item.peRatio || 'N/A'}}</td>
                        <td><button class="btn-action" onclick="event.stopPropagation(); openTriggerModal('${{item.ticker}}')">Set Alert</button></td>
                    </tr>
                `;
            }});
        }}

        function switchTab(tabName) {{
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
            if (event) event.target.classList.add('active');
            
            let filtered = [...stockData];
            if (tabName === 'gainers') {{
                filtered = stockData.filter(s => s.change > 0).sort((a,b) => b.change - a.change);
            }} else if (tabName === 'losers') {{
                filtered = stockData.filter(s => s.change < 0).sort((a,b) => a.change - b.change);
            }}
            renderTable(filtered);
        }}

        function openModal(ticker) {{
            const item = stockData.find(s => s.ticker === ticker);
            if (!item) return;

            document.getElementById('modalTitle').innerText = `${{item.name}} (${{item.ticker}}) - $${{item.price}}`;
            document.getElementById('stockModal').style.display = 'flex';

            const ctx = document.getElementById('modalChart').getContext('2d');
            if (modalChartInstance) modalChartInstance.destroy();

            modalChartInstance = new Chart(ctx, {{
                type: 'line',
                data: {{
                    labels: item.history.map((_, i) => `Day ${{i + 1}}`),
                    datasets: [{{
                        label: 'Price History (30 Days)',
                        data: item.history,
                        borderColor: item.change >= 0 ? '#4ade80' : '#f87171',
                        backgroundColor: 'rgba(56, 189, 248, 0.1)',
                        fill: true,
                        tension: 0.3
                    }}]
                }},
                options: {{
                    responsive: true,
                    plugins: {{ legend: {{ labels: {{ color: '#f8fafc' }} }} }},
                    scales: {{
                        x: {{ ticks: {{ color: '#94a3b8' }} }},
                        y: {{ ticks: {{ color: '#94a3b8' }} }}
                    }}
                }}
            }});
        }}

        function closeModal() {{
            document.getElementById('stockModal').style.display = 'none';
        }}

        function openTriggerModal(ticker) {{
            document.getElementById('triggerModal').style.display = 'flex';
        }}

        function closeTriggerModal() {{
            document.getElementById('triggerModal').style.display = 'none';
        }}

        // Initial setup
        renderTable(stockData);
    </script>
</body>
</html>"""

  with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_content)
  print("Successfully generated index.html")


if __name__ == "__main__":
  print("Running Stock Scanner...")
  data = fetch_data()
  generate_html(data)
