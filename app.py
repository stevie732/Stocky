from flask import Flask, render_template, jsonify
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime

app = Flask(__name__)

# Define profitability criteria
MIN_PERCENT_CHANGE = 0.1  # Minimum percentage increase to consider
MIN_VOLUME = 100000       # Minimum trading volume
MAX_PE_RATIO = 100        # Maximum P/E ratio
MIN_DIVIDEND_YIELD = 0    # Minimum dividend yield (%)
RSI_OVERBOUGHT = 70       # RSI threshold for overbought
RSI_OVERSOLD = 30         # RSI threshold for oversold

# List of stock tickers to analyze
stock_tickers = ['ARRY', 'NVDA', 'ULCC', 'DNA', 'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'SLA', 'NFLX', 'AMD', 'INTC', 'SPY']  # Array Technologies, NVIDIA, Frontier Airlines, Ginkgo Bioworks

def fetch_stock_data(stock):
    """Fetch historical stock data for a given stock object."""
    data = stock.history(period="1d")  # Fetch data for the last day
    return data

def calculate_rsi(data, period=14):
    """Calculate Relative Strength Index (RSI)."""
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def analyze_stock(ticker):
    """Analyze stock data based on profitability criteria."""
    stock = yf.Ticker(ticker)  # Create the stock object here
    data = fetch_stock_data(stock)
    if data.empty:
        return None

    # Get the stock's full name
    stock_info = stock.info
    stock_name = stock_info.get('longName', ticker)  # Use ticker if name is not available

    # Calculate percentage change
    price_change = (data['Close'].iloc[-1] - data['Open'].iloc[-1]) / data['Open'].iloc[-1] * 100
    volume = data['Volume'].iloc[-1]

    # Calculate RSI
    data['RSI'] = calculate_rsi(data)
    rsi = data['RSI'].iloc[-1]

    # Fetch fundamental data
    pe_ratio = stock_info.get('trailingPE', None)
    dividend_yield = stock_info.get('dividendYield', None) * 100 if stock_info.get('dividendYield') else 0

    # Check profitability criteria
    if (price_change >= MIN_PERCENT_CHANGE and
        volume >= MIN_VOLUME and
        (pe_ratio is None or pe_ratio <= MAX_PE_RATIO) and
        dividend_yield >= MIN_DIVIDEND_YIELD and
        RSI_OVERSOLD <= rsi <= RSI_OVERBOUGHT):
        return {
            'Ticker': ticker,
            'Name': stock_name,
            'Price Change (%)': round(price_change, 2),
            'Volume': volume,
            'Close Price': data['Close'].iloc[-1],
            'RSI': round(rsi, 2),
            'P/E Ratio': round(pe_ratio, 2) if pe_ratio else 'N/A',
            'Dividend Yield (%)': round(dividend_yield, 2)
        }
    return None

def find_profitable_stocks():
    """Find stocks that meet profitability criteria."""
    profitable_stocks = []
    for ticker in stock_tickers:
        result = analyze_stock(ticker)
        if result:
            profitable_stocks.append(result)
    return profitable_stocks

def save_results(results):
    """Save results to a CSV file."""
    df = pd.DataFrame(results)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"profitable_stocks_{timestamp}.csv"
    df.to_csv(filename, index=False)
    print(f"Results saved to {filename}")

def run_bot():
    """Main function to run the bot."""
    print("Searching for profitable stocks...")
    profitable_stocks = find_profitable_stocks()

    if profitable_stocks:
        print("\nProfitable Stocks Found:")
        df = pd.DataFrame(profitable_stocks)
        print(df)
        save_results(profitable_stocks)
    else:
        print("No profitable stocks found.")   

@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')

@app.route('/analyze')
def analyze():
    """Analyze stocks and return results as JSON."""
    profitable_stocks = []
    for ticker in stock_tickers:
        result = analyze_stock(ticker)
        if result:
            profitable_stocks.append(result)
    return jsonify(profitable_stocks)

if __name__ == "__main__":
    print("Stock Trade Tracking Bot is running...")
    app.run(debug=True)