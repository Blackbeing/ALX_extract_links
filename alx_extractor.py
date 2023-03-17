#!/usr/bin/python3
"""
This script extract links from alx dashboard page (projects)
and outputs them in an md file 
"""
import json
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

with open("config.json") as config_file:
    config = json.load(config_file)

output_file = config["output_file"]
cookies = config["cookies"]
headers = config["headers"]

if any([not output_file, "" in cookies.values(), "" in headers.values()]):
    print("You must specify an output file, cookies and headers")
    exit(1)

def is_connected_to_internet():
    try:
        requests.get("https://www.google.com")
        return True
    except requests.ConnectionError:
        return False

if is_connected_to_internet():
    print("You are connected to the internet")
    print("Extracting links ...\n\n")
else:
    print("You are not connected to the internet")
    exit(1)

base_url = "https://intranet.alxswe.com"
start_url = f"{base_url}/projects/current"

session = requests.Session()
session.cookies.update(cookies)
response = session.get(start_url, headers=headers, stream=False)

soup = BeautifulSoup(response.content, "html.parser")

# expand all collapsed <a> tags
for link in soup.select("div.article a.collapsed"):
    link["class"].remove("collapsed")

# Find all links on the page that start with /projects/
links = [
    (link.text.strip(), link.get("href"))
    for link in soup.select("a[href^='/projects/']")
]

if not Path(output_file).exists():
    Path(output_file).touch()

with open(f"{output_file}", "a") as f:
    for name, link in links:
        if not link.endswith("/current"):
            md_string = ""

            abs_link = urljoin(base_url, link)

            response = session.get(abs_link, headers=headers, stream=False)

            soup = BeautifulSoup(response.content, "html.parser")

            title = soup.find("title")

            md_string += f"\n<details>\n  <summary>{title.text}</summary>\n"
            md_string += f"\n  - [{title.text}]({abs_link})\n"

            ul_tags = soup.find_all("ul")

            link_number = 0
            for ul in ul_tags:
                links = ul.find_all("a")

                if links:
                    for sub_idx, link in enumerate(links, start=1):
                        try:
                            link_url = link.get("href")

                            if link_url is not None and link_url.startswith(
                                "/rltoken/"
                            ):
                                abs_link = urljoin(base_url, link_url)
                                response2 = session.get(abs_link, headers=headers, stream=False)
                                final_url = response2.url

                                md_string += (
                                    f"  {sub_idx}. [{link.text}]({final_url})\n"
                                )
                                link_number += 1

                        except Exception as e:
                            print(e)
            md_string += "\n</details>" 
            print(f"{title.text} found {link_number} links")

            f.write(md_string)
            f.flush()
