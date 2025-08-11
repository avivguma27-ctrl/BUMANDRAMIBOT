import yfinance as yf
import feedparser
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import logging
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

# ============================== #
# הגדרות ישירות בקוד - הכנס את הפרטים שלך כאן
TARGET_EMAILS = "avivguma12@gmail.com,swrrmy028@gmail.com"  # מי מקבל דוח
EMAIL_USER = "avivguma12@gmail.com"                          # מייל שולח
EMAIL_PASS = "fxgqtmhqcrszrzyj"                             # סיסמת אפליקציה (App Password)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

EMAIL_LIST = [email.strip() for email in TARGET_EMAILS.split(",")]

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

TICKERS = [
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
]

analyzer = SentimentIntensityAnalyzer()

def get_stock_data(ticker):
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

def get_news_sentiment(ticker, max_items=5):
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

def score_stock(stock_data, sentiment):
    score = 0.0

    change_pct = stock_data['change_pct']
    today_volume = stock_data['today_volume']
    avg_volume = stock_data['avg_volume']
    ma10 = stock_data['ma10']
    ma50 = stock_data['ma50']

    # 1. ניקוד על שינוי אחוזי במחיר (מקסימום 30)
    abs_change = min(abs(change_pct), 10)
    score += (abs_change / 10) * 30

    # 2. נפח מסחר (מקסימום 25)
    volume_ratio = today_volume / avg_volume if avg_volume > 0 else 0
    if volume_ratio > 1:
        score += min((volume_ratio - 1) / 2 * 25, 25)

    # 3. מגמת ממוצעים נעים (מקסימום 15)
    if ma10 > ma50:
        score += 15
    else:
        score += 5

    # 4. סנטימנט חדשות (מקסימום 20)
    sentiment_score = max(min((sentiment + 1) / 2, 1), 0)
    score += sentiment_score * 20

    # תיקון ניקוד בין 0 ל-100
    if score < 0:
        score = 0
    if score > 100:
        score = 100

    return round(score, 2)

def send_email(subject, body, to_email, html=False):
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = EMAIL_USER
        msg["To"] = to_email

        part = MIMEText(body, "html" if html else "plain")
        msg.attach(part)

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASS)
            server.sendmail(EMAIL_USER, to_email, msg.as_string())

        logging.info(f"Email sent successfully to {to_email}")

    except Exception as e:
        logging.error(f"Failed to send email to {to_email}: {e}")

def main():
    logging.info("Start processing tickers...")
    messages = []

    for ticker in TICKERS:
        stock_data = get_stock_data(ticker)
        if not stock_data:
            continue

        sentiment = get_news_sentiment(ticker)
        score = score_stock(stock_data, sentiment)

        if score >= 70:  # רק מניות עם ניקוד מעל 70 בדוח
            messages.append(
                f"<b>📈 מניה:</b> {ticker}<br>"
                f"<b>מחיר סגירה:</b> {stock_data['today_close']:.2f}$<br>"
                f"<b>שינוי יומי:</b> {stock_data['change_pct']:.2f}%<br>"
                f"<b>נפח היום:</b> {stock_data['today_volume']}<br>"
                f"<b>נפח ממוצע 30 יום:</b> {stock_data['avg_volume']:.0f}<br>"
                f"<b>MA10:</b> {stock_data['ma10']:.2f}<br>"
                f"<b>MA50:</b> {stock_data['ma50']:.2f}<br>"
                f"<b>סנטימנט:</b> {sentiment:.2f}<br>"
                f"<b>ניקוד כולל:</b> {score}<br>"
                f"<hr>"
            )

    body = "<h2>דוח הזדמנויות מניות</h2>" + ("<br>".join(messages) if messages else "<p>אין הזדמנויות כרגע.</p>")

    subject = f"דוח הזדמנויות מניות - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

    for email in EMAIL_LIST:
        send_email(subject, body, email, html=True)

    logging.info("Finished sending emails.")

if __name__ == "__main__":
    main()
