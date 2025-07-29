# 🏡 DuProprio Real Estate Scraper

This Python script scans listings on [duproprio.com](https://duproprio.com) in Quebec and alerts you by email when a property is listed significantly below its municipal value — a potential deal!

---

## 📌 Features

- ✅ Automates real estate search using Selenium
- ✅ Detects underpriced properties based on municipal evaluation
- ✅ Sends email notifications when criteria (configurable) are met 
- ✅ Supports headless mode (runs silently in the background)
- ✅ Avoids revisiting previously checked listings
- ✅ Refreshes every XX (configurable) minutes
- ✅ Easy configuration via `.env` file

---

## ⚙️ Setup Instructions

### 1. Clone or download this repository

```bash
git clone https://github.com/yourusername/duproprio-scraper.git
cd duproprio-scraper
```

### 2. Install dependencies

```bash
pip install selenium python-dotenv
```

### 3. Create a `.env` file

In the root folder, create a `.env` file and add:

```
EMAIL_SENDER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
EMAIL_RECEIVER=recipient_email@gmail.com
CHROMEDRIVER_PATH=C:\Path\To\chromedriver.exe
CHROME_BINARY_PATH=C:\Path\To\chrome.exe
PRICE_TO_ASSESSMENT_RATIO=0.9
REFRESH_INTERVAL_SECONDS=900
```

> 💡 **NOTE:** If using Gmail with 2FA, generate an **App Password**:  
> https://support.google.com/accounts/answer/185833

### 4. (Optional) Enable headless mode

Uncomment this line in `duproprio_scraper.py` if you want the browser to run in the background:
```python
options.add_argument('--headless=new')
```

---

## ▶️ Running the Script

```bash
python duproprio_scraper.py
```

### What it does:

- Opens the DuProprio search results page
- Iterates through each listing
- Opens and analyzes each listing page
- Compares asking price to municipal assessment
- Sends email alert if asking price is **< configurable PRICE_TO_ASSESSMENT_RATIO (default 0.9)**
- Tracks last visited listing to avoid reprocessing
- Restarts scraping every XX minutes **< configurable REFRESH_INTERVAL_SECONDS (default 900)**

---

## 📁 Output Files

- `list.txt` — Stores all matching listing URLs found.
- `lastVisited.txt` — Keeps track of the most recently processed listing to avoid duplicates on the next run.

To restart the script fresh:
```bash
del list.txt lastVisited.txt  # or delete manually
```

---

## 📌 Example Email Alert

```
Subject: 🏠 Property Found Under Market Value!

URL: https://duproprio.com/en/123456
Evaluation: 400000.0
Price: 300000.0
Ratio: 0.75
```

---

## ✅ Requirements

- Python 3.8+
- Google Chrome installed
- ChromeDriver compatible with your Chrome version
