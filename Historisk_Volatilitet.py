"""
Denna kod beräknar den historiska volatiliteten för ett antal aktier baserat på deras stängningspriser.
Volatiliteten beräknas genom att först hämta historisk data från Yahoo Finance via `yfinance` och sedan använda
logaritmiska avkastningar för att beräkna standardavvikelsen över ett definierat tidsfönster. Resultatet
är den årliga historiska volatiliteten för varje aktie, och resultaten lagras i en DataFrame. Strategin tillämpar
olika tidsramar, och en rullande standardavvikelse används för att beräkna volatiliteten.
"""

import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
def calculate_historical_volatility(prices, length=10, annual=365, timeframe='daily'):
    # Beräkna logaritmiska avkastningar
    log_returns = np.log(prices / prices.shift(1))

    # Standardavvikelse på logaritmiska avkastningar
    stdev_log_returns = log_returns.rolling(window=length).std().iloc[-1]

    # Justering baserat på tidsram
    if timeframe == 'daily':
        per = 1
    elif timeframe == 'weekly':
        per = 5
    elif timeframe == 'monthly':
        per = 21
    else:
        raise ValueError("Unsupported timeframe")

    # Beräkna historisk volatilitet
    hv = 100 * stdev_log_returns * np.sqrt(annual / per)

    return hv


# Lista över aktiesymboler
tickers = [
    "AAK.ST", "ACAST.ST", "AKBM.OL", "ALFA.ST", "AMBEA.ST", "ATCO-B.ST",
    "BERG-B.ST", "BINV.ST", "EAST.ST", "ENEA.ST", "HTRO.ST",
    "INWI.ST", "ISOFOL.ST", "LIN", "MSFT", "ODF.OL", "PEAB-B.ST",
    "PENG-B.ST", "PREC.ST", "SEB-A.ST", "SF.ST", "SHOT.ST", "SU.TO",
    "SWED-A.ST", "TIGO-SDB.ST", "TREL-B.ST", "VBG-B.ST", "XSPRAY.ST"
]

# Datumintervall: senaste två åren
end_date = datetime.now()
start_date = end_date - timedelta(days=365 * 2)

# Lista för att lagra resultat
volatility_data = []

for ticker in tickers:
    try:
        # Hämta data från yfinance
        data = yf.download(ticker, start=start_date, end=end_date, interval='1d')

        # Kontrollera om data hämtades korrekt
        if not data.empty:
            # Kontrollera om tillräckligt med data finns för beräkning
            if len(data) >= 10:  # För att matcha Pine Script's `length`
                latest_volatility = calculate_historical_volatility(data['Close'], length=10, annual=365,
                                                                    timeframe='daily')
            else:
                latest_volatility = np.nan
        else:
            latest_volatility = np.nan

        # Lägg till i listan
        volatility_data.append({'Ticker': ticker, 'Historical Volatility': latest_volatility})

    except Exception as e:
        volatility_data.append({'Ticker': ticker, 'Historical Volatility': np.nan})

# Konvertera listan till DataFrame
volatility_data_df = pd.DataFrame(volatility_data)

# Visa resultat
print(volatility_data_df)
