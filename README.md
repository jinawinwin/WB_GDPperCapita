# World Bank GDP per Capita Dashboard

A GitHub Pages dashboard using World Bank World Development Indicators (WDI).

## Indicators
- **Real GDP per capita, constant 2015 US$** — `NY.GDP.PCAP.KD`
- **Real GDP per capita growth (%)** — `NY.GDP.PCAP.KD.ZG`
- **GDP per capita, current US$** — `NY.GDP.PCAP.CD`

Real values are suitable for long-run comparisons after accounting for price changes. Current-US-dollar values are nominal and can change with inflation and exchange rates; they should not be interpreted as real income growth.

## Dashboard features
- Country groups matching the companion GDP growth dashboard concept
- Year and indicator selectors
- Annual time-series chart
- Real GDP-per-capita CAGR for 5, 10, 15, 20, 25 and 30 years
- Country-group comparison and selected-year nominal GDP-per-capita top 10 (plus Korea when outside the top 10)
- CSV export and browser print / Save as PDF
- Scheduled data refresh from the World Bank API

## Publish on GitHub Pages
1. Open **Settings → Pages**.
2. Under **Build and deployment**, choose **Deploy from a branch**.
3. Select branch `main` and folder `/(root)`, then save.
4. Wait for the Pages deployment to finish. The site URL should be `https://jinawinwin.github.io/WB_GDPperCapita/`.

## Data updates
GitHub Actions downloads data from the public World Bank API (no API key required) on the 15th of January, March, May, July, September and November at **00:00 UTC (09:00 Korea time)**. You can also run the workflow manually from **Actions → Update World Bank GDP per Capita data → Run workflow**.

The workflow writes `data/gdp_per_capita.json` and `data/gdp_per_capita.csv`. GitHub Actions must have repository write permissions enabled (Settings → Actions → General → Workflow permissions → Read and write permissions).

## Local run
Open `index.html` in a browser. If the cached JSON has not been generated yet, the dashboard tries to query the World Bank API directly. For a reliable published dashboard, run the update workflow once so that the JSON data file is committed.

## Caveats
- World Bank time series may be revised; the dashboard reflects the latest available WDI values.
- Recent years can be missing or provisional.
- The nominal top-10 ranking uses current US dollars and is affected by exchange rates.
- CAGR is shown only when both endpoints are positive and the selected start and end years exist in the data.
