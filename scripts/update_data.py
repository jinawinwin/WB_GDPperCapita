#!/usr/bin/env python3
"""Download World Bank GDP-per-capita indicators and write dashboard JSON/CSV."""
import csv
import json
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
INDICATORS = {
    "real": "NY.GDP.PCAP.KD",
    "growth": "NY.GDP.PCAP.KD.ZG",
    "nominal": "NY.GDP.PCAP.CD",
}
BASE = "https://api.worldbank.org/v2/country/all/indicator/{indicator}?format=json&per_page=20000&page={page}"


def get_json(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": "WB-GDP-per-capita-dashboard/1.0"})
    with urllib.request.urlopen(req, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_indicator(indicator: str):
    records, page, pages = [], 1, 1
    while page <= pages:
        url = BASE.format(indicator=indicator, page=page)
        for attempt in range(4):
            try:
                payload = get_json(url)
                break
            except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
                if attempt == 3:
                    raise
                time.sleep(2 ** attempt)
        if not isinstance(payload, list) or len(payload) < 2 or payload[1] is None:
            break
        meta = payload[0] or {}
        pages = int(meta.get("pages") or 1)
        records.extend(payload[1])
        page += 1
    return records


def main():
    countries = {}
    for key, indicator in INDICATORS.items():
        print(f"Fetching {indicator} ({key})…", flush=True)
        for row in fetch_indicator(indicator):
            code, year, value = row.get("countryiso3code"), row.get("date"), row.get("value")
            if not code or not year or value is None:
                continue
            country_info = row.get("country") or {}
            country_name = country_info.get("value") or code
            # World Bank aggregates have region id "NA"; retain countries and territories only.
            region = (row.get("country") or {}).get("region") or {}
            obj = countries.setdefault(code, {
                "code": code,
                "name": country_name,
                "region": region.get("id"),
                "values": {"real": {}, "growth": {}, "nominal": {}},
            })
            obj["values"][key][str(year)] = float(value)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    result = {
        "source": "World Bank World Development Indicators",
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "indicators": INDICATORS,
        "countries": countries,
    }
    json_path = DATA_DIR / "gdp_per_capita.json"
    json_path.write_text(json.dumps(result, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    csv_path = DATA_DIR / "gdp_per_capita.csv"
    with csv_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["iso3", "country", "region_id", "year", "real_gdp_per_capita_2015_usd", "real_gdp_per_capita_growth_pct", "nominal_gdp_per_capita_current_usd"])
        for code, c in sorted(countries.items(), key=lambda item: (item[1]["name"], item[0])):
            years = set()
            for series in c["values"].values():
                years.update(series)
            for year in sorted(years):
                writer.writerow([code, c["name"], c["region"] or "", year,
                    c["values"]["real"].get(year, ""),
                    c["values"]["growth"].get(year, ""),
                    c["values"]["nominal"].get(year, "")])
    print(f"Wrote {json_path} ({len(countries)} country/territory codes)")
    print(f"Wrote {csv_path}")


if __name__ == "__main__":
    main()
