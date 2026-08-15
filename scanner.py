name: Run Stock Scanner

on:
  schedule:
    - cron: '0 0 * * *' # Runs daily (or your scheduled time)
  workflow_dispatch: # Allows manual trigger

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'

      - name: Install Dependencies
        run: |
          python -m pip install --upgrade pip
          pip install yfinance

      - name: Run Market Scanner Script
        run: python scanner.py

      # --- THIS IS THE CRITICAL MISSING STEP ---
      - name: Commit and Push Updated index.html
        run: |
          git config --global user.name "github-actions[bot]"
          git config --global user.email "github-actions[bot]@users.noreply.github.com"
          git add index.html
          git commit -m "Auto-update index.html [skip ci]" || echo "No changes to commit"
          git push
