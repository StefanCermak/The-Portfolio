
import stockdata

def sektor_report(eigene_ticker_liste):
    """
    Erstellt einen Bericht, der eigene Aktien nach Sektoren gruppiert und für jeden Sektor
    3 weitere Peer-Aktien hinzufügt.

    :param eigene_ticker_liste: Liste eigener Aktien-Ticker
    :return: Dictionary mit Sektoren als Keys und Ticker-Listen als Values
    """
    # Schritt 1: Eigene Aktien nach Sektor gruppieren
    sector_dict = {}  # z.B. {'Technology': {'AAPL': {}, 'MSFT': {}}, ...}
    for ticker in eigene_ticker_liste:
        sector = stockdata.get_industry_and_sector(ticker)[1]  # Index 1 ist der Sektor
        if sector not in sector_dict:
            sector_dict[sector] = {}
        sector_dict[sector][ticker] = {}

    # schritt 2: füge peers hinzu
    for sector in sector_dict:
        peer_tickers = stockdata.get_peers_for_sector(sector, exclude=list(sector_dict[sector].keys()), count=3)
        for peer in peer_tickers:
            if peer not in sector_dict[sector]:
                sector_dict[sector][peer] = {}

    # Schritt 3: Hole zusätzliche Daten für alle Ticker
    for sector in sector_dict:
        for ticker, data in sector_dict[sector].items():
            # Hole weitere Kennzahlen für Peer-Vergleich
            try:
                ticker_obj = stockdata.yf.Ticker(ticker)
                info = ticker_obj.info
                data['fiftyTwoWeekHigh'] = info.get('fiftyTwoWeekHigh')
                data['fiftyTwoWeekLow'] = info.get('fiftyTwoWeekLow')
                data['trailingPE'] = info.get('trailingPE')
                data['forwardPE'] = info.get('forwardPE')
                data['marketCap'] = info.get('marketCap')
            except Exception:
                data['fiftyTwoWeekHigh'] = None
                data['fiftyTwoWeekLow'] = None
                data['trailingPE'] = None
                data['forwardPE'] = None
                data['marketCap'] = None
            # Hole aktuellen Kurs
            day_data = stockdata.get_stock_day_data(ticker)
            if day_data:
                data['current_price'] = day_data.get('current_price')
                data['currency'] = day_data.get('currency')
                data['rate'] = day_data.get('rate')
                data['high'] = day_data.get('high')
                data['low'] = day_data.get('low')
                data['volume'] = day_data.get('volume')
                data['close'] = day_data.get('close')
                data['change_percent'] = day_data.get('change_percent')
            else:
                data['current_price'] = None
                data['currency'] = None
                data['rate'] = None
                data['high'] = None
                data['low'] = None
                data['volume'] = None
                data['close'] = None
                data['change_percent'] = None
    return sector_dict
