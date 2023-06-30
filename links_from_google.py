import time
from collections import defaultdict
from urllib.parse import quote, unquote
from httpx import Client
from bs4 import BeautifulSoup
import json
import re


QUERY = "site:youtube.com openinapp.co"

client = Client(
    headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9,lt;q=0.8,et;q=0.7,de;q=0.6",
    },
    http2=True,  # use HTTP/2
)


def validate_yt_link(link):
    link = link.lower()
    valid_urls = [
        ("www.youtube.com"),
        ("youtu.be"),
        ("m.youtube.com"),
        ("music.youtube.com"),
        ("youtube.com"),
    ]

    return any([link.startswith(url) for url in valid_urls])


def parse_response(response):
    soup = BeautifulSoup(response.text, "html.parser")
    links = soup.find_all("a")
    # for link in links:
    #     print(link)
    links = [link for link in links if link.get("href") is not None]
    links = [link.get("href").split("https://")[-1].split("&")[0] for link in links]
    yt_links = [fix_url_encoding(link) for link in links if validate_yt_link(link)]
    return yt_links


def fix_url_encoding(url):
    # replace all url encoded characters with their actual characters
    return f"https://{unquote(url)}"


def main_scraper():
    yt_links = []
    page = 0
    while True:
        # scrapes until there are no more results
        page += 1
        print(f"scraping page {page}")
        url = f"https://www.google.com/search?hl=en&q={quote(QUERY)}" + (
            f"&start={10*(page-1)}" if page > 1 else ""
        )
        try:
            response = client.get(url)
            scraped_links = parse_response(response)
            print(f"scraped {len(scraped_links)} links")
            print(f"scraped {len(set(scraped_links))} unique links")
            print(scraped_links)
            yt_links.extend(list(set(scraped_links)))
            time.sleep(3)
        except Exception as e:
            print(e)
            if e == "timed out":
                print("sleeping for 30 seconds")
                time.sleep(30)
                response = client.get(url)
                scraped_links = parse_response(response)
                print(f"scraped {len(scraped_links)} links")
                print(f"scraped {len(set(scraped_links))} unique links")
                print(scraped_links)
                yt_links.extend(list(set(scraped_links)))
                time.sleep(3)
        if len(scraped_links) == 0:
            print("no more results")
            print(
                f"=========================== Halting at page {page} ==========================="
            )
            print(
                f"=========================== {len(yt_links)} links found ==========================="
            )
            with open("test.html", "w") as f:
                f.write(response.text)
            break

    return yt_links


if __name__ == "__main__":
    yt_links = main_scraper()

    print(f"scraped {len(yt_links)} links")

    print(f"scraped {len(set(yt_links))} unique links")

    yt_links = list(set(yt_links))

    print("saving links to yt_links.json")
    with open("yt_links.json", "w") as f:
        json.dump(yt_links, f, indent=4)
