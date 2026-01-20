<div align="center">
    <img src="https://avatars.githubusercontent.com/u/235483245?u=f1859a88b3e3c9d1b5a5857079c364d3746a1ad9" width="200"/>
    <h1>
       Trader Charts
    </h1>
    <h3>
        Trader Charts is a tool for performing technical analysis with interactive charts. It allows users to visualize stock data or other asset data depending on what the data providers supply, and to apply technical indicators to analyze price trends 
    </h3>
   <h5>
      * One charting tool to rule them all *
   </h5>
</div>

---

![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)
![Selenium](https://img.shields.io/badge/Selenium-4.36.0-4B32C3?logo=selenium&logoColor=white)
![PyMongo](https://img.shields.io/badge/PyMongo-4.15.3-589636?logo=mongodb&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-2.3.3-E3FF00?logo=pandas&logoColor=white)
![Python Dotenv](https://img.shields.io/badge/python--dotenv-1.0.0-blue?logo=python&logoColor=white)
![Feedparser](https://img.shields.io/badge/feedparser-6.0.0-orange?logoColor=white)
![BeautifulSoup4](https://img.shields.io/badge/BeautifulSoup4-4.12.0-ff69b4?logo=python&logoColor=white)
![TextBlob](https://img.shields.io/badge/TextBlob-0.17.0-ff6600?logo=python&logoColor=white)
![KeyBERT](https://img.shields.io/badge/KeyBERT-0.8.0-6f42c1?logo=python&logoColor=white)
![Black](https://img.shields.io/badge/Black-23.0.0-FDE2C6?logo=python&logoColor=white)
![Isort](https://img.shields.io/badge/Isort-5.12.0-B1E0FF?logo=python&logoColor=white)
![Ruff](https://img.shields.io/badge/Ruff-0.1.0-61DAFB?logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-C0C0C0)
[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2FTraderCharts%2Ftrader-charts-data-collector.svg?type=shield)](https://app.fossa.com/projects/git%2Bgithub.com%2FTraderCharts%2Ftrader-charts-data-collector?ref=badge_shield)

---

## Trader Charts Data Collector - Overview

The **Data Collector** is a Python tool that gathers and processes stock or asset data from various providers.  
Using Selenium, PyMongo, and Pandas, it stores cleaned and structured data in MongoDB for use by the backend and frontend.  
[See frontend →](https://github.com/TraderCharts/trader-charts-frontend) | [See backend →](https://github.com/TraderCharts/trader-charts-backend)

---

🚀 **Want to contribute?**

We welcome collaborators who wish to contribute and help enhance this trading tool. Feel free to reach out to the maintainers to get involved.

---

### Installing project

Trader Charts Data Collector is based on **Selenium**, and use **Panda** and **MongoDB** database.

1.  Set environment variables on .env.local file

2.  Create virtual environemnt

         $ python -m venv .venv

3.  Activate virtual environemnt _.venv_

         $ source .venv/bin/activate

4.  Install Python modules

         $ python -m pip install -e .

5.  Available main modules

         # Historical data
         $ python -m mains.main_collect_historical_data

         # RSS feeds
         $ python -m mains.main_collect_rss_feeds

         # Train sentumental analysis model for financial RSS feeds
         $ python -m mains.main_finetune_sentiment_model

         # Process sentiment analyis RSS feeds
         $ python -m mains.main_analyze_sentiment_model_rss_feeds

         # Process topic RSS feeds
         $ python -m mains.main_analyze_topic_model_rss_feeds

6.  Deactivate virtual environemnt _.venv_

         $ deactivate

### Linter and Quality Validations

To ensure best practices and maintain code quality, you can run the following scripts:

-   Check for issues

           $ ./scripts/check_code.sh

-   Fix issues

           $ ./scripts/fix-code.sh

## Required Env Variables

Create `.env.development.local` file, and include all the following:

         MONGO_URI=[string]
         MONGO_DB_NAME=[string]
         MONGO_COLLECTION=[string]


## License
[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2FTraderCharts%2Ftrader-charts-data-collector.svg?type=large)](https://app.fossa.com/projects/git%2Bgithub.com%2FTraderCharts%2Ftrader-charts-data-collector?ref=badge_large)