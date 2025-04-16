import requests
from bs4 import BeautifulSoup

def get_carrier_info(mc_number: str) -> tuple[dict, str | None]:
    """
    Scrapes the FMCSA page for the given MC number.
    Returns a tuple with:
      - A dictionary containing all scraped data (organized by section).
      - The raw MCS-150 Form Date string if found (else None).

    This version iterates through every row looking for a cell that contains
    the text "MCS-150 Form Date" (or similar), and then reads the adjacent cell.
    """
    url = "https://safer.fmcsa.dot.gov/query.asp"
    payload = {
        "searchtype": "ANY",
        "query_type": "queryCarrierSnapshot",
        "query_param": "MC_MX",
        "query_string": mc_number,
    }
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,"
                  "image/avif,image/webp,image/apng,*/*;q=0.8,"
                  "application/signed-exchange;v=b3;q=0.7",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-US,en;q=0.9",
        "Cache-Control": "max-age=0",
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://safer.fmcsa.dot.gov",
        "Priority": "u=0, i",
        "Referer": "https://safer.fmcsa.dot.gov/",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/134.0.0.0 Safari/537.36"
    }

    response = requests.post(url, data=payload, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Error from FMCSA: status code {response.status_code}")

    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table', summary="For formatting purpose")
    if not table:
        raise Exception("Data table not found in the HTML response.")

    data = {}
    current_section = "General"
    data[current_section] = {}
    mcs150_date_str = None

    # Iterate through every row in the table.
    for row in table.find_all('tr'):
        cells = row.find_all(['th', 'td'])
        # If we have a single cell and it looks like a header, update our current section.
        if len(cells) == 1:
            # Check if the cell has class "querylabelbkg" (common for section headers).
            if cells[0].has_attr("class") and "querylabelbkg" in cells[0]["class"]:
                current_section = cells[0].get_text(strip=True)
                data[current_section] = {}
            continue

        # If row contains two or more cells, treat them as key-value pairs.
        if len(cells) >= 2:
            # Loop through cells in pairs.
            for i in range(0, len(cells) - 1, 2):
                key = cells[i].get_text(" ", strip=True)
                value = cells[i+1].get_text(" ", strip=True)
                data[current_section][key] = value

                # Look for the phrase "MCS-150 Form Date" (with or without a colon).
                if "MCS-150 Form Date" in key:
                    mcs150_date_str = value

    return data, mcs150_date_str
