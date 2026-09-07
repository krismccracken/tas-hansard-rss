import json
import re
from datetime import datetime
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

calendar_html = session.get(CALENDAR_URL, timeout=30).text
calendar_soup = BeautifulSoup(calendar_html, "html.parser")

# Find proceedings links
proceedings_links = set()

for a in calendar_soup.find_all("a", href=True):
    href = a["href"]

    if "/house-of-assembly/chamber-proceedings/proceedings/" in href:
        proceedings_links.add(urljoin(BASE, href))

records = []

for page_url in sorted(proceedings_links):
    try:
        html = session.get(page_url, timeout=30).text

        pdfs = re.findall(
            r"https://www\.parliament\.tas\.gov\.au/__data/assets/pdf_file/[^\"]+\.pdf",
            html,
        )

        hansard_pdf = next(
            (
                pdf
                for pdf in pdfs
                if "Full-Text" in pdf or "Hansard" in pdf
            ),
            None,
        )

        if not hansard_pdf:
            continue

        soup = BeautifulSoup(html, "html.parser")

        title = soup.find("h1").get_text(strip=True)

        records.append(
            {
                "title": title,
                "page_url": page_url,
                "pdf_url": hansard_pdf,
            }
        )

    except Exception as e:
        print(f"Failed: {page_url} ({e})")

records.sort(key=lambda x: x["title"], reverse=True)

with open("data.json", "w") as f:
    json.dump(records, f, indent=2)

fg = FeedGenerator()

fg.title("Tasmanian House of Assembly Hansard")
fg.link(href=CALENDAR_URL)
fg.description("Automatic feed of Hansard publications")

for item in records:
    fe = fg.add_entry()
    fe.title(item["title"])
    fe.link(href=item["page_url"])
    fe.guid(item["page_url"])
    fe.enclosure(
        item["pdf_url"],
        0,
        "application/pdf",
    )

fg.rss_file("rss.xml")

print(f"Generated {len(records)} entries")
