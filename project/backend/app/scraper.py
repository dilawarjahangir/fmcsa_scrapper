import requests
from bs4 import BeautifulSoup

def get_carrier_info(mc_number: str) -> dict:
    url = "https://safer.fmcsa.dot.gov/query.asp"
    payload = {
        "searchtype": "ANY",
        "query_type": "queryCarrierSnapshot",
        "query_param": "MC_MX",
        "query_string": mc_number,
    }
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-US,en;q=0.9",
        "Cache-Control": "max-age=0",
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://safer.fmcsa.dot.gov",
        "Priority": "u=0, i",
        "Referer": "https://safer.fmcsa.dot.gov/",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
    }
    
    response = requests.post(url, data=payload, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Error from FMCSA: status code {response.status_code}")
    
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Locate the data table – adjust the selector if necessary.
    table = soup.find('table', summary="For formatting purpose")
    if not table:
        raise Exception("Data table not found in the HTML response.")
    
    # Extract the data from the table
    data = {}
    current_section = "General"
    for row in table.find_all('tr'):
        cells = row.find_all(['th', 'td'])
        cell_texts = [cell.get_text(" ", strip=True) for cell in cells]
        
        # If the row looks like a section header (one cell with a known class)
        if len(cells) == 1 and cells[0].has_attr("class") and "querylabelbkg" in cells[0]["class"]:
            current_section = cell_texts[0]
            data[current_section] = {}
            continue
        
        # For rows with an even number of cells, treat them as key/value pairs.
        if len(cells) % 2 == 0 and len(cells) > 0:
            for i in range(0, len(cells), 2):
                key = cell_texts[i]
                value = cell_texts[i+1] if (i+1) < len(cell_texts) else ""
                if current_section not in data:
                    data[current_section] = {}
                data[current_section][key] = value
        else:
            # Optionally log any rows that do not fit the pattern
            print("Unhandled row:", cell_texts)
    
    print(data)
    return data

