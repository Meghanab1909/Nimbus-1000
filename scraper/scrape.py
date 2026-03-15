import os
import re
import requests
from bs4 import BeautifulSoup

URLS_FILE = "urls.txt"
RAW_DIR = "raw_output"
FINAL_DIR = "final_kb"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(FINAL_DIR, exist_ok=True)

def clean_text(text):
    text = re.sub(r"[ \t]+", " ", text)
    lines = [line.strip() for line in text.splitlines()]
    lines = [line for line in lines if line]
    text = "\n".join(lines)
    return text

def extract_text(html):
    soup = BeautifulSoup(html, "lxml")

    for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
        tag.decompose()

    article = soup.find("article")
    if article:
        return clean_text(article.get_text(separator="\n"))

    return clean_text(soup.get_text(separator="\n"))

def main():

    with open(URLS_FILE) as f:
        lines = f.readlines()

    for line in lines:

        topic, url = line.strip().split("|")

        try:
            res = requests.get(url, headers=HEADERS)
            text = extract_text(res.text)

            raw_path = os.path.join(RAW_DIR, topic + "_raw.txt")
            with open(raw_path, "w", encoding="utf-8") as f:
                f.write(text)

            final_text = f"""
Topic: {topic.replace('_',' ').title()}

Source:
{url}

{text[:800]}
"""

            final_path = os.path.join(FINAL_DIR, topic + ".txt")

            with open(final_path, "w", encoding="utf-8") as f:
                f.write(final_text)

            print("Saved:", topic)

        except Exception as e:
            print("Error:", topic, e)

if __name__ == "__main__":
    main()