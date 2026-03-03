import httpx
from bs4 import BeautifulSoup
import traceback
from urllib.parse import urlparse
from readability import Document
import re
import warnings

import Settings

warnings.filterwarnings("ignore", category=Warning)

skip_codes = [300, 303, 305, 306, 307, 308, 400, 401, 402, 403, 404, 405,
            406, 407, 408, 409, 410, 411, 412, 413, 414, 415, 416, 417,
            418, 421, 422, 423, 424, 425, 426, 428, 429, 431, 451, 500,
            501, 502, 503, 504, 505, 506, 507, 508, 510, 511]
sentenceEndings = r"[.!?]\s+"
bannedURLs = ["youtube"]
usedURLs = []
idToURL = {}
previousInfo = {}
# {
#   "ID": int
#   "CHUNK": str
# }

chunkID = 0

# NOTE: Add Preferred Search Engine Setting
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
searchURLs = [
    ("DuckDuckGo", "https://html.duckduckgo.com/html/?q=", ".result__url"),
    ("Brave", "https://search.brave.com/search?q=", ".snippet a"),
    ("Startpage", "https://www.startpage.com/do/search?language=english&cat=web&q=", "h3.clk a"),
    ("Qwant", "https://www.qwant.com/?q=", "[data-testid=webResult] a"),
    ("Bing", "https://www.bing.com/search?q=", "li.b_algo h2 a"),
    # ("Searx", "https://priv.au/search?q=", "&format=json"), # Needs new Instance to stop '429 Too Many Requests' Error
]

def search(query):
    urls = []
    try:
        for name, baseURL, selector in searchURLs:
            if name != "Searx":
                response = httpx.get(baseURL + query, headers=headers)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, "html.parser")
                urls = [a["href"] for a in soup.select(selector)] # pass all URLS | Sort and Filter in cleanup()
                if urls:
                    break
            else:
                response = httpx.get(baseURL + query + selector, headers=headers)
                response.raise_for_status()
                results = response.json().get("results", [])
                urls = [r.get("url") for r in results]  # pass all URLS | Sort and Filter in cleanup()
                if urls:
                    break
        if urls:
            return cleanup(urls)
    except Exception as _e:  # Broader catch for debugging
        print("Search Request Failed")
        # traceback.print_exc()
    return None

def cleanup(urls):
    global previousInfo, usedURLs, chunkID, bannedURLs, idToURL
    content = []
    urlCount = 0
    urlMAX = 2 if Settings.ctxSize <= 8192 else 5
    for url in urls:
        if (urlCount >= urlMAX):
            break
        if (url in usedURLs):
            continue
        banned = False
        for i in bannedURLs:
            if (str(i) in url.lower()):
                banned = True
                break
        for i in Settings.userBlacklist:
            if (str(i) in url.lower()):
                # print(f"BANNING: {str(i)}")
                banned = True
                break
        if (banned):
            continue
        if (urlparse(url).scheme not in ("http", "https")) or (not urlparse(url).netloc):
            continue
        try:
            page = httpx.get(url, headers=headers)
            # Block Redirects and Trackers
            if (page.status_code in skip_codes):
                continue
            page.raise_for_status()
            html = page.text
            doc = Document(html)
            cleanHTML = doc.summary()
            soup = BeautifulSoup(cleanHTML, "lxml")
            sections = []
            for paragraph in soup.find_all(['p', 'table']):
                if paragraph.name == 'table':
                    # Handle table rows
                    tableText = ""
                    for row in paragraph.find_all('tr'):
                        rowText = row.get_text(strip=False)
                        tableText += re.sub(r"\n+", ' ', rowText) + "\n"
                    sections.append(tableText.strip())
                else:
                    # Handle regular paragraphs
                    sections.append(paragraph.get_text(strip=False))

            processed_data = []
            for section in sections:
                if len(section.split()) >= 350:
                    # Split long paragraphs into smaller chunks
                    for miniChunk in split_into_sentences(section):
                        processed_data.append(miniChunk)
                else:
                    # Short sections can be added as-is
                    processed_data.append(section)

            for chunk in processed_data:
                if (chunk.strip() != ""):
                    content.append({"ID": chunkID, "CHUNK": chunk})
                    previousInfo[chunkID] = chunk
                    usedURLs.append(url)
                    idToURL[chunkID] = url
                    chunkID += 1
            urlCount += 1
        except Exception as e:
            print(f"Cleanup failed for {url}: {e}")
            traceback.print_exc()
            continue
    # print("CONTENT: ", type(content))
    return content if content else None


def split_into_sentences(text: str):
    newlineSplit = re.split("\n+", text)
    sentences = []
    for i in newlineSplit:
        sentences += re.split(sentenceEndings, i)
        # sentences.append()
    # sentences = re.split(sentenceEndings, newlineSplit)
    result = []
    sentID = 0
    newChunk = ""
    prevChunk = ""
    for sentence in sentences:
        sentID += 1
        # print(f"{sentID}: {sentence}")
        newChunk += sentence + " "
        if (len(newChunk.split(" ")) >= 200) and (len(newChunk.split(" ")) <= 300):
            result.append(newChunk)
            newChunk = ""
            prevChunk = ""
        elif (len(newChunk.split(" ")) > 300):
            result.append(prevChunk)
            newChunk = sentence
            prevChunk = ""
        else:
            prevChunk += sentence

    if (newChunk != ""):
        result.append(newChunk)
        newChunk = ""

    return result
