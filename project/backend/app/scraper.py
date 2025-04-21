# app/scraper.py

import requests
from bs4 import BeautifulSoup
from typing import Tuple, Dict, Optional


def get_carrier_info(mc_number: str) -> Tuple[Dict, Optional[str]]:
    """
    Scrape FMCSA 'Company Snapshot' for a given MC number.

    Returns
    -------
    tuple
        (data_dict, raw_mcs150_date | None)

    Raises
    ------
    Exception if no table is found or if the row isn't an active carrier.
    """
    url = "https://safer.fmcsa.dot.gov/query.asp"
    payload = {
        "searchtype": "ANY",
        "query_type": "queryCarrierSnapshot",
        "query_param": "MC_MX",
        "query_string": mc_number,
    }
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://safer.fmcsa.dot.gov",
        "Referer": "https://safer.fmcsa.dot.gov/",
        "User-Agent": "Mozilla/5.0",
    }

    resp = requests.post(url, data=payload, headers=headers, timeout=25)
    if resp.status_code != 200:
        raise Exception(f"FMCSA returned HTTP {resp.status_code}")

    soup = BeautifulSoup(resp.text, "html.parser")
    table = soup.find("table", summary="For formatting purpose")
    if table is None:
        raise Exception("Could not find snapshot table in HTML.")

    data: Dict[str, Dict[str, str]] = {}
    current_section = "General"
    data[current_section] = {}
    mcs150_raw: Optional[str] = None

    for row in table.find_all("tr"):
        cells = row.find_all(["th", "td"])
        # Section header
        if len(cells) == 1 and cells[0].has_attr("class") and "querylabelbkg" in cells[0]["class"]:
            current_section = cells[0].get_text(strip=True)
            data[current_section] = {}
            continue
        # Key/value pairs
        for i in range(0, len(cells) - 1, 2):
            key = cells[i].get_text(" ", strip=True)
            val = cells[i + 1].get_text(" ", strip=True)
            data[current_section][key] = val
            if "MCS-150 Form Date" in key:
                mcs150_raw = val

    # ── only keep active carriers ──
    info = data.get("USDOT INFORMATION", {})
    entity = info.get("Entity Type:", "").lower()
    status = info.get("USDOT Status:", "").lower()

    if "carrier" not in entity or "active" not in status:
        raise Exception(
            f"Skipping MC {mc_number}: "
            f"Entity='{info.get('Entity Type:', '')}', "
            f"Status='{info.get('USDOT Status:', '')}'"
        )

    return data, mcs150_raw
