#app/scrapper.py
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
    """
    url = "https://safer.fmcsa.dot.gov/query.asp"
    payload = {
        "searchtype": "ANY",
        "query_type": "queryCarrierSnapshot",
        "query_param": "MC_MX",
        "query_string": mc_number,
    }
    headers = {
        "Accept": ("text/html,application/xhtml+xml,application/xml;q=0.9,"
                   "image/avif,image/webp,image/apng,*/*;q=0.8,"
                   "application/signed-exchange;v=b3;q=0.7"),
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-US,en;q=0.9",
        "Cache-Control": "max-age=0",
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://safer.fmcsa.dot.gov",
        "Priority": "u=0, i",
        "Referer": "https://safer.fmcsa.dot.gov/",
        "User-Agent": ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                       "(KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"),
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

        # Section header (single TH/TD with CSS class)
        if len(cells) == 1 and cells[0].has_attr("class") and \
                "querylabelbkg" in cells[0]["class"]:
            current_section = cells[0].get_text(strip=True)
            data[current_section] = {}
            continue

        # Key/value pairs (walk in steps of 2)
        for i in range(0, len(cells) - 1, 2):
            key = cells[i].get_text(" ", strip=True)
            val = cells[i + 1].get_text(" ", strip=True)
            data[current_section][key] = val

            if "MCS-150 Form Date" in key:
                mcs150_raw = val

    return data, mcs150_raw
