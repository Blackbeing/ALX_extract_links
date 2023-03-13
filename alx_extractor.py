#!/usr/bin/python3
"""
This script extract links from alx dashboard page (projects)
and outputs them in an md file 
"""
import json
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

with open("config.json") as config_file:
    config = json.load(config_file)

output_file = config["output_file"]
cookies = config["cookies"]
headers = config["headers"]


base_url = "https://intranet.alxswe.com"
start_url = f"{base_url}/projects/current"

session = requests.Session()
session.cookies.update(cookies)
response = session.get(start_url, headers=headers)

soup = BeautifulSoup(response.content, "html.parser")

# expand all collapsed <a> tags
for link in soup.select("div.article a.collapsed"):
    link["class"].remove("collapsed")

# Find all links on the page that start with /projects/
links = [
    (link.text.strip(), link.get("href"))
    for link in soup.select("a[href^='/projects/']")
]

with open(f"{output_file}", "a") as f:
    for name, link in links:
        md_string = ""

        abs_link = urljoin(base_url, link)

        response = session.get(abs_link, headers=headers)

        soup = BeautifulSoup(response.content, "html.parser")

        title = soup.find("title")

        md_string += f"\n#### [{title.text}]({abs_link})\n"

        ul_tags = soup.find_all("ul")

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

                            md_string += (
                                f"  {sub_idx}. [{link.text}]({abs_link})\n"
                            )

                    except Exception as e:
                        print(e)

        f.write(md_string)
