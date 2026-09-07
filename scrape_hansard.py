import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE = "https://www.parliament.tas.gov.au"

CALENDAR_URL = (
    "https://www.parliament.tas.gov.au/"
    "house-of-assembly/chamber-proceedings/"
    "sitting-calendar-2026"
)

print("Loading calendar...")

response = requests.get(CALENDAR_URL, timeout=30)
response.raise_for_status()

html = response.text

print("\n" + "=" * 80)
print("FIRST 5000 CHARACTERS OF HTML")
print("=" * 80)
print(html[:5000])

print("\n" + "=" * 80)
print("SEARCHING FOR PROCEEDINGS LINKS")
print("=" * 80)

soup = BeautifulSoup(html, "html.parser")

found_links = []

for a in soup.find_all("a", href=True):
    href = a["href"]

    if "/house-of-assembly/chamber-proceedings/proceedings/" in href:
        full_url = urljoin(BASE, href)
        found_links.append(full_url)

if found_links:
    print(f"\nFound {len(found_links)} proceedings links:\n")

    for link in sorted(set(found_links)):
        print(link)
else:
    print("\nNO PROCEEDINGS LINKS FOUND")

print("\n" + "=" * 80)
print("ALL LINKS ON PAGE")
print("=" * 80)

for a in soup.find_all("a", href=True):
    href = a["href"]
    text = a.get_text(" ", strip=True)

    print(f"TEXT: {text}")
    print(f"HREF: {href}")
    print("-" * 40)

print("\nFinished.")
``
