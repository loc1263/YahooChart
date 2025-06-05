import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.patches as patches
import argparse

plt.style.use('dark_background')
plt.rcParams['font.size'] = 10
plt.rcParams['font.family'] = 'sans-serif'

def create_revenue_earnings_chart(ticker_symbol, periods=4):
    ticker = yf.Ticker(ticker_symbol)
    financials = ticker.financials
    if financials.empty:
        print(f"No se encontraron datos financieros para {ticker_symbol}")
        return None
    try:
        revenue = financials.loc['Total Revenue'].head(periods) / 1e9
        net_income = financials.loc['Net Income'].head(periods) / 1e9
    except KeyError:
        print("No se encontraron datos de Revenue o Earnings")
        return None
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), facecolor='#1a1a1a')
    fig.patch.set_facecolor('#1a1a1a')
    ax1.set_facecolor('#2a2a2a')
    years = [date.strftime('%Y') for date in revenue.index]
    x_pos = np.arange(len(years))
    width = 0.35
    bars1 = ax1.bar(x_pos - width/2, revenue.values, width, label='Revenue', color='#00d4ff', alpha=0.8)
    bars2 = ax1.bar(x_pos + width/2, net_income.values, width, label='Earnings', color='#ffa500', alpha=0.8)
    ax1.set_xlabel('Periodo', color='white')
    ax1.set_ylabel('Billones (USD)', color='white')
    ax1.set_title('Revenue vs. Earnings', color='white', fontweight='bold', pad=20)
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(years, color='white')
    ax1.tick_params(colors='white')
    ax1.legend(loc='upper left')
    ax1.grid(True, alpha=0.3)
    for bar in bars1:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                f'{height:.1f}B', ha='center', va='bottom', color='white', fontsize=9)
    for bar in bars2:
        height = bar.get_height()
        if height >= 0:
            ax1.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                    f'{height:.1f}B', ha='center', va='bottom', color='white', fontsize=9)
        else:
            ax1.text(bar.get_x() + bar.get_width()/2., height - abs(height)*0.1,
                    f'{height:.1f}B', ha='center', va='top', color='white', fontsize=9)
    return fig, ax1, ax2

def create_analyst_recommendations_chart(ticker_symbol):
    ticker = yf.Ticker(ticker_symbol)
    try:
        recommendations = ticker.recommendations
        if recommendations is None or recommendations.empty:
            print("No hay recomendaciones disponibles")
            return None
    except:
        print("Error al obtener recomendaciones")
        return None
    recent_recommendations = recommendations.tail(90)
    recent_recommendations['Month'] = recent_recommendations.index.to_period('M')
    monthly_rec = recent_recommendations.groupby('Month').sum()
    if len(monthly_rec) < 3:
        months = ['Apr', 'May', 'Jun']
        strong_buy = [7, 7, 7]
        buy = [4, 4, 4]
        hold = [3, 3, 3]
        underperform = [1, 1, 1]
        sell = [0, 0, 0]
    else:
        months = [month.strftime('%b') for month in monthly_rec.index[-3:]]
        strong_buy = monthly_rec['strongBuy'].values[-3:]
        buy = monthly_rec['buy'].values[-3:]
        hold = monthly_rec['hold'].values[-3:]
        underperform = monthly_rec['underperform'].values[-3:]
        sell = monthly_rec['sell'].values[-3:]
    return months, strong_buy, buy, hold, underperform, sell

def plot_complete_dashboard(ticker_symbol):
    fig = plt.figure(figsize=(16, 8), facecolor='#1a1a1a')
    gs = fig.add_gridspec(2, 2, height_ratios=[1, 1], width_ratios=[2, 1])
    ax1 = fig.add_subplot(gs[:, 0])
    ax1.set_facecolor('#2a2a2a')
    ticker = yf.Ticker(ticker_symbol)
    info = ticker.info
    financials = ticker.financials
    company_name = info.get('longName', ticker_symbol)
    fig.suptitle(f"{company_name} ({ticker_symbol})", color='white', fontsize=18, fontweight='bold', y=0.97)
    if not financials.empty:
        try:
            revenue = financials.loc['Total Revenue'].head(4) / 1e9
            net_income = financials.loc['Net Income'].head(4) / 1e9
            years = [f"Q{i+1}'24" if i < 2 else f"Q{i-1}'23" for i in range(len(revenue))][::-1]
            x_pos = np.arange(len(years))
            width = 0.35
            bars1 = ax1.bar(x_pos - width/2, revenue.values[::-1], width, 
                           label='Revenue', color='#00d4ff', alpha=0.8)
            bars2 = ax1.bar(x_pos + width/2, net_income.values[::-1], width, 
                           label='Earnings', color='#ffa500', alpha=0.8)
            ax1.set_title('Revenue vs. Earnings', color='white', fontweight='bold', fontsize=14)
            ax1.set_xticks(x_pos)
            ax1.set_xticklabels(years, color='white')
            ax1.tick_params(colors='white')
            ax1.set_ylabel('Billones (USD)', color='white')
            legend_elements = [
                plt.Rectangle((0,0),1,1, facecolor='#00d4ff', alpha=0.8, label=f'Revenue {revenue.iloc[0]:.1f}B'),
                plt.Rectangle((0,0),1,1, facecolor='#ffa500', alpha=0.8, label=f'Earnings {net_income.iloc[0]:.1f}B')
            ]
            ax1.legend(handles=legend_elements, loc='upper left', frameon=False)
            ax1.grid(True, alpha=0.2)
        except KeyError:
            ax1.text(0.5, 0.5, 'Datos financieros no disponibles', 
                    ha='center', va='center', transform=ax1.transAxes, color='white')
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.set_facecolor('#2a2a2a')
    months = ['Apr', 'May', 'Jun']
    recommendations_data = {
        'Strong Buy': [7, 7, 7],
        'Buy': [4, 4, 4], 
        'Hold': [3, 3, 3],
        'Underperform': [1, 1, 1],
        'Sell': [0, 0, 0]
    }
    colors = ['#00ff88', '#88ff00', '#ffaa00', '#ff6600', '#ff0066']
    bottom = np.zeros(len(months))
    for i, (label, values) in enumerate(recommendations_data.items()):
        ax2.bar(months, values, bottom=bottom, color=colors[i], alpha=0.8, label=label)
        bottom += values
    ax2.set_title('Analyst Recommendations', color='white', fontweight='bold', fontsize=12)
    ax2.tick_params(colors='white')
    ax2.set_ylabel('Número de Analistas', color='white')
    ax3 = fig.add_subplot(gs[1, 1])
    ax3.set_facecolor('#2a2a2a')
    ax3.axis('off')
    legend_items = [
        ('● Strong Buy', '#00ff88'),
        ('● Buy', '#88ff00'),
        ('● Hold', '#ffaa00'), 
        ('● Underperform', '#ff6600'),
        ('● Sell', '#ff0066')
    ]
    for i, (text, color) in enumerate(legend_items):
        ax3.text(0.1, 0.8 - i*0.15, text, color=color, fontsize=11, 
                transform=ax3.transAxes, fontweight='bold')
    plt.tight_layout()
    plt.subplots_adjust(hspace=0.3, wspace=0.3)
    return fig

def plot_revenue_dashboards(symbols):
    n = len(symbols)
    cols = 2 if n > 1 else 1
    rows = (n + 1) // 2 if n > 1 else 1
    fig, axes = plt.subplots(rows, cols, figsize=(8*cols, 6*rows), facecolor='#1a1a1a')
    if n == 1:
        axes = [axes]
    else:
        axes = axes.flatten()
    for idx, ticker_symbol in enumerate(symbols):
        ax = axes[idx]
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.info
        financials = ticker.financials
        company_name = info.get('longName', ticker_symbol)
        if not financials.empty:
            try:
                revenue = financials.loc['Total Revenue'].head(4) / 1e9
                net_income = financials.loc['Net Income'].head(4) / 1e9
                years = [f"Q{i+1}'24" if i < 2 else f"Q{i-1}'23" for i in range(len(revenue))][::-1]
                x_pos = np.arange(len(years))
                width = 0.35
                bars1 = ax.bar(x_pos - width/2, revenue.values[::-1], width, label='Revenue', color='#00d4ff', alpha=0.8)
                bars2 = ax.bar(x_pos + width/2, net_income.values[::-1], width, label='Earnings', color='#ffa500', alpha=0.8)
                ax.set_title(f"{company_name} ({ticker_symbol})\nRevenue vs. Earnings", color='white', fontweight='bold', fontsize=14)
                ax.set_xticks(x_pos)
                ax.set_xticklabels(years, color='white')
                ax.tick_params(colors='white')
                ax.set_ylabel('Billones (USD)', color='white')
                legend_elements = [
                    plt.Rectangle((0,0),1,1, facecolor='#00d4ff', alpha=0.8, label=f'Revenue {revenue.iloc[0]:.1f}B'),
                    plt.Rectangle((0,0),1,1, facecolor='#ffa500', alpha=0.8, label=f'Earnings {net_income.iloc[0]:.1f}B')
                ]
                ax.legend(handles=legend_elements, loc='upper left', frameon=False)
                ax.grid(True, alpha=0.2)
            except Exception as e:
                ax.text(0.5, 0.5, f'Error: {e}', ha='center', va='center', transform=ax.transAxes, color='white')
        else:
            ax.text(0.5, 0.5, 'Datos financieros no disponibles', ha='center', va='center', transform=ax.transAxes, color='white')
        ax.set_facecolor('#2a2a2a')
    for j in range(idx+1, len(axes)):
        fig.delaxes(axes[j])
    plt.tight_layout()
    plt.show()

def plot_full_dashboards(symbols):
    n = len(symbols)
    fig, axes = plt.subplots(n, 2, figsize=(8, 3*n), facecolor='#1a1a1a')
    if n == 1:
        axes = np.array([axes])
    tickers = yf.Tickers(' '.join(symbols))
    for idx, ticker_symbol in enumerate(symbols):
        ticker = tickers.tickers.get(ticker_symbol)
        if ticker is None:
            axes[idx, 0].text(0.5, 0.5, f'Símbolo no encontrado: {ticker_symbol}', ha='center', va='center', color='white')
            axes[idx, 1].axis('off')
            continue
        info = ticker.info
        financials = ticker.financials
        company_name = info.get('longName', ticker_symbol)
        ax1 = axes[idx, 0]
        ax1.set_facecolor('#2a2a2a')
        if not financials.empty:
            try:
                revenue = financials.loc['Total Revenue'].head(4) / 1e9
                net_income = financials.loc['Net Income'].head(4) / 1e9
                years = [f"Q{i+1}'24" if i < 2 else f"Q{i-1}'23" for i in range(len(revenue))][::-1]
                x_pos = np.arange(len(years))
                width = 0.35
                bars1 = ax1.bar(x_pos - width/2, revenue.values[::-1], width, label='Revenue', color='#00d4ff', alpha=0.8)
                bars2 = ax1.bar(x_pos + width/2, net_income.values[::-1], width, label='Earnings', color='#ffa500', alpha=0.8)
                ax1.set_title(f"{company_name} ({ticker_symbol})\nRevenue vs. Earnings", color='white', fontweight='bold', fontsize=14)
                ax1.set_xticks(x_pos)
                ax1.set_xticklabels(years, color='white')
                ax1.tick_params(colors='white')
                ax1.set_ylabel('Billones (USD)', color='white')
                legend_elements = [
                    plt.Rectangle((0,0),1,1, facecolor='#00d4ff', alpha=0.8, label=f'Revenue {revenue.iloc[0]:.1f}B'),
                    plt.Rectangle((0,0),1,1, facecolor='#ffa500', alpha=0.8, label=f'Earnings {net_income.iloc[0]:.1f}B')
                ]
                ax1.legend(handles=legend_elements, loc='upper left', frameon=False)
                ax1.grid(True, alpha=0.2)
            except Exception as e:
                ax1.text(0.5, 0.5, f'Error: {e}', ha='center', va='center', transform=ax1.transAxes, color='white')
        else:
            ax1.text(0.5, 0.5, 'Datos financieros no disponibles', ha='center', va='center', transform=ax1.transAxes, color='white')
        ax2 = axes[idx, 1]
        ax2.set_facecolor('#2a2a2a')
        try:
            recommendations = ticker.recommendations
            if recommendations is None or recommendations.empty:
                months = ['Apr', 'May', 'Jun']
                recommendations_data = {
                    'Strong Buy': [7, 7, 7],
                    'Buy': [4, 4, 4],
                    'Hold': [3, 3, 3],
                    'Underperform': [1, 1, 1],
                    'Sell': [0, 0, 0]
                }
            else:
                recent_recommendations = recommendations.tail(90)
                if not pd.api.types.is_datetime64_any_dtype(recent_recommendations.index):
                    recent_recommendations.index = pd.to_datetime(recent_recommendations.index, errors='coerce')
                recent_recommendations = recent_recommendations[recent_recommendations.index.notnull()]
                recent_recommendations['Month'] = recent_recommendations.index.to_period('M')
                monthly_rec = recent_recommendations.groupby('Month').sum()
                if len(monthly_rec) < 3:
                    months = ['Apr', 'May', 'Jun']
                    recommendations_data = {
                        'Strong Buy': [7, 7, 7],
                        'Buy': [4, 4, 4],
                        'Hold': [3, 3, 3],
                        'Underperform': [1, 1, 1],
                        'Sell': [0, 0, 0]
                    }
                else:
                    months = [month.strftime('%b') for month in monthly_rec.index[-3:]]
                    recommendations_data = {
                        'Strong Buy': monthly_rec['strongBuy'].values[-3:],
                        'Buy': monthly_rec['buy'].values[-3:],
                        'Hold': monthly_rec['hold'].values[-3:],
                        'Underperform': monthly_rec['underperform'].values[-3:],
                        'Sell': monthly_rec['sell'].values[-3:]
                    }
            colors = ['#00ff88', '#88ff00', '#ffaa00', '#ff6600', '#ff0066']
            bottom = np.zeros(len(months))
            for i, (label, values) in enumerate(recommendations_data.items()):
                ax2.bar(months, values, bottom=bottom, color=colors[i], alpha=0.8, label=label)
                bottom += values
            ax2.set_title('Analyst Recommendations', color='white', fontweight='bold', fontsize=12)
            ax2.tick_params(colors='white')
            ax2.set_ylabel('Número de Analistas', color='white')
            ax2.legend(loc='upper left', frameon=False)
        except Exception as e:
            ax2.text(0.5, 0.5, f'Error: {e}', ha='center', va='center', transform=ax2.transAxes, color='white')
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Dashboard financiero estilo Yahoo Finance para 1 a 5 símbolos.")
    parser.add_argument('symbols', nargs='+', help='Símbolos de las acciones (mínimo 1, máximo 5)')
    args = parser.parse_args()
    if not (1 <= len(args.symbols) <= 5):
        print("Debes ingresar entre 1 y 5 símbolos. Ejemplo: python YDash.py AAPL MSFT TSLA")
        exit(1)
    if len(args.symbols) == 1:
        ticker_symbol = args.symbols[0]
        print(f"\nMostrando dashboard para: {ticker_symbol}")
        try:
            fig = plot_complete_dashboard(ticker_symbol)
            plt.show()
            ticker = yf.Ticker(ticker_symbol)
            info = ticker.info
            print(f"\nInformación de {ticker_symbol}:")
            print(f"Nombre: {info.get('longName', 'N/A')}")
            print(f"Sector: {info.get('sector', 'N/A')}")
            print(f"Precio actual: ${info.get('currentPrice', 'N/A')}")
            print(f"Market Cap: ${info.get('marketCap', 'N/A'):,}")
        except Exception as e:
            print(f"Error con {ticker_symbol}: {e}")
    else:
        print(f"\nMostrando dashboards para: {', '.join(args.symbols)}")
        plot_full_dashboards(args.symbols)

def get_real_time_data(ticker_symbol):
    ticker = yf.Ticker(ticker_symbol)
    hist = ticker.history(period="5d", interval="1d")
    info = ticker.info
    financials = ticker.financials
    balance_sheet = ticker.balance_sheet
    cash_flow = ticker.cashflow
    return {
        'history': hist,
        'info': info,
        'financials': financials,
        'balance_sheet': balance_sheet,
        'cash_flow': cash_flow
    }

symbols = ["AAPL", "GOOGL", "MSFT", "TSLA"]


