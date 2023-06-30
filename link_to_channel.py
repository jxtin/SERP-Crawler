import json
from httpx import Client
from tqdm import tqdm
import time
import re

client = Client(
    headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9,lt;q=0.8,et;q=0.7,de;q=0.6",
    },
    http2=True,
)


def classify_links(links):
    links_by_type = {}
    for link in links:
        type_url = link.split("/")[3]
        if type_url not in links_by_type:
            links_by_type[type_url] = []
        links_by_type[type_url].append(link)
    return links_by_type


def get_channel_link(link):
    if "watch" in link:
        response = client.get(link)
        link = re.findall(
            r'"ownerProfileUrl":"http://www.youtube.com/@[^"]*"', response.text
        )
        link = link[0].split('"ownerProfileUrl":"')[-1].split('"')[0].strip()
        return link
    elif "post" in link:
        response = client.get(link)
        return (
            re.findall(r'"ownerUrls":\["http://www.youtube.com/@[^"]*"', response.text)[
                0
            ]
            .replace("'", "")
            .replace('"', "")
            .split("[")[-1]
            .strip()
        )
    elif "/c" in link:
        return link.replace("/community", "").strip()
    elif "channel" in link:
        return link.strip()
    else:
        return None


def get_channel_links(links_by_type):
    links_with_channel = []
    unique_channels = set()

    for key in tqdm(links_by_type.keys()):
        for link in links_by_type[key]:
            print(link)
            time.sleep(1)
            try:
                channel_link = get_channel_link(link)
            except Exception as e:
                print(e)
                time.sleep(30)
                channel_link = get_channel_link(link)
            links_with_channel.append([link, channel_link, key])
            if channel_link in unique_channels:
                continue
            print(f"Found new channel: {channel_link}")
            unique_channels.add(channel_link)
            print(channel_link)
            time.sleep(3)

    return links_with_channel, unique_channels


if __name__ == "__main__":
    with open("yt_links.json", "r") as f:
        yt_links = json.load(f)

    links_by_type = classify_links(yt_links)

    links_with_channel, unique_channels = get_channel_links(links_by_type)
    with open("links_with_channel.json", "w") as f:
        json.dump(links_with_channel, f, indent=4)

    with open("unique_channels.json", "w") as f:
        json.dump(list(unique_channels), f, indent=4)
