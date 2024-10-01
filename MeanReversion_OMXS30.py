"""
Denna kod implementerar en backtesting-strategi för att handla aktier på OMXS30-börsen
baserat på tekniska indikatorer såsom Bollingerband och SMA200. Strategin går enbart lång
(köper aktier) när aktiekursen är under det nedre Bollingerbandet och över SMA200.
Positioner hålls i maximalt 5 dagar eller tills en stop-loss-nivå på 2% från köpkursen nås.
Efter backtestet sammanfattas avkastningen och resultaten visualiseras i en equity curve.
"""
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# Lista över OMXS30-aktier
OMXS30_tickers = [
    "ABB.ST", "ALFA.ST", "ASSA-B.ST", "ATCO-B.ST", "AZN.ST", "BOL.ST", "EQT.ST", "ERIC-B.ST", "ESSITY-B.ST",
    "EVO.ST", "GETI-B.ST", "HEXA-B.ST", "HM-B.ST", "HUSQ-B.ST", "INVE-B.ST", "KINV-B.ST", "LATO-B.ST", "LIFCO-B.ST",
    "LUND-B.ST", "NDA-SE.ST", "NIBE-B.ST", "PEAB-B.ST", "SAND.ST", "SCA-B.ST", "SEB-A.ST", "SHB-A.ST", "SKF-B.ST",
    "SINCH.ST", "SWED-A.ST", "TEL2-B.ST", "TELIA.ST", "TREL-B.ST", "VOLV-B.ST"]

# Funktion för att backtesta en enskild aktie
def backtest_strategy(symbol, initial_capital):
    data = yf.download(symbol, start="2000-01-01", end="2024-06-19")

    # Beräkna Bollingerband och MA200
    data['SMA20'] = data['Close'].rolling(window=20).mean()
    data['SMA200'] = data['Close'].rolling(window=200).mean()
    data['stddev'] = data['Close'].rolling(window=20).std()
    data['UpperBB'] = data['SMA20'] + (data['stddev'] * 2)
    data['LowerBB'] = data['SMA20'] - (data['stddev'] * 2)

    # Implementera köpregler och säljregler med trendfilter och stop-loss på 2% av kapitalet
    data['LongEntry'] = (data['Close'] < data['LowerBB']) & (data['Close'] > data['SMA200'])

    # Initialisera portfölj
    position = 0  # Antal aktier köpta
    portfolio_value = initial_capital  # Portföljvärde
    trades = []  # Lista för att hålla reda på köp- och säljdatum
    days_in_position = 0  # Antal dagar i position

    equity_curve_df = pd.DataFrame(columns=["Portfolio Value"], index=data.index)
    for index, row in data.iterrows():
        if row['LongEntry'] and position == 0:
            # Köp aktier
            position_value = portfolio_value / 10  # 10% av totala kapitalet
            position = position_value // row['Close']
            buy_price = row['Close']
            stop_loss_price = buy_price * 0.98  # 2% risk av köpkursen
            days_in_position = 0  # Återställ räknare för antal dagar
            trades.append({'Symbol': symbol, 'Entry Date': index, 'Entry Price': buy_price, 'Position': 'Long',
                           'Stop Loss': stop_loss_price})
        elif position > 0:
            days_in_position += 1  # Räkna upp antal dagar i position
            # Sälj om någon av följande villkor uppfylls:
            if row['Close'] <= trades[-1]['Stop Loss'] or days_in_position >= 5:
                # Sälj om aktien når stop-loss-nivån eller efter 5 dagar
                portfolio_value += position * (row['Close'] - buy_price)
                trades[-1]['Exit Date'] = index
                trades[-1]['Exit Price'] = row['Close']
                trades[-1]['Return'] = (row['Close'] - buy_price) / buy_price
                position = 0

        # Uppdatera equity kurvan för varje dag
        equity_curve_df.loc[index, 'Portfolio Value'] = portfolio_value

    trades_df = pd.DataFrame(trades)
    return trades_df, portfolio_value, data, equity_curve_df


# Sammanfatta resultat för alla aktier i OMXS30
initial_capital = 100000
all_trades = []
combined_equity_curve_df = pd.DataFrame()

for ticker in OMXS30_tickers:
    trades_df, final_portfolio_value, data, equity_curve_df = backtest_strategy(ticker, initial_capital)
    all_trades.append(trades_df)
    combined_equity_curve_df = pd.concat([combined_equity_curve_df, equity_curve_df])

# Ta bort dubbletter i indexet innan resampling
combined_equity_curve_df = combined_equity_curve_df.loc[~combined_equity_curve_df.index.duplicated(keep='first')]

# Fyll datumluckor i equity curve och droppa NaN-värden
combined_equity_curve_df = combined_equity_curve_df.resample('D').ffill().dropna()

# Skriv ut trade-detaljer för varje aktie
all_trades_df = pd.concat(all_trades, ignore_index=True)
pd.set_option('display.max_columns', None)
print(all_trades_df)

# Beräkna total avkastning för alla trades
total_return = all_trades_df['Return'].sum()
num_trades = len(all_trades_df)
num_wins = len(all_trades_df[all_trades_df['Return'] > 0])
num_losses = num_trades - num_wins
win_rate = num_wins / num_trades if num_trades > 0 else 0

print(f"Total Return: {total_return:.2f}")
print(f"Number of Trades: {num_trades}")
print(f"Win Rate: {win_rate:.2%}")
print(f"Number of Wins: {num_wins}")
print(f"Number of Losses: {num_losses}")

# Plotta equity-kurvan
plt.figure(figsize=(12, 6))
plt.plot(combined_equity_curve_df.index, combined_equity_curve_df["Portfolio Value"], label='Equity Curve')
plt.xlabel('Date')
plt.ylabel('Portfolio Value (SEK)')
plt.title(f'Equity Curve of the Bollinger Band Strategy on OMXS30 Stocks (Long only)')
plt.legend()
plt.grid(True)
plt.show()
