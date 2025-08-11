import os
import yfinance as yf
import feedparser
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import requests
import concurrent.futures
import logging
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from dotenv import load_dotenv

# ============================== #
# טעינת משתני סביבה
load_dotenv()

QUIVER_API_KEY = os.getenv("QUIVER_API_KEY")
TARGET_EMAILS = os.getenv("TARGET_EMAILS")
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))

if not all([QUIVER_API_KEY, TARGET_EMAILS, EMAIL_USER, EMAIL_PASS]):
    raise Exception("One or more environment variables are missing. Please check your .env file.")

EMAIL_LIST = [email.strip() for email in TARGET_EMAILS.split(",")]

# ============================== #
# הגדרת לוגינג
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ============================== #
# רשימת מניות (אפשר לצמצם לפי הצורך)
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


# ============================== #
# פונקציות

def get_stock_data(ticker: str) -> dict | None:
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
        logging.error(f"Error getting stock data for {ticker}: {e}")
        return None


def get_news_sentiment(ticker: str, max_items: int = 5) -> float:
    try:
        rss_url = f"https://news.google.com/rss/search?q={ticker}&hl=en-US&gl=US&ceid=US:en"
        feed = feedparser.parse(rss_url)
        sentiments = []
        for entry in feed.entries[:max_items]:
            vs = analyzer.polarity_scores(entry.title)
            sentiments.append(vs['compound'])
        return sum(sentiments) / len(sentiments) if sentiments else 0.0
    except Exception as e:
        logging.error(f"Error getting news sentiment for {ticker}: {e}")
        return 0.0


def get_politician_trades(ticker: str, api_key: str) -> int:
    try:
        url = f"https://api.quiverquant.com/beta/historical/congresstrading/{ticker}"
        headers = {"Authorization": f"Token {api_key}"}
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200 and r.json():
            buys = [t for t in r.json() if t["Transaction"] == "Purchase"]
            return len(buys)
    except Exception as e:
        logging.error(f"Error getting politician trades for {ticker}: {e}")
    return 0


def get_insider_trades(ticker: str, api_key: str) -> int:
    try:
        url = f"https://api.quiverquant.com/beta/historical/insidertrading/{ticker}"
        headers = {"Authorization": f"Token {api_key}"}
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200 and r.json():
            buys = [t for t in r.json() if t["Transaction"].lower() == "buy"]
            return len(buys)
    except Exception as e:
        logging.error(f"Error getting insider trades for {ticker}: {e}")
    return 0


def get_institutional_holding(ticker: str, api_key: str) -> int:
    try:
        url = f"https://api.quiverquant.com/beta/historical/institutionalownership/{ticker}"
        headers = {"Authorization": f"Token {api_key}"}
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200 and r.json():
            latest = r.json()[0]
            return latest.get("Shares", 0)
    except Exception as e:
        logging.error(f"Error getting institutional holdings for {ticker}: {e}")
    return 0


def score_stock(stock_data: dict, sentiment: float, pol_trades: int, insider_trades: int, inst_holding: int) -> float:
    score = 0.0

    change_pct = stock_data['change_pct']
    today_volume = stock_data['today_volume']
    avg_volume = stock_data['avg_volume']
    ma10 = stock_data['ma10']
    ma50 = stock_data['ma50']

    score += min(abs(change_pct) / 2, 5)  # עד 5 נקודות על שינוי מחירים
    if change_pct > 5:
        score += 2

    if today_volume > avg_volume * 1.5:
        score += 3

    score += 2 if ma10 > ma50 else -1

    if sentiment > 0.3:
        score += 3
    elif sentiment < -0.3:
        score -= 3

    if pol_trades > 0:
        score += 2

    if insider_trades > 0:
        score += 2

    if inst_holding > 1_000_000:
        score += 1

    return score


def send_email(subject: str, body: str, to_email: str, html: bool = False):
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = EMAIL_USER
        msg["To"] = to_email

        if html:
            part = MIMEText(body, "html")
        else:
            part = MIMEText(body, "plain")

        msg.attach(part)

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.sendmail(EMAIL_USER, to_email, msg.as_string())
        server.quit()

        logging.info(f"Email sent to {to_email}")
    except Exception as e:
        logging.error(f"Error sending email to {to_email}: {e}")


def process_ticker(ticker: str) -> str | None:
    stock_data = get_stock_data(ticker)
    if not stock_data:
        return None

    sentiment = get_news_sentiment(ticker)
    pol_trades = get_politician_trades(ticker, QUIVER_API_KEY)
    insider_trades = get_insider_trades(ticker, QUIVER_API_KEY)
    inst_holding = get_institutional_holding(ticker, QUIVER_API_KEY)

    score = score_stock(stock_data, sentiment, pol_trades, insider_trades, inst_holding)

    if score >= 7:
        return (
            f"<b>📈 מניה:</b> {ticker}<br>"
            f"<b>מחיר סגירה:</b> {stock_data['today_close']:.2f}$<br>"
            f"<b>שינוי יומי:</b> {stock_data['change_pct']:.2f}%<br>"
            f"<b>נפח היום:</b> {stock_data['today_volume']}<br>"
            f"<b>נפח ממוצע 30 יום:</b> {stock_data['avg_volume']:.0f}<br>"
            f"<b>MA10:</b> {stock_data['ma10']:.2f}<br>"
            f"<b>MA50:</b> {stock_data['ma50']:.2f}<br>"
            f"<b>סנטימנט:</b> {sentiment:.2f}<br>"
            f"<b>קניות פוליטיקאים:</b> {pol_trades}<br>"
            f"<b>קניות מנהלים בכירים:</b> {insider_trades}<br>"
            f"<b>אחזקות מוסדיים:</b> {inst_holding}<br>"
            f"<b>ניקוד:</b> {score:.2f}<br>"
            "<hr>"
        )
    return None


def main():
    logging.info("Start processing tickers...")
    messages = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(process_ticker, ticker): ticker for ticker in TICKERS}
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
                if result:
                    messages.append(result)
            except Exception as e:
                ticker = futures[future]
                logging.error(f"Error processing ticker {ticker}: {e}")

    if not messages:
        body = "<p>אין הזדמנויות כרגע.</p>"
    else:
        body = "<h2>דוח הזדמנויות מניות משודרג</h2>" + "".join(messages)

    subject = f"דוח הזדמנויות מניות משודרג - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

    for email in EMAIL_LIST:
        send_email(subject, body, email, html=True)

    logging.info("Finished sending emails.")


if __name__ == "__main__":
    main()
