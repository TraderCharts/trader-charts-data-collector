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
![License](https://img.shields.io/badge/License-MIT-C0C0C0)

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

5.  Execute Python module _app_

         $  python -m app

6.  Deactivate virtual environemnt _.venv_

         $ deactivate

## Required Env Variables

Create `.env.development.local` file, and include all the following:

         MONGO_URI=[string]
         MONGO_DB_NAME=[string]
         MONGO_COLLECTION=[string]
