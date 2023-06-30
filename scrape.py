import links_from_google
import link_to_channel
import time
import json


def main():
    yt_links = links_from_google.main_scraper()

    print(f"scraped {len(yt_links)} links")

    print(f"scraped {len(set(yt_links))} unique links")

    yt_links = list(set(yt_links))

    print("saving links to yt_links.json")
    with open("yt_links.json", "w") as f:
        json.dump(yt_links, f, indent=4)

    print("Now will get channel names")

    with open("yt_links.json", "r") as f:
        yt_links = json.load(f)

    links_by_type = link_to_channel.classify_links(yt_links)

    links_with_channel, unique_channels = link_to_channel.get_channel_links(
        links_by_type
    )

    with open("links_with_channel.json", "w") as f:
        json.dump(links_with_channel, f, indent=4)

    with open("unique_channels.json", "w") as f:
        json.dump(list(unique_channels), f, indent=4)

    print("Done")

    print(f"Crawled {len(links_with_channel)} links")
    print(f"Found {len(unique_channels)} unique channels")


if __name__ == "__main__":
    main()
