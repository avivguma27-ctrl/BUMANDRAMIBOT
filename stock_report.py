import os
import yfinance as yf
import feedparser
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from send_email import send_email
import requests

# ==============================
# הגדרות
# ==============================
TICKERS = list(set([
    "AAPL","MSFT","AMZN","GOOG","GOOGL","FB","TSLA","BRK.B","BRK.A","JNJ",
    "V","WMT","JPM","UNH","NVDA","HD","PG","MA","DIS","BAC",
    "XOM","PYPL","VZ","ADBE","CMCSA","NFLX","T","KO","PFE","NKE",
    "MRK","INTC","PEP","ABT","CVX","CSCO","ORCL","CRM","MCD","ACN",
    "COST","WFC","MDT","TXN","LLY","NEE","HON","QCOM","BMY","LOW",
    "IBM","LIN","SBUX","AMGN","CAT","GE","BKNG","CHTR","USB","INTU",
    "BLK","TMO","MO","MMM","DE","ISRG","ZTS","SPGI","CI","SYK",
    "PLD","LMT","BDX","FIS","CME","GILD","ADI","CB","VRTX","EW",
    "TJX","ATVI","CL","SHW","ICE","MET","GM","SO","ITW","GD",
    "CCI","MCO","EL","NOC","DUK","F","APD","ECL","AON","COF",
    "BSX","PGR","EMR","HCA","AIG","ALL","DD","ADP","REGN","NSC",
    "KLAC","ROST","ADSK","CTSH","EXC","MNST","A","LRCX","MAR","EA",
    "ETN","BIIB","CERN","APH","MCK","MET","MPC","EOG","VLO","KMB",
    "FISV","DHR","BK","BDX","DG","MMC","WBA","TEL","XEL","ORLY",
    "HSY","AFL","KMI","HES","RMD","AEE","ZBRA","VAR","GLW","CINF",
    "FFIV","HOLX","NUE","WRB","CTAS","OKE","PH","AEP","HIG","PSA",
    "NTRS","MTD","TRV","VRSK","STZ","EVRG","WLTW","ABMD","XYL","HWM",
    "PEG","XLNX","LVS","CAG","ESS","XRX","ALGN","SNPS","FLT","MHK",
    "SWK","CBOE","ALB","SRE","ANSS","FTNT","DLR","FMC","TDG","PPL",
    "CNC","HAS","GL","MRO","BKR","NWSA","HLT","MSCI","D","DDOG","DOV",
    "ZBH","TT","WEC","GPN","MGM","XL","HST","TRMB","K","CTXS","COO",
    "GRMN","HPE","ED","PBCT","LYB","ROK","VTR","VRSN","LDOS","NTAP",
    "DTE","INFO","CHRW","EFX","CTRA","MCK","PHM","FRC","SWKS","MTB",
    "OKE","XYL","PEG","PNC","EIX","EBAY","CMA","ALXN","DGX","HBI","LHX",
    "BAX","TTWO","AKAM","ODFL","PXD","WDC","LEN","SYY","STX",
    "CDNS","ALGN","VMC","HSIC","PAYX","MTCH","CPRT","L","CE","KEYS",
    "IT","DHI","CAG","RSG","WAB","HUM","DXC","RJF","ES","NDAQ","WMB",
    "CLX","COG","FANG","JBHT","IRM","NWL","MKC","IEX","MCHP","SIVB",
    "MOS","BWA","MAS","SNA","TXT","VFC","EXPE","ULTA","NLOK","OMC","RCL",
    "GWW","LH","CMS","PAYC","MKTX","DLTR","CNP","PPG","ANET","DRE",
    "KSU","KIM","NWS","PKI","ARE","BEN","BKR","WY","LNT","GPC","AIZ",
    "AVY","PPL","WELL","VAR","PSX","APA","IDXX","WRK","AMCR","PEAK",
    "AOS","WYNN","BXP","FLS","JKHY","LKQ","FAST","TDG","CFG","ADM",
    "BLL","WM","TROW","AVB","O","NLSN","IRM","BXP","PRGO","ABMD","HOLX",
    "ZBRA","NWL","BBY","DD","DOV","PHM","AMT","LEN","HWM","AVB",
    "BABA","TCEHY","PDD","JD","SHOP","SQ","COIN","RIVN","LCID","BYDDY",
    "NIO","XPEV","LI","PLTR","SNOW","NET","CRWD","ZS","OKTA","SMCI",
    "ARM","TSM","ASML","AMD","MU","ON","MRVL","ENPH","SEDG","RUN",
    "BLDP","FCEL","SPWR","DUK","BA","LUV","UAL","DAL","RYAAY","EADSY",
    "CCL","RCL","NCLH","UBER","LYFT","ABNB","EXPE","MAR","HLT","MELI",
    "SE","GRAB","YNDX",
    "NVAX", "INCY", "EDIT", "BLUE", "ACAD", "ALNY", "SGEN", "CELG",
    "BGNE", "DXCM", "MGLN", "NBIX", "XOMA", "VTRS", "VSTM", "VIVO",
    "ZS", "ZM", "DOCU", "TEAM", "TWLO", "MDB", "FVRR", "UPST", "ROKU",
    "AFRM", "RBLX", "U", "PATH", "HOOD", "VTI", "VOO", "SPY", "IVV",
    "QQQ", "DIA", "IWM", "EEM", "VNQ", "XLF", "XLK", "XLY", "XLC",
    "XLI", "XLE", "XLV", "XLB", "XLU", "XBI", "ARKK", "ARKG", "ARKW",
    "ARKF", "ARKQ", "ARKX", "VGT", "VHT", "VFH", "VPU", "VDE", "VDC",
    "VOX", "VCR", "VIS", "VO", "VB", "VBR", "VOE", "VOT", "VUG", "VTV",
    "VYM", "SCHD", "DGRO", "VIG", "DVY", "SPHD", "SPYD", "HDV", "SDY",
    "NOBL", "PFF", "BND", "AGG", "LQD", "HYG", "JNK", "EMB", "MUB",
    "TIP", "GOVT", "SHY", "IEF", "TLT", "GLD", "SLV", "DBC", "USO",
    "UNG", "UUP", "FXE", "FXY"
]))

analyzer = SentimentIntensityAnalyzer()

# ==============================
# פונקציות
# ==============================

def get_stock_data(ticker):
    """משיכת נתונים טכניים על המניה"""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="60d")
        if len(hist) < 60:
            return None

        today_close = hist['Close'][-1]
        yesterday_close = hist['Close'][-2]
        change_pct = ((today_close - yesterday_close) / yesterday_close) * 100
        today_volume = hist['Volume'][-1]
        avg_volume = hist['Volume'][-30:].mean()
        ma10 = hist['Close'][-10:].mean()
        ma50 = hist['Close'][-50:].mean()

        return {
            "ticker": ticker,
            "today_close": today_close,
            "change_pct": change_pct,
            "today_volume": today_volume,
            "avg_volume": avg_volume,
            "ma10": ma10,
            "ma50": ma50
        }
    except Exception as e:
        print(f"Error getting stock data for {ticker}: {e}")
        return None


def get_news_sentiment(ticker, max_items=5):
    """משיכת סנטימנט חדשות מגוגל ניוז"""
    try:
        rss_url = f"https://news.google.com/rss/search?q={ticker}&hl=en-US&gl=US&ceid=US:en"
        feed = feedparser.parse(rss_url)
        sentiments = []
        for entry in feed.entries[:max_items]:
            vs = analyzer.polarity_scores(entry.title)
            sentiments.append(vs['compound'])
        return sum(sentiments) / len(sentiments) if sentiments else 0
    except Exception as e:
        print(f"Error getting news sentiment for {ticker}: {e}")
        return 0


def get_politician_trades(ticker):
    """בדיקת קניות/מכירות של פוליטיקאים (מקור: QuiverQuant API)"""
    try:
        url = f"https://api.quiverquant.com/beta/historical/congresstrading/{ticker}"
        headers = {"Authorization": f"Token {os.getenv('QUIVER_API_KEY')}"}
        r = requests.get(url, headers=headers)
        if r.status_code == 200 and r.json():
            buys = [t for t in r.json() if t["Transaction"] == "Purchase"]
            return len(buys)
    except Exception as e:
        print(f"Error getting politician trades for {ticker}: {e}")
    return 0


def get_insider_trades(ticker):
    """בדיקת קניות של מנהלים בכירים (מקור: QuiverQuant API)"""
    try:
        url = f"https://api.quiverquant.com/beta/historical/insidertrading/{ticker}"
        headers = {"Authorization": f"Token {os.getenv('QUIVER_API_KEY')}"}
        r = requests.get(url, headers=headers)
        if r.status_code == 200 and r.json():
            buys = [t for t in r.json() if t["Transaction"] == "Buy"]
            return len(buys)
    except Exception as e:
        print(f"Error getting insider trades for {ticker}: {e}")
    return 0


def get_institutional_holding(ticker):
    """בדיקת אחזקות מוסדיים (מקור: QuiverQuant API)"""
    try:
        url = f"https://api.quiverquant.com/beta/historical/institutionalownership/{ticker}"
        headers = {"Authorization": f"Token {os.getenv('QUIVER_API_KEY')}"}
        r = requests.get(url, headers=headers)
        if r.status_code == 200 and r.json():
            latest = r.json()[0]
            return latest.get("Shares", 0)
    except Exception as e:
        print(f"Error getting institutional holdings for {ticker}: {e}")
    return 0


def score_stock(stock_data, sentiment, pol_trades, insider_trades, inst_holding):
    """חישוב ניקוד כולל"""
    score = 0

    # שינוי מחיר חד
    if abs(stock_data['change_pct']) > 3:
        score += 5
    if stock_data['change_pct'] > 5:
        score += 3

    # נפח מסחר גבוה
    if stock_data['today_volume'] > stock_data['avg_volume'] * 1.5:
        score += 3

    # מגמה חיובית
    if stock_data['ma10'] > stock_data['ma50']:
        score += 2
    else:
        score -= 1

    # סנטימנט חיובי
    if sentiment > 0.3:
        score += 3
    elif sentiment < -0.3:
        score -= 3

    # קניות פוליטיקאים
    if pol_trades > 0:
        score += 2

    # קניות מנהלים בכירים
    if insider_trades > 0:
        score += 2

    # אחזקות מוסדיים גבוהות
    if inst_holding > 1_000_000:
        score += 1

    return score


def main():
    target_emails = os.getenv("TARGET_EMAILS")
    if not target_emails:
        print("ERROR: TARGET_EMAILS environment variable is not set.")
        return

    email_list = [e.strip() for e in target_emails.split(",")]

    messages = []
    for ticker in TICKERS:
        stock_data = get_stock_data(ticker)
        if not stock_data:
            continue

        sentiment = get_news_sentiment(ticker)
        pol_trades = get_politician_trades(ticker)
        insider_trades = get_insider_trades(ticker)
        inst_holding = get_institutional_holding(ticker)

        score = score_stock(stock_data, sentiment, pol_trades, insider_trades, inst_holding)

        if score >= 7:
            msg = (
                f"📈 מניה: {ticker}\n"
                f"מחיר סגירה: {stock_data['today_close']:.2f}$\n"
                f"שינוי יומי: {stock_data['change_pct']:.2f}%\n"
                f"נפח היום: {stock_data['today_volume']}\n"
                f"נפח ממוצע 30 יום: {stock_data['avg_volume']:.0f}\n"
                f"MA10: {stock_data['ma10']:.2f}\n"
                f"MA50: {stock_data['ma50']:.2f}\n"
                f"סנטימנט: {sentiment:.2f}\n"
                f"קניות פוליטיקאים: {pol_trades}\n"
                f"קניות מנהלים בכירים: {insider_trades}\n"
                f"אחזקות מוסדיים: {inst_holding}\n"
                f"ניקוד: {score}\n"
                "-------------------------"
            )
            messages.append(msg)

    body = "\n\n".join(messages) if messages else "אין הזדמנויות כרגע."

    for email in email_list:
        send_email("דוח הזדמנויות מניות משודרג", body, email)


if __name__ == "__main__":
    main()
