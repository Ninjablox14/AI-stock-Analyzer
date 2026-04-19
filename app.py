import yfinance as yf
import matplotlib.pyplot as plt
from groq import Groq
import csv
import datetime
import os
import subprocess
import re
import pandas as pd
from colorama import init, Fore, Back, Style

# Initialize colorama
init(autoreset=True)

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed, will use environment variables directly

# Initialize Groq client
def get_groq_client():
    """Get Groq client with API key from file, environment, or user input"""
    api_key = None
    
    # Try to read from api_key.txt
    try:
        with open('api_key.txt', 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('Key ='):
                    api_key = line.split('=', 1)[1].strip()
                    break
    except FileNotFoundError:
        pass
    
    # If not found, try environment variable
    if not api_key:
        api_key = os.getenv('GROQ_API_KEY')
    
    # If still not found, prompt user
    if not api_key:
        api_key = input("Please enter your Groq API key: ").strip()
        if not api_key:
            raise ValueError("Groq API key is required.")
    
    return Groq(api_key=api_key)

client = get_groq_client()
MODEL_NAME = "groq/compound-mini"

def create_chat_completion(prompt, model=MODEL_NAME):
    try:
        return client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
    except Exception as e:
        if model != "llama-3.3-70b-versatile":
            print(f"{Fore.YELLOW}Warning: {model} failed ({e}). Retrying with llama-3.3-70b-versatile...{Style.RESET_ALL}")
            return client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}]
            )
        raise

def get_valid_period():
    """Get and validate a period input from user with retry on invalid input."""
    valid_periods = ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']
    while True:
        period = input("Enter analysis period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max): ").strip().lower()
        if period in valid_periods:
            return period
        print(f"{Fore.RED}Invalid period '{period}'. Please enter one of: {', '.join(valid_periods)}{Style.RESET_ALL}")

def calculate_rsi(prices, period=14):
    delta = prices.diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def calculate_macd(prices):
    ema12 = prices.ewm(span=12).mean()
    ema26 = prices.ewm(span=26).mean()
    macd = ema12 - ema26
    signal = macd.ewm(span=9).mean()
    return macd, signal

def run_professional_backtest(ticker, period='1y', initial_capital=10000, position_pct=1.0, 
                               stop_loss_pct=10, take_profit_pct=20, strategies=['RSI', 'MACD', 'MA']):
    """
    Professional-grade backtesting with multiple strategies, risk metrics, and comparison.
    
    Parameters:
    - ticker: Stock symbol
    - period: Analysis period (e.g., '1y', '2y', '5y')
    - initial_capital: Starting capital
    - position_pct: % of capital to use per trade (0.1 to 1.0)
    - stop_loss_pct: Stop loss percentage
    - take_profit_pct: Take profit percentage
    - strategies: List of strategies to test ['RSI', 'MACD', 'MA', 'COMBINED']
    """
    stock = yf.Ticker(ticker)
    hist = stock.history(period=period)
    if hist.empty:
        return None
    
    prices = hist['Close']
    dates = hist.index
    
    # Calculate indicators
    rsi = calculate_rsi(prices)
    macd_line, signal_line = calculate_macd(prices)
    ma20 = prices.rolling(window=20).mean()
    ma50 = prices.rolling(window=50).mean()
    
    results = {}
    
    for strategy in strategies:
        trades = []
        cash = initial_capital
        position = 0
        entry_price = 0
        entry_date = None
        portfolio_values = []
        
        start_idx = max(14, 50)  # Need enough data for indicators
        
        for i in range(start_idx, len(prices)):
            current_price = prices.iloc[i]
            current_date = dates[i]
            current_rsi = rsi.iloc[i] if i < len(rsi) else 50
            current_macd = macd_line.iloc[i] if i < len(macd_line) else 0
            current_signal = signal_line.iloc[i] if i < len(signal_line) else 0
            current_ma20 = ma20.iloc[i] if i < len(ma20) and not pd.isna(ma20.iloc[i]) else 0
            current_ma50 = ma50.iloc[i] if i < len(ma50) and not pd.isna(ma50.iloc[i]) else 0
            
            # Calculate current portfolio value
            portfolio_value = cash + (position * current_price) if position > 0 else cash
            portfolio_values.append(portfolio_value)
            
            # Generate signals based on strategy
            buy_signal = False
            sell_signal = False
            
            if strategy == 'RSI':
                buy_signal = current_rsi < 30
                sell_signal = current_rsi > 70
            elif strategy == 'MACD':
                buy_signal = current_macd > current_signal
                sell_signal = current_macd < current_signal
            elif strategy == 'MA':
                buy_signal = current_price > current_ma20 and current_ma20 > current_ma50
                sell_signal = current_price < current_ma20 or current_ma20 < current_ma50
            elif strategy == 'COMBINED':
                rsi_buy = current_rsi < 35
                macd_buy = current_macd > current_signal
                ma_buy = current_price > current_ma20
                buy_signal = rsi_buy and macd_buy and ma_buy
                
                rsi_sell = current_rsi > 65
                macd_sell = current_macd < current_signal
                ma_sell = current_price < current_ma20
                sell_signal = rsi_sell or macd_sell or ma_sell
            
            # Execute trades with position sizing
            trade_capital = cash * position_pct
            
            if position == 0 and buy_signal:
                shares = int(trade_capital // current_price)
                if shares > 0:
                    position = shares
                    cash -= shares * current_price
                    entry_price = current_price
                    entry_date = current_date
                    
            elif position > 0:
                # Check stop loss
                sl_triggered = (current_price - entry_price) / entry_price <= -(stop_loss_pct / 100)
                # Check take profit
                tp_triggered = (current_price - entry_price) / entry_price >= (take_profit_pct / 100)
                # Check strategy sell signal
                strategy_sell = sell_signal and (current_price - entry_price) > 0
                
                if sl_triggered or tp_triggered or strategy_sell:
                    cash += position * current_price
                    pl = (current_price - entry_price) * position
                    trades.append({
                        'entry_date': entry_date.strftime('%Y-%m-%d') if entry_date else 'N/A',
                        'exit_date': current_date.strftime('%Y-%m-%d'),
                        'entry_price': entry_price,
                        'exit_price': current_price,
                        'shares': position,
                        'pl': pl,
                        'return_pct': ((current_price - entry_price) / entry_price) * 100,
                        'exit_reason': 'STOP_LOSS' if sl_triggered else 'TAKE_PROFIT' if tp_triggered else 'SIGNAL'
                    })
                    position = 0
                    entry_price = 0
                    entry_date = None
        
        # Close any remaining position at end
        if position > 0:
            final_price = prices.iloc[-1]
            cash += position * final_price
            pl = (final_price - entry_price) * position
            trades.append({
                'entry_date': entry_date.strftime('%Y-%m-%d') if entry_date else 'N/A',
                'exit_date': dates[-1].strftime('%Y-%m-%d'),
                'entry_price': entry_price,
                'exit_price': final_price,
                'shares': position,
                'pl': pl,
                'return_pct': ((final_price - entry_price) / entry_price) * 100,
                'exit_reason': 'EOD'
            })
        
        # Calculate metrics
        final_value = cash
        total_return = ((final_value - initial_capital) / initial_capital) * 100
        buy_hold_return = ((prices.iloc[-1] - prices.iloc[start_idx]) / prices.iloc[start_idx]) * 100
        
        winning_trades = [t for t in trades if t['pl'] > 0]
        losing_trades = [t for t in trades if t['pl'] <= 0]
        win_rate = (len(winning_trades) / len(trades) * 100) if trades else 0
        
        # Calculate risk metrics
        if len(portfolio_values) > 1:
            returns = [(portfolio_values[i+1] - portfolio_values[i]) / portfolio_values[i] for i in range(len(portfolio_values)-1)]
            avg_return = sum(returns) / len(returns) if returns else 0
            std_return = (sum((r - avg_return) ** 2 for r in returns) / len(returns)) ** 0.5 if returns else 1
            sharpe_ratio = (avg_return * 252) / (std_return * (252 ** 0.5)) if std_return > 0 else 0
            
            # Max drawdown
            peak = portfolio_values[0]
            max_dd = 0
            for val in portfolio_values:
                if val > peak:
                    peak = val
                dd = (peak - val) / peak * 100
                if dd > max_dd:
                    max_dd = dd
        else:
            sharpe_ratio = 0
            max_dd = 0
        
        # Average trade metrics
        avg_win = sum(t['pl'] for t in winning_trades) / len(winning_trades) if winning_trades else 0
        avg_loss = sum(t['pl'] for t in losing_trades) / len(losing_trades) if losing_trades else 0
        profit_factor = abs(avg_win / avg_loss) if avg_loss != 0 else 0
        
        results[strategy] = {
            'final_value': final_value,
            'total_return': total_return,
            'buy_hold_return': buy_hold_return,
            'vs_buy_hold': total_return - buy_hold_return,
            'num_trades': len(trades),
            'win_rate': win_rate,
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_dd,
            'trades': trades
        }
    
    return results

def backtest_summary(ticker, period='1y'):
    """Legacy function for simple backtest - now runs professional version"""
    results = run_professional_backtest(ticker, period, strategies=['RSI'])
    if results and 'RSI' in results:
        r = results['RSI']
        return {
            'final_value': r['final_value'],
            'total_return': r['total_return'],
            'buy_hold_value': r['final_value'] / (1 + r['total_return']/100) * (1 + r['buy_hold_return']/100),
            'win_rate': r['win_rate'],
            'num_trades': r['num_trades'],
            'sharpe_ratio': r['sharpe_ratio'],
            'max_drawdown': r['max_drawdown'],
            'profit_factor': r['profit_factor'],
            'vs_buy_hold': r.get('vs_buy_hold', 0)
        }
    return {'total_return': 0, 'num_trades': 0, 'win_rate': 0, 'vs_buy_hold': 0, 'sharpe_ratio': 0, 'max_drawdown': 0, 'profit_factor': 0}

def get_tickers_from_groq(description):
    description = description.strip()
    if len(description) > 200:
        description = description[:200].rstrip() + "..."

    prompt = (
        f"Search recent stock news, earnings, analyst upgrades, catalysts, and sector momentum for: '{description}'. "
        "Return exactly 5 tickers separated by commas. No explanation, no extra text. "
        "Example: AAPL,MSFT,GOOGL,AMZN,TSLA"
    )

    response = create_chat_completion(prompt, model="groq/compound-mini")
    raw = response.choices[0].message.content.strip()
    tickers = re.findall(r'\b[A-Z]{1,5}\b', raw)
    return tickers[:5]

def analyze_stocks(tickers, period):
    all_data = {}
    backtest_summaries = {}
    summary_for_ai = []

    for ticker in tickers:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period)

        if hist.empty:
            continue

        start_price = hist["Close"].iloc[0]
        end_price = hist["Close"].iloc[-1]
        change = ((end_price - start_price) / start_price) * 100
        high = hist["Close"].max()
        low = hist["Close"].min()
        avg = hist["Close"].mean()
        avg_volume = hist["Volume"].mean()
        last_volume = hist["Volume"].iloc[-1]
        volume_signal = "HIGH" if last_volume > avg_volume * 1.5 else "LOW" if last_volume < avg_volume * 0.5 else "NORMAL"

        ma20 = hist["Close"].rolling(window=20).mean().iloc[-1]
        rsi = calculate_rsi(hist["Close"]).iloc[-1]
        macd_series, signal_series = calculate_macd(hist["Close"])
        macd_val = macd_series.iloc[-1]
        macd_signal = signal_series.iloc[-1]

        ma_signal = "BUY" if end_price > ma20 else "SELL"
        rsi_signal = "OVERSOLD - BUY" if rsi < 30 else "OVERBOUGHT - SELL" if rsi > 70 else "NEUTRAL"
        macd_signal_str = "BUY" if macd_val > macd_signal else "SELL"

        backtest = backtest_summary(ticker, period)

        all_data[ticker] = {
            "change": change,
            "price": end_price,
            "rsi": rsi,
            "macd_signal": macd_signal_str,
            "ma_signal": ma_signal,
            "volume_signal": volume_signal,
            "beat_spy": "",  # will set later
            "high": high,
            "low": low,
            "avg": avg,
            "last_volume": last_volume,
            "avg_volume": avg_volume,
            "rsi_signal": rsi_signal,
            "backtest": backtest
        }

        backtest_summaries[ticker] = backtest

        summary_for_ai.append(
            f"{ticker}: Price=${end_price:.2f}, Change={change:.2f}%, "
            f"RSI={rsi:.1f} ({rsi_signal}), "
            f"MA20 Signal={ma_signal}, "
            f"MACD Signal={macd_signal_str}, "
            f"Volume={volume_signal}, "
            f"Backtest: {backtest['total_return']:.1f}% return, {backtest['win_rate']:.1f}% win rate, {backtest['num_trades']} trades"
        )

    # S&P 500
    spy = yf.Ticker("SPY")
    spy_hist = spy.history(period=period)
    spy_change = ((spy_hist["Close"].iloc[-1] - spy_hist["Close"].iloc[0]) / spy_hist["Close"].iloc[0]) * 100 if not spy_hist.empty else 0

    for ticker in all_data:
        all_data[ticker]["beat_spy"] = "Yes" if all_data[ticker]["change"] > spy_change else "No"

    # AI Analysis with backtesting
    tickers_str = ', '.join(all_data.keys())
    short_summary = []
    for item in summary_for_ai:
        if len(item) > 180:
            short_summary.append(item[:177].rstrip() + '...')
        else:
            short_summary.append(item)

    prompt = (
        f"Search recent stock news, analyst ratings, and market catalysts for: {tickers_str}. "
        "Analyze them using the technical indicators below and current news. Do not rely on general reputation or hype. "
        "For each stock give one sentence on what is happening now, a technical signal summary, and BUY/HOLD/SELL with a reason. "
        "Then give top 2 buys, top 2 sells or avoids, and one market observation. "
        "Be direct. No disclaimers. No generic advice.\n\n"
        f"Technical Data:\n{chr(10).join(short_summary)}\n\n"
        f"S&P 500 benchmark: {spy_change:.2f}%"
    )

    response = create_chat_completion(prompt, model="groq/compound-mini")
    ai_analysis = response.choices[0].message.content

    # Chart
    plt.figure(figsize=(10, 5))
    changes = {t: all_data[t]["change"] for t in all_data}
    colors = ["green" if v >= 0 else "red" for v in changes.values()]
    plt.bar(changes.keys(), changes.values(), color=colors)
    plt.axhline(spy_change, color="blue", linewidth=1.5, linestyle="--", label=f"S&P 500 ({spy_change:.2f}%)")
    plt.title(f"Stock Performance vs S&P 500 - {period} (%)")
    plt.xlabel("Ticker")
    plt.ylabel("% Change")
    plt.axhline(0, color="black", linewidth=0.8)
    plt.legend()
    plt.tight_layout()
    chart_path = f"chart_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    plt.savefig(chart_path)
    plt.close()

    return all_data, summary_for_ai, spy_change, ai_analysis, chart_path, backtest_summaries

def check_alerts():
    alerts_file = "alerts.csv"
    if not os.path.exists(alerts_file):
        return []
    triggered = []
    with open(alerts_file, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            ticker = row['ticker']
            action = row['action']
            target_price = float(row['price'])
            stock = yf.Ticker(ticker)
            current_price = stock.history(period="1d")["Close"].iloc[-1]
            if (action == 'BUY' and current_price <= target_price) or (action == 'SELL' and current_price >= target_price):
                triggered.append({
                    'ticker': ticker,
                    'action': action,
                    'target_price': target_price,
                    'current_price': current_price
                })
    return triggered

def save_alert(ticker, action, price):
    alerts_file = "alerts.csv"
    file_exists = os.path.exists(alerts_file)
    with open(alerts_file, 'a', newline='') as csvfile:
        fieldnames = ['ticker', 'action', 'price', 'date_saved']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            'ticker': ticker,
            'action': action,
            'price': price,
            'date_saved': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })

def open_and_handle_chart(chart_path):
    try:
        os.startfile(chart_path)  # Windows
    except AttributeError:
        try:
            subprocess.run(['open', chart_path])  # macOS
        except:
            subprocess.run(['xdg-open', chart_path])  # Linux
    print(f"Chart opened: {chart_path}")
    choice = input("Do you want to save the chart (s) or delete it (d)? ").strip().lower()
    if choice == 'd':
        os.remove(chart_path)
        print("Chart deleted.")
    else:
        print(f"Chart saved as {chart_path}")

def main():
    print(f"{Fore.CYAN}=== AI Stock Analyzer ==={Style.RESET_ALL}")
    print(f"{Fore.GREEN}Using model: {MODEL_NAME}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}⚠️  IMPORTANT: This is AI-powered software. AI can make mistakes and should not be trusted")
    print(f"{Fore.YELLOW}   completely for making financial decisions. Always do your own research!{Style.RESET_ALL}")
    print()

    # Check alerts
    triggered_alerts = check_alerts()
    if triggered_alerts:
        print(f"\n{Fore.RED}🚨 ALERTS TRIGGERED:{Style.RESET_ALL}")
        for alert in triggered_alerts:
            print(f"{alert['ticker']}: {alert['action']} at ${alert['target_price']:.2f} - Current: ${alert['current_price']:.2f}")
        print()

    while True:
        print(f"\n{Fore.BLUE}Choose an option:{Style.RESET_ALL}")
        print("1. Analyze specific stocks")
        print("2. Get AI recommendations")
        print("3. Exit")
        choice = input("Enter choice (1-3): ").strip()

        if choice == '1':
            tickers_str = input("Enter tickers separated by commas: ")
            tickers = [t.strip().upper() for t in tickers_str.split(',')]
            period = get_valid_period()
            try:
                analysis_data = perform_analysis(tickers, period)
                q_and_a_mode(analysis_data)
            except Exception as e:
                print(f"{Fore.RED}Error: Invalid ticker or data unavailable. Please check the ticker symbols and try again.{Style.RESET_ALL}")
                print(f"{Fore.RED}Details: {str(e)}{Style.RESET_ALL}")
                continue

        elif choice == '2':
            focus = input("What are you looking for? Specific industries, market recommendations, or stocks to look into: ")
            period = get_valid_period()
            try:
                tickers = get_tickers_from_groq(focus)
                print(f"AI selected stocks: {', '.join(tickers)}")
                analysis_data = perform_analysis(tickers, period)
                q_and_a_mode(analysis_data)
            except Exception as e:
                print(f"{Fore.RED}Error: Invalid ticker or data unavailable. Please try again.{Style.RESET_ALL}")
                print(f"{Fore.RED}Details: {str(e)}{Style.RESET_ALL}")
                continue

        elif choice == '3':
            print("Goodbye!")
            break
        else:
            print(f"{Fore.RED}Invalid choice. Try again.{Style.RESET_ALL}")

def perform_analysis(tickers, period):
    print("\nAnalyzing stocks... (this may take a moment)")
    all_data, summary_for_ai, spy_change, ai_analysis, chart_path, backtests = analyze_stocks(tickers, period)

    print(f"\n{Fore.CYAN}=== Stock Analysis Results ({period}) ==={Style.RESET_ALL}")
    spy_color = Fore.GREEN if spy_change >= 0 else Fore.RED
    print(f"S&P 500 Change: {spy_color}{spy_change:.2f}%{Style.RESET_ALL}")
    print(f"\n{Fore.BLUE}Stock Data:{Style.RESET_ALL}")
    print(f"{Fore.BLUE}Ticker | Price    | Change (%) | RSI   | MACD | MA20 | Volume | Beat SPY | Backtest Return{Style.RESET_ALL}")
    print("-" * 85)
    for ticker, data in all_data.items():
        bt = data['backtest']
        change_color = Fore.GREEN if data['change'] >= 0 else Fore.RED
        rsi_color = Fore.GREEN if data['rsi'] < 30 else Fore.RED if data['rsi'] > 70 else Fore.YELLOW
        macd_color = Fore.GREEN if data['macd_signal'] == 'BUY' else Fore.RED
        ma_color = Fore.GREEN if data['ma_signal'] == 'BUY' else Fore.RED
        beat_color = Fore.GREEN if data['beat_spy'] == 'Yes' else Fore.RED
        bt_color = Fore.GREEN if bt['total_return'] >= 0 else Fore.RED
        print(f"{ticker:<6} | ${data['price']:<8.2f} | {change_color}{data['change']:<10.2f}{Style.RESET_ALL} | {rsi_color}{data['rsi']:<5.1f}{Style.RESET_ALL} | {macd_color}{data['macd_signal']:<4}{Style.RESET_ALL} | {ma_color}{data['ma_signal']:<4}{Style.RESET_ALL} | {data['volume_signal']:<6} | {beat_color}{data['beat_spy']:<7}{Style.RESET_ALL} | {bt_color}{bt['total_return']:<6.1f}%{Style.RESET_ALL}")

    # Detailed Backtest Results
    print(f"\n{Fore.CYAN}=== 📊 Professional Backtest Results ==={Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}Strategy: RSI + MACD + MA Combined | Position: 100% | Stop Loss: 10% | Take Profit: 20%{Style.RESET_ALL}")
    print("-" * 90)
    print(f"{'Ticker':<8} | {'Return':>8} | {'vs B&H':>8} | {'Trades':>6} | {'Win%':>6} | {'Sharpe':>7} | {'Max DD':>7} | {'P.Factor':>8}")
    print("-" * 90)
    for ticker, bt in backtests.items():
        ret_color = Fore.GREEN if bt['total_return'] >= 0 else Fore.RED
        vs_color = Fore.GREEN if bt.get('vs_buy_hold', 0) >= 0 else Fore.RED
        sharpe_color = Fore.GREEN if bt.get('sharpe_ratio', 0) > 1 else Fore.YELLOW if bt.get('sharpe_ratio', 0) > 0 else Fore.RED
        dd_color = Fore.GREEN if bt.get('max_drawdown', 100) < 10 else Fore.YELLOW if bt.get('max_drawdown', 100) < 20 else Fore.RED
        print(f"{ticker:<8} | {ret_color}{bt['total_return']:>7.1f}%{Style.RESET_ALL} | {vs_color}{bt.get('vs_buy_hold', 0):>7.1f}%{Style.RESET_ALL} | {bt['num_trades']:>6} | {bt['win_rate']:>5.1f}% | {sharpe_color}{bt.get('sharpe_ratio', 0):>6.2f}{Style.RESET_ALL} | {dd_color}{bt.get('max_drawdown', 0):>6.1f}%{Style.RESET_ALL} | {bt.get('profit_factor', 0):>8.2f}")
    print("-" * 90)
    print(f"{Fore.CYAN}Metrics Explained:{Style.RESET_ALL}")
    print(f"  • Return: Strategy total return | vs B&H: Outperformance vs buy-and-hold")
    print(f"  • Trades: Number of completed trades | Win%: Percentage of profitable trades")
    print(f"  • Sharpe: Risk-adjusted return (>1 is good, >2 is excellent) | Max DD: Maximum drawdown")
    print(f"  • P.Factor: Profit factor (>1.5 is good, >2 is excellent)")

    print(f"\n{Fore.CYAN}=== AI Recommendations ==={Style.RESET_ALL}")
    print(ai_analysis)
    print(f"\n{Fore.YELLOW}⚠️  Disclaimer: This analysis is AI-generated and may contain errors. Always verify information")
    print(f"{Fore.YELLOW}   and consult financial professionals before making investment decisions.{Style.RESET_ALL}")

    # Handle chart
    open_and_handle_chart(chart_path)

    # Set alerts
    set_alert = input("\nDo you want to set price alerts based on recommendations? (y/n): ").strip().lower()
    if set_alert == 'y':
        for ticker in all_data:
            action = input(f"Set alert for {ticker} - BUY, SELL, or skip (s)? ").strip().upper()
            if action in ['BUY', 'SELL']:
                price = float(input(f"Enter target price for {action}: ").strip())
                save_alert(ticker, action, price)
                print(f"{Fore.GREEN}Alert saved: {ticker} {action} at ${price:.2f}{Style.RESET_ALL}")

    return {
        'tickers': tickers,
        'period': period,
        'all_data': all_data,
        'summary_for_ai': summary_for_ai,
        'spy_change': spy_change,
        'ai_analysis': ai_analysis,
        'backtests': backtests
    }

def q_and_a_mode(analysis_data):
    print(f"\n{Fore.CYAN}=== Q&A Mode ==={Style.RESET_ALL}")
    print("Ask questions about these stocks, analysis, or potential changes.")
    print("Type 'done' to exit Q&A mode.")

    context = f"""
Current Analysis Context:
Stocks: {', '.join(analysis_data['tickers'])}
Period: {analysis_data['period']}
S&P 500 Change: {analysis_data['spy_change']:.2f}%

Technical Data:
{chr(10).join(analysis_data['summary_for_ai'])}

AI Recommendations:
{analysis_data['ai_analysis']}
"""

    while True:
        question = input(f"\n{Fore.GREEN}Your question (type 'done', 'exit', or 'quit' to return to menu):{Style.RESET_ALL} ").strip()
        if question.lower() in ['done', 'exit', 'quit']:
            print(f"{Fore.BLUE}Returning to main menu...{Style.RESET_ALL}")
            break

        prompt = f"""You are a professional financial analyst. Based on the following analysis context, answer the user's question directly and helpfully. If they ask about changes or modifications, assess viability and provide specific recommendations.

{context}

User Question: {question}

Answer:"""

        response = create_chat_completion(prompt, model="groq/compound-mini")
        answer = response.choices[0].message.content
        print(f"\n{Fore.YELLOW}Analyst:{Style.RESET_ALL} {answer}")

if __name__ == '__main__':
    main()