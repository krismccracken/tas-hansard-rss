import json
import re
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator

BASE = "https://www.parliament.tas.gov.au"

CALENDAR_URL = (
    "https://www.parliament.tas.gov.au/"
    "house-of-assembly/chamber-proceedings/"
    "sitting-calendar-2026"
)

session = requests.Session()

print("Loading calendar...")

html = session.get(CALENDAR_URL, timeout=30).text
soup = BeautifulSoup(html, "html.parser")

links = set()

for a in soup.find_all("a", href=True):
    href = a["href"]

    if "/house-of-assembly/chamber-proceedings/proceedings/" in href:
        links.add(urljoin(BASE, href))

print(f"Found {len(links)} proceedings pages")

records = []

for page_url in sorted(links):
    try:
        page_html = session.get(page_url, timeout=30).text

        pdfs = re.findall(
            r'https://www\.parliament\.tas\.gov\.au/__data/assets/pdf_file/[^"]+\.pdf',
            page_html,
        )

        if not pdfs:
            continue

        soup = BeautifulSoup(page_html, "html.parser")

        title = soup.find("h1").get_text(strip=True)

        records.append(
            {
                "title": title,
                "page": page_url,
                "pdf": pdfs[0],
            }
        )

    except Exception as e:
        print(f"Error: {page_url}")
        print(e)

records.reverse()

print(f"Collected {len(records)} Hansard documents")

with open("data.json", "w") as f:
    json.dump(records, f, indent=2)

fg = FeedGenerator()

fg.title("Tasmanian House of Assembly Hansard")
fg.description("Automatically generated Hansard feed")
fg.link(href=CALENDAR_URL)

for item in records:

    fe = fg.add_entry()

    fe.title(item["title"])
    fe.guid(item["page"])
    fe.link(href=item["page"])

    fe.enclosure(
        item["pdf"],
        0,
        "application/pdf",
    )

fg.rss_file("rss.xml")

print("RSS created")
